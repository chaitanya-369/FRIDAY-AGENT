"""
friday/api/routes/session.py

REST API endpoints for managing FRIDAY's active model session.

Endpoints:
  GET  /api/session           → current active (provider, model, set_by, ...)
  POST /api/session/switch    → switch to a new (provider, model) immediately
  GET  /api/session/history   → last 10 switch events
  POST /api/session/reset     → reset to settings.default_provider/model
  GET  /api/session/status    → health of the active provider (key health + offline check)
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import APIKey, LLMProvider, ModelEntry
from friday.llm.session import active_session

router = APIRouter(prefix="/api/session", tags=["session"])


# ── Pydantic schemas ──────────────────────────────────────────────────────────


class SessionState(BaseModel):
    provider_name: str
    model_id: str
    set_by: str
    reason: str
    switched_at: Optional[str]
    switch_history: list[dict]


class SwitchRequest(BaseModel):
    provider_name: str
    model_id: str
    reason: Optional[str] = "manual switch via API"


class SwitchResponse(BaseModel):
    success: bool
    message: str
    previous_provider: str
    previous_model: str
    new_provider: str
    new_model: str


class KeyHealthEntry(BaseModel):
    label: str
    is_active: bool
    is_rate_limited: bool
    rate_limited_until: Optional[str]
    request_count: int
    error_count: int


class ProviderHealthEntry(BaseModel):
    provider_name: str
    display_name: str
    is_enabled: bool
    healthy_keys: int
    rate_limited_keys: int
    auth_failed_keys: int
    total_keys: int
    keys: list[KeyHealthEntry]


class SessionStatusResponse(BaseModel):
    provider_name: str
    model_id: str
    set_by: str
    is_online: bool
    ollama_available: bool
    ollama_models: list[str]
    providers: list[ProviderHealthEntry]


# ── Validation helpers ────────────────────────────────────────────────────────


def _validate_provider_and_model(provider_name: str, model_id: str) -> None:
    """Raise HTTPException if provider or model don't exist in the DB."""
    with Session(engine) as db:
        provider = db.exec(
            select(LLMProvider).where(
                LLMProvider.name == provider_name,
                LLMProvider.is_enabled,
            )
        ).first()
        if not provider:
            raise HTTPException(
                status_code=404,
                detail=f"Provider '{provider_name}' not found or not enabled. "
                "Use GET /api/providers to list available providers.",
            )

        model = db.exec(
            select(ModelEntry).where(
                ModelEntry.provider_id == provider.id,
                ModelEntry.model_id == model_id,
                ModelEntry.is_active,
            )
        ).first()
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{model_id}' not found for provider '{provider_name}'. "
                "Use GET /api/models to list available models.",
            )


def _check_ollama() -> tuple[bool, list[str]]:
    """Return (is_available, model_names) for local Ollama instance."""
    try:
        import httpx

        resp = httpx.get("http://localhost:11434/api/tags", timeout=2)
        resp.raise_for_status()
        data = resp.json()
        models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
        return True, [m for m in models if m]
    except Exception:
        return False, []


# ── Endpoints ──────────────────────────────────────────────────────────────────


@router.get("", response_model=SessionState)
def get_session():
    """Return the current active model session state."""
    state = active_session.get_state()
    return SessionState(
        provider_name=state["provider_name"],
        model_id=state["model_id"],
        set_by=state["set_by"],
        reason=state.get("reason", ""),
        switched_at=state.get("switched_at"),
        switch_history=state.get("switch_history", []),
    )


@router.post("/switch", response_model=SwitchResponse)
def switch_session(req: SwitchRequest):
    """
    Switch the active model immediately.

    Validates that the requested provider and model exist in the catalog
    before making any changes.
    """
    _validate_provider_and_model(req.provider_name, req.model_id)

    previous_provider, previous_model = active_session.get()

    active_session.set(
        provider_name=req.provider_name,
        model_id=req.model_id,
        set_by="user",
        reason=req.reason or "manual switch via API",
    )

    return SwitchResponse(
        success=True,
        message=f"Switched from {previous_provider}/{previous_model} to {req.provider_name}/{req.model_id}.",
        previous_provider=previous_provider,
        previous_model=previous_model,
        new_provider=req.provider_name,
        new_model=req.model_id,
    )


@router.get("/history", response_model=list[dict])
def get_session_history():
    """Return the last 10 model switch events (newest first)."""
    return active_session.get_history()


@router.post("/reset", response_model=SwitchResponse)
def reset_session():
    """Reset the active session to settings defaults (default_provider / default_model)."""
    previous_provider, previous_model = active_session.get()
    active_session.reset_to_default()
    new_provider, new_model = active_session.get()

    return SwitchResponse(
        success=True,
        message=f"Reset to default: {new_provider}/{new_model}.",
        previous_provider=previous_provider,
        previous_model=previous_model,
        new_provider=new_provider,
        new_model=new_model,
    )


@router.get("/status", response_model=SessionStatusResponse)
def get_session_status():
    """
    Return a comprehensive health report for the active session.

    Includes:
      - Current active provider + model
      - Per-provider key health (healthy / rate-limited / auth-failed)
      - Ollama availability check
    """
    current_provider, current_model = active_session.get()
    state = active_session.get_state()
    now = datetime.now(timezone.utc)

    # Ollama check
    ollama_available, ollama_models = _check_ollama()

    # Per-provider health from DB
    provider_health: list[ProviderHealthEntry] = []
    is_online = False

    with Session(engine) as db:
        providers = db.exec(
            select(LLMProvider)
            .where(LLMProvider.is_enabled)
            .order_by(LLMProvider.priority)
        ).all()

        for prov in providers:
            keys = db.exec(select(APIKey).where(APIKey.provider_id == prov.id)).all()

            key_entries: list[KeyHealthEntry] = []
            healthy_count = 0
            rate_limited_count = 0
            auth_failed_count = 0

            for k in keys:
                rate_limited_until_dt = k.rate_limited_until
                is_rate_limited = False
                if rate_limited_until_dt:
                    rt = rate_limited_until_dt
                    if rt.tzinfo is None:
                        rt = rt.replace(tzinfo=timezone.utc)
                    is_rate_limited = rt > now

                if not k.is_active:
                    auth_failed_count += 1
                elif is_rate_limited:
                    rate_limited_count += 1
                else:
                    healthy_count += 1
                    if prov.name == current_provider:
                        is_online = True

                key_entries.append(
                    KeyHealthEntry(
                        label=k.label,
                        is_active=k.is_active,
                        is_rate_limited=is_rate_limited,
                        rate_limited_until=(
                            k.rate_limited_until.isoformat()
                            if k.rate_limited_until
                            else None
                        ),
                        request_count=k.request_count,
                        error_count=k.error_count,
                    )
                )

            provider_health.append(
                ProviderHealthEntry(
                    provider_name=prov.name,
                    display_name=prov.display_name,
                    is_enabled=prov.is_enabled,
                    healthy_keys=healthy_count,
                    rate_limited_keys=rate_limited_count,
                    auth_failed_keys=auth_failed_count,
                    total_keys=len(keys),
                    keys=key_entries,
                )
            )

    return SessionStatusResponse(
        provider_name=current_provider,
        model_id=current_model,
        set_by=state.get("set_by", "system"),
        is_online=is_online or ollama_available,
        ollama_available=ollama_available,
        ollama_models=ollama_models,
        providers=provider_health,
    )
