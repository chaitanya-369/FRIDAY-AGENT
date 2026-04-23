"""
friday/api/routes/models_catalog.py

REST endpoints for browsing the model catalog.
"""

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from friday.core.database import engine
from friday.llm.model_catalog import ModelCatalog
from friday.llm.models.db_models import LLMProvider
from friday.llm.models.schemas import ModelRead

router = APIRouter(prefix="/api/models", tags=["models"])
catalog = ModelCatalog()


@router.get("", response_model=list[ModelRead])
def list_all_models():
    """List all active models across every registered provider."""
    return catalog.list_all_models()


@router.get("/{provider_name}", response_model=list[ModelRead])
def list_models_for_provider(provider_name: str):
    """List all active models for a specific provider."""
    models = catalog.list_models(provider_name)
    if not models:
        raise HTTPException(
            status_code=404,
            detail=f"No models found for provider '{provider_name}'. "
            "Check the provider is registered and enabled.",
        )
    return models


@router.post("/{provider_name}/sync", status_code=200)
def sync_provider_models(provider_name: str):
    """
    Re-seed the model catalog for a provider from the static catalog.
    Useful after adding new model entries to STATIC_CATALOG.
    """
    with Session(engine) as session:
        provider = session.exec(
            select(LLMProvider).where(LLMProvider.name == provider_name)
        ).first()
        if not provider:
            raise HTTPException(
                status_code=404, detail=f"Provider '{provider_name}' not registered."
            )

    catalog.sync_to_db()
    return {"message": f"Model catalog synced for '{provider_name}'."}
