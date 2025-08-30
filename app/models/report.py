from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    query_parameters = Column(JSON)
    analysis_results = Column(JSON)
    predictions = Column(JSON)
    citations = Column(JSON)
    confidence_scores = Column(JSON)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    ai_model_version = Column(String)
