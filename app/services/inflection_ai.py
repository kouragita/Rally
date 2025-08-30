import httpx
import logging
import json
from typing import List, Dict, Any

from app.core.config import settings
from app.schemas.report import ReportCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InflectionAIService:
    def __init__(self):
        self.api_key = settings.INFLECTION_AI_API_KEY
        self.api_url = f"{settings.INFLECTION_AI_BASE_URL}/v1/chat/completions"

    async def _call_ai_api(self, messages: List[Dict[str, Any]], model: str = "Pi-3.1", max_tokens: int = 2048, temperature: float = 0.4) -> str:
        if not self.api_key:
            raise ValueError("Inflection AI API key is not set.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                ai_response = response.json()
                return ai_response['choices'][0]['message']['content']
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred during AI call: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"An error occurred during AI call: {e}", exc_info=True)
                raise

    async def analyze(
        self,
        query: str,
        climate_data: List[Dict[str, Any]],
        wildlife_data: List[Dict[str, Any]]
    ) -> ReportCreate:
        logger.info("Starting AI analysis process.")

        # --- Step 1: Get natural language analysis from AI ---
        system_prompt_analysis = (
            "You are a senior climate scientist and wildlife biologist. Your task is to analyze the provided data "
            "to answer the user's query. Provide a detailed, evidence-based report. The report must include: "
            "1. A concise summary of your findings. "
            "2. A list of key insights and patterns. "
            "3. A predictive analysis of future trends. "
            "4. A set of actionable recommendations. "
            "5. A confidence score (0.0 to 1.0) for your overall analysis. "
            "Do NOT output JSON in this response. Provide a natural language report."
        )

        climate_data_str = "\n".join([str(d) for d in climate_data[:5]]) # Sample first 5 for prompt
        wildlife_data_str = "\n".join([str(d) for d in wildlife_data[:5]]) # Sample first 5 for prompt

        user_prompt_analysis = (
            f"User Query: {query}\n\n"
            f"Supporting Climate Data (sample):\n{climate_data_str}\n\n"
            f"Supporting Wildlife Data (sample):\n{wildlife_data_str}\n\n"
            f"Please generate the full report based on this query and data."
        )

        messages_analysis = [
            {"role": "system", "content": system_prompt_analysis},
            {"role": "user", "content": user_prompt_analysis}
        ]

        logger.info("Making first AI call for natural language analysis.")
        natural_language_content = await self._call_ai_api(messages_analysis)
        logger.info("Received natural language analysis from AI.")

        # --- Step 2: Get structured JSON from AI based on natural language content ---
        system_prompt_json_extraction = (
            "You are a data extraction assistant. Your task is to parse the provided natural language report "
            "and extract specific information into a JSON object. "
            "The JSON object MUST have the following keys: "
            "\"summary\": string, "
            "\"key_insights\": list of strings, "
            "\"predictions\": dict, "
            "\"citations\": dict, "
            "\"confidence_score\": float (between 0.0 and 1.0). "
            "If a field cannot be extracted, use an empty string, empty list, empty dict, or 0.0 as appropriate. "
            "Ensure the output is ONLY the JSON object, nothing else."
        )

        user_prompt_json_extraction = f"Natural Language Report:\n{natural_language_content}\n\nExtract the information into a JSON object."

        messages_json_extraction = [
            {"role": "system", "content": system_prompt_json_extraction},
            {"role": "user", "content": user_prompt_json_extraction}
        ]

        logger.info("Making second AI call for JSON extraction.")
        json_content_str = await self._call_ai_api(messages_json_extraction, temperature=0.1) # Lower temp for strict JSON
        logger.info("Received JSON extraction from AI.")

        # --- Step 3: Parse JSON and create ReportCreate schema ---
        try:
            parsed_json = json.loads(json_content_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI's JSON response: {e}. Raw response: {json_content_str}", exc_info=True)
            # Fallback: if JSON parsing fails, use raw text and default empty values
            parsed_json = {
                "summary": "AI response could not be fully parsed.",
                "key_insights": [],
                "predictions": {},
                "citations": {},
                "confidence_score": 0.0,
            }
            # Store the raw text in analysis_results for debugging
            parsed_json["analysis_results"] = {"raw_text": natural_language_content, "parsing_error": str(e)}
        else:
            # If parsing successful, ensure all expected keys are present
            parsed_json.setdefault("summary", "")
            parsed_json.setdefault("key_insights", [])
            parsed_json.setdefault("predictions", {})
            parsed_json.setdefault("citations", {})
            parsed_json.setdefault("confidence_score", 0.0)
            # Store the original natural language content as well
            parsed_json["analysis_results"] = {"raw_text": natural_language_content}


        report = ReportCreate(
            report_type=query,
            query_parameters=json.dumps({"query": query}),
            analysis_results=json.dumps(parsed_json.get("analysis_results", {"raw_text": natural_language_content})),
            predictions=json.dumps(parsed_json.get("predictions", {})),
            citations=json.dumps(parsed_json.get("citations", {})),
            confidence_scores=json.dumps({"overall": parsed_json.get("confidence_score", 0.0)}),
            ai_model_version="Pi-3.1" # Assuming Pi-3.1 for both calls
        )
        logger.info("AI analysis process completed successfully.")
        return report