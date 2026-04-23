"""
friday/config/settings.py

Pydantic Settings for FRIDAY-AGENT.

LLM provider/model/key configuration is now DB-backed (via friday/llm/).
Legacy single-key fields (anthropic_api_key etc.) are kept for backward
compatibility and are auto-seeded into the DB on first startup.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── LLM Routing ───────────────────────────────────────────────────────────
    default_provider: str = "groq"
    default_model: str = "llama-3.3-70b-versatile"
    key_rotation_strategy: str = (
        "round_robin"  # round_robin | least_used | priority | random
    )

    # ── Legacy single-key fields (used for DB auto-seed on first startup) ─────
    # These are read from .env and seeded into the api_keys table once.
    # After that, use the /api/keys endpoints to manage keys.
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""

    # ── Memory System ─────────────────────────────────────────────────────────
    chromadb_path: str = "data/vectors"  # path to ChromaDB persistent store
    memory_extraction_model: str = (
        "claude-haiku-4-5-20251001"  # cheap model for extraction
    )
    memory_context_token_budget: int = 1200  # max tokens to inject into system prompt
    memory_max_facts: int = 5  # max fact memories to inject per turn
    memory_max_preferences: int = 5  # max preference memories to inject
    memory_max_tasks: int = 5  # max active tasks to inject
    memory_decay_interval_hours: int = 24  # how often decay engine runs
    memory_enabled: bool = True  # master switch

    # ── Server ────────────────────────────────────────────────────────────────
    environment: str = "development"
    port: int = 8000

    # ── Slack ─────────────────────────────────────────────────────────────────
    slack_bot_token: Optional[str] = None
    slack_app_token: Optional[str] = None
    slack_channel_id: Optional[str] = "#general"

    # ── Observability (optional) ──────────────────────────────────────────────
    sentry_dsn: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: Optional[str] = "https://cloud.langfuse.com"
    infisical_token: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
