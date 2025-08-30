from pydantic import BaseModel, Field, Json
from typing import Any, Literal, List, Dict

class AnalysisRequest(BaseModel):
    query: str
    target_type: Literal["ecosystem", "species"] # What kind of analysis target
    target_id: int | None = None # ID of the ecosystem or species
    target_name: str | None = None # Name of the ecosystem or species (for convenience)

class AIResponse(BaseModel):
    """Defines and validates the expected JSON structure from the AI's extraction step."""
    summary: str = ""
    key_insights: List[str] = []
    predictions: Dict[str, Any] = {}
    citations: Dict[str, Any] = {}
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)

class AnalysisResult(BaseModel):
    """The final response model after a successful analysis."""
    report_id: int
    message: str = "Analysis complete and report generated."

    class Config:
        orm_mode = True
