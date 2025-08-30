import httpx
import logging
import json # Import the json module
from typing import List, Dict, Any

from app.core.config import settings
from app.schemas.report import ReportCreate

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InflectionAIService:
    """A service for interacting with the Inflection AI API."""

    def __init__(self):
        self.api_key = settings.INFLECTION_AI_API_KEY
        self.api_url = f"{settings.INFLECTION_AI_BASE_URL}/v1/chat/completions"

    async def analyze(
        self,
        query: str,
        climate_data: List[Dict[str, Any]],
        wildlife_data: List[Dict[str, Any]]
    ) -> ReportCreate:
        """
        Performs analysis by sending data and a query to the Inflection AI API.

        Args:
            query: The user's natural language query for the analysis.
            climate_data: A list of dictionaries representing climate data points.
            wildlife_data: A list of dictionaries representing wildlife data points.

        Returns:
            A Pydantic schema containing the structured report from the AI.
        """
        if not self.api_key:
            logger.error("Inflection AI API key is not set.")
            raise ValueError("Inflection AI API key is not set.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # --- Prompt Engineering ---
        system_prompt = (
            "You are a senior climate scientist and wildlife biologist. Your task is to analyze the provided data "
            "to answer the user's query. Provide a detailed, evidence-based report. The report must include: "
            "1. A concise summary of your findings. "
            "2. A list of key insights and patterns. "
            "3. A predictive analysis of future trends. "
            "4. A set of actionable recommendations. "
            "5. A confidence score (0.0 to 1.0) for your overall analysis."
        )

        climate_data_str = "\n".join([str(d) for d in climate_data[:5]])
        wildlife_data_str = "\n".join([str(d) for d in wildlife_data[:5]])

        user_prompt = (
            f"User Query: {query}\n\n"
            f"Supporting Climate Data (sample):\n{climate_data_str}\n\n"
            f"Supporting Wildlife Data (sample):\n{wildlife_data_str}\n\n"
            f"Please generate the full report based on this query and data."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": "Pi-3.1",
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.4,
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.info("Sending request to Inflection AI...")
                response = await client.post(self.api_url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                ai_response = response.json()
                logger.info("Successfully received response from Inflection AI.")

                content = ai_response['choices'][0]['message']['content']

                report = ReportCreate(
                    report_type=query,
                    query_parameters=json.dumps({"query": query}), # Convert dict to JSON string
                    analysis_results=json.dumps({"raw_text": content}), # Convert dict to JSON string
                    predictions=json.dumps({}), # Convert dict to JSON string
                    citations=json.dumps({}), # Convert dict to JSON string
                    confidence_scores=json.dumps({}), # Convert dict to JSON string
                    ai_model_version=ai_response.get('model')
                )
                return report

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"An error occurred while calling the AI service: {e}", exc_info=True)
                raise
