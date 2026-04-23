"""
friday/llm/key_pool.py

Manages multiple API keys for a single LLM provider.
Handles rotation strategies, health tracking, and rate-limit awareness.
"""

import random
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import APIKey


class KeyPool:
    """
    Selects healthy API keys for a provider using a configurable strategy.

    Rotation strategies:
      - round_robin : cycle through keys in insertion order
      - least_used  : key with the lowest total request_count
      - priority    : key with the lowest priority number (1 = highest)
      - random      : pick a random healthy key each time

    Health rules:
      - is_active == False → permanently disabled (auth error)
      - rate_limited_until > now → temporarily skipped (429 received)
    """

    def __init__(self, provider_id: int, strategy: str = "round_robin"):
        self.provider_id = provider_id
        self.strategy = strategy
        self._rr_index = 0  # round-robin cursor

    # ── Private helpers ────────────────────────────────────────────────────────

    def _healthy_keys(self) -> list[APIKey]:
        """Load active, non-rate-limited keys from DB for this provider."""
        now = datetime.now(timezone.utc)
        with Session(engine) as session:
            stmt = (
                select(APIKey)
                .where(
                    APIKey.provider_id == self.provider_id,
                    APIKey.is_active,
                )
                .order_by(APIKey.priority)
            )
            all_keys = session.exec(stmt).all()

        return [
            k
            for k in all_keys
            if k.rate_limited_until is None
            or k.rate_limited_until.replace(tzinfo=timezone.utc) < now
        ]

    def _update_key(self, key_id: int, **fields) -> None:
        """Persist field updates to an APIKey row."""
        with Session(engine) as session:
            key = session.get(APIKey, key_id)
            if key:
                for field_name, value in fields.items():
                    setattr(key, field_name, value)
                session.add(key)
                session.commit()

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_key(self) -> Optional[APIKey]:
        """
        Return the next healthy key according to the configured strategy.
        Returns None if no healthy keys are available.
        """
        keys = self._healthy_keys()
        if not keys:
            return None

        if self.strategy == "round_robin":
            key = keys[self._rr_index % len(keys)]
            self._rr_index += 1
            return key

        if self.strategy == "least_used":
            return min(keys, key=lambda k: k.request_count)

        if self.strategy == "priority":
            return min(keys, key=lambda k: k.priority)

        if self.strategy == "random":
            return random.choice(keys)

        # Fallback to first available
        return keys[0]

    def report_success(self, key: APIKey) -> None:
        """Increment request_count and update last_used_at."""
        self._update_key(
            key.id,
            request_count=key.request_count + 1,
            last_used_at=datetime.now(timezone.utc),
        )

    def report_rate_limit(self, key: APIKey, retry_after_seconds: int = 60) -> None:
        """Mark the key as rate-limited until retry_after_seconds from now."""
        from datetime import timedelta

        self._update_key(
            key.id,
            error_count=key.error_count + 1,
            rate_limited_until=datetime.now(timezone.utc)
            + timedelta(seconds=retry_after_seconds),
        )

    def report_auth_error(self, key: APIKey) -> None:
        """Permanently deactivate a key that returned an authentication error."""
        self._update_key(key.id, is_active=False, error_count=key.error_count + 1)

    def report_error(self, key: APIKey) -> None:
        """Increment error_count for a generic (non-rate-limit, non-auth) failure."""
        self._update_key(key.id, error_count=key.error_count + 1)

    def all_exhausted(self) -> bool:
        """True if no healthy keys remain."""
        return len(self._healthy_keys()) == 0
