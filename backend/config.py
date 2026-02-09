"""Configuration management for LLMLab backend."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment."""

    # App
    APP_NAME: str = "LLMLab Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://your-supabase-url.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-anon-key")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    # API Keys for mock providers
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-key")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "mock-key")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "mock-key")
    
    class Config:
        env_file = ".env"


settings = Settings()
