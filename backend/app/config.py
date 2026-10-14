"""
Application Configuration Module for CivicPulse AI.
Loads configuration from environment variables and .env file with sensible defaults.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
UPLOADS_DIR = BACKEND_DIR / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure upload directory exists
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "CivicPulse AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Smart Civic Issue Reporting and Resolution Platform"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'civicpulse.db'}"
)
    
    # Security
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    JWT_SECRET_KEY: str = "civicpulse-ai-secure-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # AI Vision API (Optional Google Gemini Key)
    GEMINI_API_KEY: str = ""
    
    # Demo Data
    SEED_DEMO_DATA: bool = True
    
    # File Uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    
    # Paths
    BASE_DIR: Path = BASE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    FRONTEND_DIR: Path = FRONTEND_DIR

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
