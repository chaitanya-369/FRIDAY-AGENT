"""
friday/llm/model_catalog.py

Static + DB-backed catalog of models per provider.

On first startup, STATIC_CATALOG is seeded into the model_entries table.
Subsequent lookups hit the DB, allowing runtime additions/overrides.
"""

from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import LLMProvider, ModelEntry

# ---------------------------------------------------------------------------
# Static catalog — source of truth for known models at install time.
# Fields: model_id, display_name, context_window (tokens),
#         supports_tools, supports_vision, cost_input_per_1m (USD), cost_output_per_1m (USD)
# ---------------------------------------------------------------------------
STATIC_CATALOG: dict[str, list[dict]] = {
    "anthropic": [
        {
            "model_id": "claude-opus-4-5-20251101",
            "display_name": "Claude Opus 4.5",
            "ctx": 200000,
            "tools": True,
            "vision": True,
            "cin": 15.0,
            "cout": 75.0,
        },
        {
            "model_id": "claude-sonnet-4-5-20250514",
            "display_name": "Claude Sonnet 4.5",
            "ctx": 200000,
            "tools": True,
            "vision": True,
            "cin": 3.0,
            "cout": 15.0,
        },
        {
            "model_id": "claude-haiku-4-5-20251001",
            "display_name": "Claude Haiku 4.5",
            "ctx": 200000,
            "tools": True,
            "vision": True,
            "cin": 0.8,
            "cout": 4.0,
        },
    ],
    "groq": [
        {
            "model_id": "llama-3.3-70b-versatile",
            "display_name": "LLaMA 3.3 70B",
            "ctx": 128000,
            "tools": True,
            "vision": False,
            "cin": 0.59,
            "cout": 0.79,
        },
        {
            "model_id": "llama-3.1-8b-instant",
            "display_name": "LLaMA 3.1 8B",
            "ctx": 128000,
            "tools": True,
            "vision": False,
            "cin": 0.05,
            "cout": 0.08,
        },
        {
            "model_id": "mixtral-8x7b-32768",
            "display_name": "Mixtral 8x7B",
            "ctx": 32768,
            "tools": True,
            "vision": False,
            "cin": 0.24,
            "cout": 0.24,
        },
        {
            "model_id": "gemma2-9b-it",
            "display_name": "Gemma 2 9B",
            "ctx": 8192,
            "tools": False,
            "vision": False,
            "cin": 0.2,
            "cout": 0.2,
        },
        {
            "model_id": "llama-3.2-90b-vision-preview",
            "display_name": "LLaMA 3.2 90B Vision",
            "ctx": 128000,
            "tools": True,
            "vision": True,
            "cin": 0.9,
            "cout": 0.9,
        },
    ],
    "gemini": [
        {
            "model_id": "gemini-2.0-flash",
            "display_name": "Gemini 2.0 Flash",
            "ctx": 1048576,
            "tools": True,
            "vision": True,
            "cin": 0.1,
            "cout": 0.4,
        },
        {
            "model_id": "gemini-1.5-pro",
            "display_name": "Gemini 1.5 Pro",
            "ctx": 2097152,
            "tools": True,
            "vision": True,
            "cin": 1.25,
            "cout": 5.0,
        },
        {
            "model_id": "gemini-1.5-flash",
            "display_name": "Gemini 1.5 Flash",
            "ctx": 1048576,
            "tools": True,
            "vision": True,
            "cin": 0.075,
            "cout": 0.3,
        },
    ],
    "openai": [
        {
            "model_id": "gpt-4o",
            "display_name": "GPT-4o",
            "ctx": 128000,
            "tools": True,
            "vision": True,
            "cin": 2.5,
            "cout": 10.0,
        },
        {
            "model_id": "gpt-4o-mini",
            "display_name": "GPT-4o Mini",
            "ctx": 128000,
            "tools": True,
            "vision": True,
            "cin": 0.15,
            "cout": 0.6,
        },
        {
            "model_id": "o3-mini",
            "display_name": "o3 Mini",
            "ctx": 200000,
            "tools": True,
            "vision": False,
            "cin": 1.1,
            "cout": 4.4,
        },
        {
            "model_id": "o1",
            "display_name": "o1",
            "ctx": 200000,
            "tools": True,
            "vision": True,
            "cin": 15.0,
            "cout": 60.0,
        },
    ],
    "deepseek": [
        {
            "model_id": "deepseek-chat",
            "display_name": "DeepSeek Chat",
            "ctx": 64000,
            "tools": True,
            "vision": False,
            "cin": 0.27,
            "cout": 1.1,
        },
        {
            "model_id": "deepseek-reasoner",
            "display_name": "DeepSeek Reasoner",
            "ctx": 64000,
            "tools": False,
            "vision": False,
            "cin": 0.55,
            "cout": 2.19,
        },
    ],
}


class ModelCatalog:
    """
    Provides model listing and DB seeding for all supported providers.
    """

    def list_models(self, provider_name: str) -> list[ModelEntry]:
        """Return all active ModelEntry rows for a given provider name."""
        with Session(engine) as session:
            provider = session.exec(
                select(LLMProvider).where(LLMProvider.name == provider_name)
            ).first()
            if not provider:
                return []
            return session.exec(
                select(ModelEntry).where(
                    ModelEntry.provider_id == provider.id,
                    ModelEntry.is_active,
                )
            ).all()

    def list_all_models(self) -> list[ModelEntry]:
        """Return all active ModelEntry rows across all providers."""
        with Session(engine) as session:
            return session.exec(select(ModelEntry).where(ModelEntry.is_active)).all()

    def sync_to_db(self) -> None:
        """
        Seed the model_entries table from STATIC_CATALOG.
        Skips models that already exist (idempotent).
        """
        with Session(engine) as session:
            for provider_name, models in STATIC_CATALOG.items():
                provider = session.exec(
                    select(LLMProvider).where(LLMProvider.name == provider_name)
                ).first()
                if not provider:
                    continue  # provider not registered yet

                for m in models:
                    exists = session.exec(
                        select(ModelEntry).where(
                            ModelEntry.provider_id == provider.id,
                            ModelEntry.model_id == m["model_id"],
                        )
                    ).first()
                    if not exists:
                        entry = ModelEntry(
                            provider_id=provider.id,
                            model_id=m["model_id"],
                            display_name=m["display_name"],
                            context_window=m["ctx"],
                            supports_tools=m["tools"],
                            supports_vision=m["vision"],
                            supports_streaming=True,
                            cost_input_per_1m=m.get("cin"),
                            cost_output_per_1m=m.get("cout"),
                        )
                        session.add(entry)
            session.commit()
