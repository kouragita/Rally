from pydantic import BaseModel, ConfigDict # Import ConfigDict from pydantic
from datetime import datetime
from typing import Any, Optional, Dict # Import Dict

class ReportBase(BaseModel):
    report_type: str | None = None
    query_parameters: Dict[str, Any] | None = None # Changed from Json[Any]
    analysis_results: Dict[str, Any] | None = None # Changed from Json[Any]
    predictions: Dict[str, Any] | None = None # Changed from Json[Any]
    citations: Dict[str, Any] | None = None # Changed from Json[Any]
    confidence_scores: Dict[str, Any] | None = None # Changed from Json[Any]
    ai_model_version: str | None = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    report_type: Optional[str] = None
    query_parameters: Optional[Dict[str, Any]] = None # Changed from Json[Any]
    analysis_results: Optional[Dict[str, Any]] = None # Changed from Json[Any]
    predictions: Optional[Dict[str, Any]] = None # Changed from Json[Any]
    citations: Optional[Dict[str, Any]] = None # Changed from Json[Any]
    confidence_scores: Optional[Dict[str, Any]] = None # Changed from Json[Any]
    ai_model_version: Optional[str] = None

class Report(ReportBase):
    id: int
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True) # Use model_config instead of Config
