import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Legal Document Analyzer API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./legal_analyzer.db")
    
    # Celery & Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # MinIO / Object Storage
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "legal-documents")
    
    # Storage Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STORAGE_DIR: str = os.path.join(BASE_DIR, "storage")
    SAMPLES_DIR: str = os.path.join(STORAGE_DIR, "samples")
    UPLOADS_DIR: str = os.path.join(STORAGE_DIR, "uploads")
    
    class Config:
        case_sensitive = True

settings = Settings()

os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.SAMPLES_DIR, exist_ok=True)
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
