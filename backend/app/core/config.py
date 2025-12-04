# brandguard/backend/app/core/config.py
from pydantic import BaseSettings, validator
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "brandguard"
    POSTGRES_PASSWORD: str = "secure_password"
    POSTGRES_DB: str = "brandguard_db"
    DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # External APIs (only public sources)
    NEWS_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    
    # Application
    PROJECT_NAME: str = "BrandGuard"
    API_V1_STR: str = "/api/v1"
    
    # Compliance
    DATA_RETENTION_DAYS: int = 365
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()