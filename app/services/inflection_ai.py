import httpx
import logging
import json
import random
from typing import List, Dict, Any

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.report import ReportCreate
from app.schemas.analysis import AIResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InflectionAIService:
    def __init__(self):
        self.api_key = settings.INFLECTION_AI_API_KEY
        self.api_url = f"{settings.INFLECTION_AI_BASE_URL}/v1/chat/completions"
        self.model = settings.INFLECTION_AI_MODEL

    async def _call_ai_api(self, messages: List[Dict[str, Any]], temperature: float) -> str:
        if not self.api_key:
            raise ValueError("Inflection AI API key is not set.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": temperature,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=90.0)
                response.raise_for_status()
                ai_response = response.json()
                return ai_response['choices'][0]['message']['content']
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred during AI call: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"An error occurred during AI call: {e}", exc_info=True)
                raise

    def _get_data_sample(self, data: List[Dict[str, Any]], sample_size: int = 20) -> str:
        """Takes a random sample of the data to keep the prompt concise."""
        if len(data) <= sample_size:
            sample = data
        else:
            sample = random.sample(data, sample_size)
        return "\n".join([str(d) for d in sample])

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

        climate_data_str = self._get_data_sample(climate_data)
        wildlife_data_str = self._get_data_sample(wildlife_data)

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
        natural_language_content = await self._call_ai_api(messages_analysis, temperature=0.4)
        logger.info("Received natural language analysis from AI.")

        # --- Step 2: Get structured JSON from AI based on natural language content ---
        system_prompt_json_extraction = (
            f"""You are a data extraction assistant. Your task is to parse the provided natural language report and extract specific information into a valid JSON object that conforms to the following Pydantic schema:

```json
{AIResponse.model_json_schema()}
```

Ensure the output is ONLY the JSON object, nothing else."""
        )

        user_prompt_json_extraction = f"Natural Language Report:\n{natural_language_content}\n\nExtract the information into a JSON object."

        messages_json_extraction = [
            {"role": "system", "content": system_prompt_json_extraction},
            {"role": "user", "content": user_prompt_json_extraction}
        ]

        logger.info("Making second AI call for JSON extraction.")
        json_content_str = await self._call_ai_api(messages_json_extraction, temperature=0.1)
        logger.info("Received JSON extraction from AI.")

        # --- Step 3: Parse and validate JSON using the Pydantic model ---
        try:
            # Clean the response to ensure it is valid JSON
            cleaned_json_str = json_content_str.strip().replace('\n', '').replace('```json', '').replace('```', '')
            ai_response = AIResponse.model_validate_json(cleaned_json_str)
        except (ValidationError, json.JSONDecodeError) as e:
            logger.error(f"Failed to validate AI's JSON response: {e}. Raw response: {json_content_str}", exc_info=True)
            ai_response = AIResponse() # Use a default empty response
            # Store the raw text in analysis_results for debugging
            analysis_results = {"raw_text": natural_language_content, "parsing_error": str(e)}
        else:
            analysis_results = {"raw_text": natural_language_content}

        report = ReportCreate(
            report_type=query,
            query_parameters=json.dumps({"query": query}),
            analysis_results=json.dumps(analysis_results),
            predictions=json.dumps(ai_response.predictions),
            citations=json.dumps(ai_response.citations),
            confidence_scores=json.dumps({"overall": ai_response.confidence_score}),
            ai_model_version=self.model
        )
        logger.info("AI analysis process completed successfully.")
        return report
