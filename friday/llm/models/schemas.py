"""
friday/llm/models/schemas.py

Pydantic request/response schemas for the management REST API.
These are separate from DB models to decouple API shape from storage.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Provider ──────────────────────────────────────────────────────────────────


class ProviderCreate(BaseModel):
    name: str
    display_name: str
    adapter_class: str
    base_url: Optional[str] = None
    priority: int = 10


class ProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None
    base_url: Optional[str] = None


class ProviderRead(BaseModel):
    id: int
    name: str
    display_name: str
    adapter_class: str
    base_url: Optional[str]
    is_enabled: bool
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── API Key ───────────────────────────────────────────────────────────────────


class KeyCreate(BaseModel):
    provider_id: int
    label: str
    key_value: str
    priority: int = 10


class KeyUpdate(BaseModel):
    label: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class KeyRead(BaseModel):
    id: int
    provider_id: int
    label: str
    key_value: str  # shown masked by endpoint logic
    is_active: bool
    priority: int
    request_count: int
    error_count: int
    rate_limited_until: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class KeyHealth(BaseModel):
    id: int
    label: str
    is_active: bool
    request_count: int
    error_count: int
    rate_limited_until: Optional[datetime]
    last_used_at: Optional[datetime]
    is_healthy: bool


class KeyTestResult(BaseModel):
    success: bool
    message: str


# ── Model Catalog ─────────────────────────────────────────────────────────────


class ModelRead(BaseModel):
    id: int
    provider_id: int
    model_id: str
    display_name: str
    context_window: int
    supports_tools: bool
    supports_vision: bool
    supports_streaming: bool
    is_active: bool
    cost_input_per_1m: Optional[float]
    cost_output_per_1m: Optional[float]

    class Config:
        from_attributes = True


# ── Routing Config ────────────────────────────────────────────────────────────


class RoutingConfig(BaseModel):
    default_provider: str
    default_model: str
    key_rotation_strategy: str  # "round_robin" | "least_used" | "priority" | "random"
    fallback_chain: list[
        dict
    ]  # [{"provider": "groq", "model": "llama-3.3-70b-versatile"}, ...]


class RoutingConfigUpdate(BaseModel):
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    key_rotation_strategy: Optional[str] = None
    fallback_chain: Optional[list[dict]] = None
