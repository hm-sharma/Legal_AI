from app.core.database import SessionLocal
from app.services.legal_engine.attorney_evaluator import AttorneyEvaluatorService
from app.services.storage.minio_client import MinIOStorageService

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_evaluator_service() -> AttorneyEvaluatorService:
    return AttorneyEvaluatorService()

def get_storage_service() -> MinIOStorageService:
    return MinIOStorageService()
