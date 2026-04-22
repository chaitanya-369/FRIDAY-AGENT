from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    llm_provider: str = "groq"
    llm_model: str = "llama3-70b-8192"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""

    environment: str = "development"
    port: int = 8000
    slack_bot_token: Optional[str] = None
    slack_channel_id: Optional[str] = "#general"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
