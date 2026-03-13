from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None

    # Model Defaults
    model_name: str = "gpt-4o"
    temperature: float = 0.1

    # Azure Configuration
    openai_api_version: str = "2024-05-01-preview"
    azure_openai_endpoint: Optional[str] = None

    # Local Model
    local_model: Optional[str] = None

    # Observability
    verbose: bool = False
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings():
    return Settings()
