"""
friday/api/routes/providers.py

REST endpoints for managing LLM providers.
Providers registered here become available to LLMRouter immediately.
"""

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.models.db_models import LLMProvider
from friday.llm.models.schemas import ProviderCreate, ProviderRead, ProviderUpdate
from friday.llm.registry import list_registered_providers

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("", response_model=list[ProviderRead])
def list_providers():
    """List all registered LLM providers."""
    with Session(engine) as session:
        return session.exec(select(LLMProvider).order_by(LLMProvider.priority)).all()


@router.post("", response_model=ProviderRead, status_code=201)
def create_provider(data: ProviderCreate):
    """Register a new LLM provider."""
    if data.adapter_class not in [
        "AnthropicAdapter",
        "GroqAdapter",
        "OpenAIAdapter",
        "DeepSeekAdapter",
        "GeminiAdapter",
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown adapter_class '{data.adapter_class}'. "
            f"Registered providers: {list_registered_providers()}",
        )
    with Session(engine) as session:
        existing = session.exec(
            select(LLMProvider).where(LLMProvider.name == data.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409, detail=f"Provider '{data.name}' already exists."
            )
        provider = LLMProvider(**data.model_dump())
        session.add(provider)
        session.commit()
        session.refresh(provider)
        return provider


@router.patch("/{provider_id}", response_model=ProviderRead)
def update_provider(provider_id: int, data: ProviderUpdate):
    """Enable/disable a provider or change its priority."""
    with Session(engine) as session:
        provider = session.get(LLMProvider, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found.")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(provider, field, value)
        session.add(provider)
        session.commit()
        session.refresh(provider)
        return provider


@router.delete("/{provider_id}", status_code=204)
def delete_provider(provider_id: int):
    """Remove a provider and all its keys/models."""
    with Session(engine) as session:
        provider = session.get(LLMProvider, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found.")
        session.delete(provider)
        session.commit()
