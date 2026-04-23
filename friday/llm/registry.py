"""
friday/llm/registry.py

Maps provider name strings to their concrete adapter classes.
Add new providers here as Phase 2 adapters are built.
"""

from friday.llm.adapters.base import BaseAdapter
from friday.llm.adapters.anthropic_adapter import AnthropicAdapter
from friday.llm.adapters.groq_adapter import GroqAdapter
from friday.llm.adapters.openai_adapter import OpenAIAdapter
from friday.llm.adapters.deepseek_adapter import DeepSeekAdapter
from friday.llm.adapters.gemini_adapter import GeminiAdapter

# ---------------------------------------------------------------------------
# Phase 1 — Active providers
# Phase 2 — Mistral, Together, Cohere, xAI, Bedrock (add adapters here when ready)
# ---------------------------------------------------------------------------
ADAPTER_REGISTRY: dict[str, type[BaseAdapter]] = {
    "anthropic": AnthropicAdapter,
    "groq": GroqAdapter,
    "openai": OpenAIAdapter,
    "deepseek": DeepSeekAdapter,
    "gemini": GeminiAdapter,
}


def get_adapter(provider_name: str) -> BaseAdapter:
    """
    Instantiate and return the adapter for a given provider name.

    Args:
        provider_name: Lowercase provider identifier (e.g. "anthropic").

    Raises:
        ValueError: If the provider is not registered in ADAPTER_REGISTRY.
    """
    cls = ADAPTER_REGISTRY.get(provider_name)
    if not cls:
        supported = ", ".join(ADAPTER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported LLM provider: '{provider_name}'. Supported: {supported}"
        )
    return cls()


def list_registered_providers() -> list[str]:
    """Return a sorted list of all registered provider names."""
    return sorted(ADAPTER_REGISTRY.keys())
