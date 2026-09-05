import os
import shutil
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class MinIOStorageService:
    """
    MinIO Object Storage Service with automatic local disk fallback.
    """
    def __init__(self):
        self.minio_client = None
        self._init_minio()

    def _init_minio(self):
        try:
            from minio import Minio
            self.minio_client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False
            )
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info("MinIO storage client initialized.")
        except Exception as e:
            logger.warning(f"MinIO client initialization skipped, using local filesystem storage: {e}")
            self.minio_client = None

    def save_file(self, file_obj, destination_path: str, object_name: Optional[str] = None) -> str:
        # Save locally
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)

        # Upload to MinIO if available
        if self.minio_client and object_name:
            try:
                self.minio_client.fput_object(
                    settings.MINIO_BUCKET_NAME,
                    object_name,
                    destination_path
                )
            except Exception as e:
                logger.error(f"MinIO upload error: {e}")

        return destination_path
