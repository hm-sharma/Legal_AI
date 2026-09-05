from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
from app.sample_generator import generate_sample_contracts

# Create database tables if using SQLite / SQL engine
Base.metadata.create_all(bind=engine)

# Generate sample contracts on startup
generate_sample_contracts(settings.SAMPLES_DIR)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise dual-perspective contract risk scoring & PDF coordinate mapping engine.",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
