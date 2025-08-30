from pydantic import BaseModel, Json
from typing import Any, Literal

class AnalysisRequest(BaseModel):
    query: str
    target_type: Literal["ecosystem", "species"] # What kind of analysis target
    target_id: int | None = None # ID of the ecosystem or species
    target_name: str | None = None # Name of the ecosystem or species (for convenience)

class AnalysisResult(BaseModel):
    # This will essentially be the ReportCreate schema
    # For now, we can just use a generic dict or the Report schema directly
    pass
