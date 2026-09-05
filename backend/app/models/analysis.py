from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    overall_score = Column(Integer, default=50)
    summary_of_findings = Column(Text, nullable=True)
    clauses_json = Column(JSON, nullable=True)
    total_spans_count = Column(Integer, default=0)
    high_risk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
