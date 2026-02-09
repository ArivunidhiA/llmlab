"""Configuration for LLMlab backend"""

from pydantic_settings import BaseSettings
from typing import Optional
import json


class Settings(BaseSettings):
    """Application settings loaded from environment"""
    
    # Core
    app_name: str = "LLMlab"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://user:password@localhost/llmlab"
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Provider Rates (JSON string or dict)
    # Format: {"openai": {"gpt-4": {"input": 0.03, "output": 0.06}}}
    provider_rates: str = json.dumps({
        "openai": {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "gpt-4o": {"input": 0.005, "output": 0.015},
        },
        "anthropic": {
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        },
        "google": {
            "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
        },
        "cohere": {
            "command": {"input": 0.0001, "output": 0.0003},
            "command-light": {"input": 0.00003, "output": 0.0001},
        },
    })
    
    # Webhooks
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


def get_provider_rates() -> dict:
    """Parse provider rates from JSON string"""
    if isinstance(settings.provider_rates, str):
        return json.loads(settings.provider_rates)
    return settings.provider_rates
