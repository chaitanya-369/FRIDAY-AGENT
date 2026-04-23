"""
friday/api/routes/keys.py

REST endpoints for managing API keys.
Supports multiple keys per provider with health visibility.
Key values are masked in list responses (last 4 chars only).
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import APIKey, LLMProvider
from friday.llm.models.schemas import (
    KeyCreate,
    KeyHealth,
    KeyRead,
    KeyTestResult,
    KeyUpdate,
)
from friday.llm.registry import get_adapter

router = APIRouter(prefix="/api/keys", tags=["keys"])


def _mask(key_value: str) -> str:
    """Return key with all but last 4 chars masked."""
    if len(key_value) <= 4:
        return "****"
    return "*" * (len(key_value) - 4) + key_value[-4:]


@router.get("", response_model=list[KeyRead])
def list_keys():
    """List all API keys (values masked)."""
    with Session(engine) as session:
        keys = session.exec(
            select(APIKey).order_by(APIKey.provider_id, APIKey.priority)
        ).all()
    result = []
    for k in keys:
        d = k.model_dump()
        d["key_value"] = _mask(k.key_value)
        result.append(KeyRead(**d))
    return result


@router.post("", response_model=KeyRead, status_code=201)
def add_key(data: KeyCreate):
    """Add a new API key for a provider."""
    with Session(engine) as session:
        provider = session.get(LLMProvider, data.provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found.")
        key = APIKey(**data.model_dump())
        session.add(key)
        session.commit()
        session.refresh(key)
        d = key.model_dump()
        d["key_value"] = _mask(key.key_value)
        return KeyRead(**d)


@router.patch("/{key_id}", response_model=KeyRead)
def update_key(key_id: int, data: KeyUpdate):
    """Update key label, active status, or priority."""
    with Session(engine) as session:
        key = session.get(APIKey, key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(key, field, value)
        session.add(key)
        session.commit()
        session.refresh(key)
        d = key.model_dump()
        d["key_value"] = _mask(key.key_value)
        return KeyRead(**d)


@router.delete("/{key_id}", status_code=204)
def delete_key(key_id: int):
    """Remove an API key."""
    with Session(engine) as session:
        key = session.get(APIKey, key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found.")
        session.delete(key)
        session.commit()


@router.get("/{key_id}/health", response_model=KeyHealth)
def key_health(key_id: int):
    """Get health stats for a specific key."""
    with Session(engine) as session:
        key = session.get(APIKey, key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found.")
        now = datetime.now(timezone.utc)
        is_healthy = key.is_active and (
            key.rate_limited_until is None
            or key.rate_limited_until.replace(tzinfo=timezone.utc) < now
        )
        return KeyHealth(
            id=key.id,
            label=key.label,
            is_active=key.is_active,
            request_count=key.request_count,
            error_count=key.error_count,
            rate_limited_until=key.rate_limited_until,
            last_used_at=key.last_used_at,
            is_healthy=is_healthy,
        )


@router.post("/{key_id}/test", response_model=KeyTestResult)
def test_key(key_id: int):
    """Send a minimal test request to validate the key works right now."""
    with Session(engine) as session:
        key = session.get(APIKey, key_id)
        if not key:
            raise HTTPException(status_code=404, detail="Key not found.")
        provider = session.get(LLMProvider, key.provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found.")

    try:
        adapter = get_adapter(provider.name)
        # Minimal single-token probe — use cheapest model for provider
        from friday.llm.model_catalog import STATIC_CATALOG

        models = STATIC_CATALOG.get(provider.name, [])
        model_id = models[-1]["model_id"] if models else "gpt-4o-mini"

        list(
            adapter.stream(
                messages=[{"role": "user", "content": "Reply with one word: ready"}],
                system_prompt="You are a test assistant.",
                model=model_id,
                api_key=key.key_value,
                tools=[],
                max_tokens=5,
                base_url=provider.base_url,
            )
        )
        return KeyTestResult(success=True, message="Key is valid and responsive.")
    except Exception as e:
        return KeyTestResult(success=False, message=str(e))
