"""
friday/llm/session.py

ActiveModelSession — singleton that tracks FRIDAY's currently active
(provider, model) pair.

Design decisions:
  - In-memory cache: avoids a DB round-trip on every LLM call.
  - DB-backed persistence: chosen model survives server restarts.
  - Thread-safe: a threading.Lock protects all state mutations.
  - Single-row pattern: the `active_session` table always has exactly one row (id=1).
  - Notification-based: callers (brain, router) call notify_hard_failure() /
    notify_success() so the session can react to provider health automatically.

Usage:
    from friday.llm.session import active_session

    provider, model = active_session.get()
    active_session.set("openai", "gpt-4o", set_by="user", reason="user request")
    history = active_session.get_history()
"""

import threading
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from friday.config.settings import settings
from friday.core.database import engine
from friday.llm.models.db_models import ActiveSession


class ActiveModelSession:
    """
    Singleton managing FRIDAY's currently active (provider, model) pair.

    Public interface:
      get()                  → (provider_name, model_id)
      set(...)               → switch to a new provider/model, logs history
      get_state()            → full ActiveSession row as a dict
      get_history()          → list of last 10 switch events
      reset_to_default()     → revert to settings.default_provider / model
      notify_hard_failure()  → called by LLMRouter on LLMExhaustedError
      notify_success()       → called by LLMRouter on successful stream
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache: Optional[tuple[str, str]] = None  # (provider_name, model_id)
        self._initialized = False

    # ── Internal DB helpers ───────────────────────────────────────────────────

    def _load_or_create(self) -> ActiveSession:
        """
        Load the singleton row from DB.
        If it doesn't exist yet, create it using settings defaults.
        """
        with Session(engine) as db:
            row = db.exec(select(ActiveSession).where(ActiveSession.id == 1)).first()
            if row is None:
                row = ActiveSession(
                    id=1,
                    provider_name=settings.default_provider,
                    model_id=settings.default_model,
                    set_by="system",
                    reason="initial default from settings",
                    switched_at=datetime.now(timezone.utc),
                )
                db.add(row)
                db.commit()
                db.refresh(row)
            return row

    def _ensure_initialized(self) -> None:
        """Lazy-load the in-memory cache from DB on first access."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    row = self._load_or_create()
                    self._cache = (row.provider_name, row.model_id)
                    self._initialized = True

    # ── Public read API ───────────────────────────────────────────────────────

    def get(self) -> tuple[str, str]:
        """
        Return the currently active (provider_name, model_id).
        Uses in-memory cache — zero DB latency.
        """
        self._ensure_initialized()
        with self._lock:
            return self._cache  # type: ignore[return-value]

    def get_state(self) -> dict:
        """Return the full state dict of the current active session row."""
        with Session(engine) as db:
            row = db.exec(select(ActiveSession).where(ActiveSession.id == 1)).first()
            if row is None:
                return {
                    "provider_name": settings.default_provider,
                    "model_id": settings.default_model,
                    "set_by": "system",
                    "reason": "not yet initialized",
                    "switched_at": None,
                    "switch_history": [],
                }
            return {
                "provider_name": row.provider_name,
                "model_id": row.model_id,
                "set_by": row.set_by,
                "reason": row.reason,
                "switched_at": row.switched_at.isoformat() if row.switched_at else None,
                "switch_history": row.get_history(),
            }

    def get_history(self) -> list[dict]:
        """Return the last 10 switch events (newest first)."""
        with Session(engine) as db:
            row = db.exec(select(ActiveSession).where(ActiveSession.id == 1)).first()
            return row.get_history() if row else []

    # ── Public write API ──────────────────────────────────────────────────────

    def set(
        self,
        provider_name: str,
        model_id: str,
        *,
        set_by: str = "user",
        reason: str = "",
    ) -> None:
        """
        Switch the active (provider, model).

        Args:
            provider_name : Target provider (e.g., "openai").
            model_id      : Target model ID (e.g., "gpt-4o").
            set_by        : Who is switching — "user" | "friday_auto" | "system".
            reason        : Human-readable reason for the switch.
        """
        now = datetime.now(timezone.utc)

        with self._lock:
            with Session(engine) as db:
                row = db.exec(
                    select(ActiveSession).where(ActiveSession.id == 1)
                ).first()
                if row is None:
                    row = ActiveSession(id=1)
                    db.add(row)

                # Push the OLD state into history before overwriting
                old_entry = {
                    "provider_name": row.provider_name,
                    "model_id": row.model_id,
                    "set_by": row.set_by,
                    "reason": row.reason,
                    "switched_at": row.switched_at.isoformat()
                    if row.switched_at
                    else None,
                }
                row.push_history_entry(old_entry)

                # Update to new state
                row.provider_name = provider_name
                row.model_id = model_id
                row.set_by = set_by
                row.reason = reason or f"switched by {set_by}"
                row.switched_at = now
                db.commit()

            # Update in-memory cache
            self._cache = (provider_name, model_id)

    def reset_to_default(self) -> None:
        """
        Reset the active session to settings.default_provider / default_model.
        Recorded in history with set_by="system".
        """
        self.set(
            provider_name=settings.default_provider,
            model_id=settings.default_model,
            set_by="system",
            reason="reset to settings default",
        )

    # ── Router notification hooks ─────────────────────────────────────────────

    def notify_hard_failure(
        self,
        failed_provider: str,
        failed_model: str,
        fallback_provider: str,
        fallback_model: str,
        error_summary: str,
    ) -> None:
        """
        Called by LLMRouter when the active provider exhausts all keys and
        a hard fallback was executed.

        Only auto-switches if the current session was NOT explicitly set by the user.
        If it was set by the user, we honour their choice and do NOT silently change it.
        """
        current_provider, _ = self.get()
        state = self.get_state()
        set_by = state.get("set_by", "system")

        if set_by == "user" and current_provider == failed_provider:
            # User explicitly chose this provider — don't silently switch.
            # The OfflineGuardian will still handle the response, but we leave
            # the session unchanged so the user's preference is preserved.
            return

        # Auto-switch: silent, with notification
        self.set(
            provider_name=fallback_provider,
            model_id=fallback_model,
            set_by="friday_auto",
            reason=f"hard failure on {failed_provider}: {error_summary}",
        )

    def notify_success(self, provider_name: str, model_id: str) -> None:
        """
        Called by LLMRouter after a successful stream.
        Currently a no-op but kept as a hook for future health-based routing.
        """
        pass


# ── Module-level singleton ─────────────────────────────────────────────────────

active_session = ActiveModelSession()
