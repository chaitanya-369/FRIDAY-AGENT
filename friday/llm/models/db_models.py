"""
friday/llm/models/db_models.py

SQLModel table definitions for the Omni-LLM layer:
  - LLMProvider   : registered provider (anthropic, groq, gemini, openai, deepseek)
  - APIKey        : one or more keys per provider, health-tracked
  - ModelEntry    : catalog of models per provider
  - ActiveSession : single-row table tracking the currently active (provider, model) pair
"""

import json
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class LLMProvider(SQLModel, table=True):
    """A registered LLM provider."""

    __tablename__ = "llm_providers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(
        index=True, unique=True
    )  # "anthropic" | "groq" | "gemini" | "openai" | "deepseek"
    display_name: str  # "Anthropic Claude"
    adapter_class: str  # "AnthropicAdapter"
    base_url: Optional[str] = None  # for OpenAI-compat providers
    is_enabled: bool = True
    priority: int = 10  # lower = preferred in fallback chain
    created_at: datetime = Field(default_factory=datetime.utcnow)


class APIKey(SQLModel, table=True):
    """An API key belonging to a provider. Multiple keys per provider are allowed."""

    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="llm_providers.id")
    label: str  # "groq-personal-1", "anthropic-work"
    key_value: str  # plaintext (add database.db to .gitignore)
    is_active: bool = True
    priority: int = 10  # lower = preferred within the pool
    request_count: int = 0
    error_count: int = 0
    rate_limited_until: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelEntry(SQLModel, table=True):
    """A known model for a given provider."""

    __tablename__ = "model_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="llm_providers.id")
    model_id: str  # "claude-sonnet-4-5-20250514"
    display_name: str  # "Claude Sonnet 4.5"
    context_window: int = 4096
    supports_tools: bool = True
    supports_vision: bool = False
    supports_streaming: bool = True
    is_active: bool = True
    cost_input_per_1m: Optional[float] = None  # USD per 1M input tokens
    cost_output_per_1m: Optional[float] = None  # USD per 1M output tokens


class ActiveSession(SQLModel, table=True):
    """
    Single-row table (always id=1) that persists FRIDAY's currently active
    LLM selection across restarts.

    Fields:
      provider_name  : The currently active provider ("groq", "anthropic", ...)
      model_id       : The currently active model_id
      set_by         : Who last changed it — "user" | "friday_auto" | "system"
      reason         : Free-text reason for the last switch (e.g., "key exhausted")
      switched_at    : Timestamp of the last switch
      switch_history : JSON list of the last 10 switches, newest first.
                       Each entry: {provider, model, set_by, reason, switched_at}
    """

    __tablename__ = "active_session"

    id: int = Field(default=1, primary_key=True)  # always row 1 — singleton
    provider_name: str = Field(default="groq")
    model_id: str = Field(default="llama-3.3-70b-versatile")
    set_by: str = Field(default="system")  # "user" | "friday_auto" | "system"
    reason: str = Field(default="initial default")
    switched_at: datetime = Field(default_factory=datetime.utcnow)
    switch_history: str = Field(default="[]")  # JSON-encoded list[dict], max 10 entries

    # ── Convenience helpers ────────────────────────────────────────────────────

    def get_history(self) -> list[dict]:
        """Deserialize switch_history JSON into a list of dicts."""
        try:
            return json.loads(self.switch_history)
        except (json.JSONDecodeError, TypeError):
            return []

    def push_history_entry(self, entry: dict) -> None:
        """
        Prepend a new entry to switch_history, keeping only the latest 10.
        Mutates self.switch_history in-place — caller must commit the session.
        """
        history = self.get_history()
        history.insert(0, entry)
        self.switch_history = json.dumps(history[:10])
