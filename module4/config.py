"""Configuration - stores API keys and database settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Load settings from .env file."""

    # API Keys
    groq_api_key: str = ""

    # Database
    database_url: str = "sqlite:///./rayeva.db"

    # Environment
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Get cached settings - only loads once."""
    return Settings()
