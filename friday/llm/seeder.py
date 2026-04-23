"""
friday/llm/seeder.py

Auto-seeds the DB with providers and API keys from .env on first startup.
This is idempotent — running it multiple times won't create duplicates.

Called from friday/core/database.py → create_db_and_tables().
"""

from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import APIKey, LLMProvider
from friday.llm.model_catalog import ModelCatalog

# Phase 1 provider definitions
PROVIDER_DEFAULTS = [
    {
        "name": "groq",
        "display_name": "Groq",
        "adapter_class": "GroqAdapter",
        "base_url": None,
        "priority": 1,
    },
    {
        "name": "anthropic",
        "display_name": "Anthropic Claude",
        "adapter_class": "AnthropicAdapter",
        "base_url": None,
        "priority": 2,
    },
    {
        "name": "gemini",
        "display_name": "Google Gemini",
        "adapter_class": "GeminiAdapter",
        "base_url": None,
        "priority": 3,
    },
    {
        "name": "openai",
        "display_name": "OpenAI",
        "adapter_class": "OpenAIAdapter",
        "base_url": None,
        "priority": 4,
    },
    {
        "name": "deepseek",
        "display_name": "DeepSeek",
        "adapter_class": "DeepSeekAdapter",
        "base_url": "https://api.deepseek.com",
        "priority": 5,
    },
]


def seed_providers_and_keys() -> None:
    """
    Seed LLM providers and .env API keys into the DB.
    Idempotent — skips records that already exist.
    """
    from friday.config.settings import settings

    # Map of provider_name → env key value
    env_keys: dict[str, str] = {
        "anthropic": settings.anthropic_api_key,
        "groq": settings.groq_api_key,
        "gemini": settings.gemini_api_key,
        "openai": settings.openai_api_key,
        "deepseek": settings.deepseek_api_key,
    }

    with Session(engine) as session:
        for pd in PROVIDER_DEFAULTS:
            # Upsert provider
            existing = session.exec(
                select(LLMProvider).where(LLMProvider.name == pd["name"])
            ).first()

            if not existing:
                provider = LLMProvider(**pd)
                session.add(provider)
                session.flush()  # get provider.id before commit
                provider_id = provider.id
            else:
                provider_id = existing.id

            # Seed .env key if present and not already seeded
            key_value = env_keys.get(pd["name"], "")
            if key_value and key_value not in ("", "your_anthropic_api_key_here"):
                existing_key = session.exec(
                    select(APIKey).where(
                        APIKey.provider_id == provider_id,
                        APIKey.label == f"{pd['name']}-env-default",
                    )
                ).first()
                if not existing_key:
                    session.add(
                        APIKey(
                            provider_id=provider_id,
                            label=f"{pd['name']}-env-default",
                            key_value=key_value,
                            priority=10,
                        )
                    )

        session.commit()

    # Sync model catalog after providers are in DB
    ModelCatalog().sync_to_db()
