# brandguard/backend/app/core/config.py (Updated)
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """BrandGuard configuration using Pydantic Settings"""

    # Database and Core Settings
    DATABASE_URL: str = (
        "postgresql://brandguard:secure_password@localhost:5432/brandguard_db"
    )

    # Security Settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs (All documented in requirements.txt)
    NEWS_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None

    # Infrastructure (All from requirements.txt)
    REDIS_URL: str = "redis://localhost:6379/0"
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # Application Settings
    PROJECT_NAME: str = "BrandGuard"
    API_V1_STR: str = "/api/v1"

    # Compliance
    DATA_RETENTION_DAYS: int = 365

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from requirements


# Instantiate settings
settings = Settings()
