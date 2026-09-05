from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.core.database import Base

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    contract_type = Column(String, default="Commercial Contract")
    selected_role = Column(String, default="Service Provider")
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
