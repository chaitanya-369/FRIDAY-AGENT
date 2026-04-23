"""
friday/llm/router.py

LLMRouter — the central orchestrator for all LLM calls.

Responsibilities:
  1. Resolve provider + model from DB or settings fallback.
  2. Pull a healthy API key from the KeyPool.
  3. Instantiate the correct adapter via the registry.
  4. Stream via the adapter, yielding StreamChunks to the caller.
  5. On rate-limit / auth error → rotate keys and retry.
  6. If all keys for a provider exhaust → walk the fallback chain.
"""

from typing import Generator, Optional

from sqlmodel import Session, select

from friday.config.settings import settings
from friday.core.database import engine
from friday.llm.adapters.base import StreamChunk
from friday.llm.key_pool import KeyPool
from friday.llm.models.db_models import APIKey, LLMProvider
from friday.llm.registry import get_adapter


class LLMExhaustedError(Exception):
    """Raised when all providers and keys in the fallback chain are exhausted."""


class LLMRouter:
    """
    Routes LLM calls across providers, models, and keys.

    Usage:
        router = LLMRouter()
        for chunk in router.stream(messages, system_prompt):
            if chunk.text:
                print(chunk.text, end="")
    """

    def __init__(self):
        self._strategy = settings.key_rotation_strategy

    # ── Provider / Key resolution ──────────────────────────────────────────────

    def _get_provider(self, name: str) -> Optional[LLMProvider]:
        with Session(engine) as session:
            return session.exec(
                select(LLMProvider).where(
                    LLMProvider.name == name,
                    LLMProvider.is_enabled,
                )
            ).first()

    def _get_default_provider(self) -> Optional[LLMProvider]:
        """Return the lowest-priority enabled provider, or settings fallback."""
        with Session(engine) as session:
            provider = session.exec(
                select(LLMProvider)
                .where(LLMProvider.is_enabled)
                .order_by(LLMProvider.priority)
            ).first()
        if provider:
            return provider
        # No DB record — fall back to settings
        return None

    def _build_fallback_chain(self) -> list[tuple[str, str]]:
        """
        Build an ordered fallback chain of (provider_name, model) pairs.
        Default order is by priority ascending; settings override applies.
        """
        with Session(engine) as session:
            providers = session.exec(
                select(LLMProvider)
                .where(LLMProvider.is_enabled)
                .order_by(LLMProvider.priority)
            ).all()

        chain = []
        for p in providers:
            # Use settings default model for the active provider, else first catalog model
            if p.name == settings.default_provider:
                chain.append((p.name, settings.default_model))
            else:
                from friday.llm.model_catalog import STATIC_CATALOG

                models = STATIC_CATALOG.get(p.name, [])
                if models:
                    chain.append((p.name, models[0]["model_id"]))
        return chain

    # ── Tool schema normalization ──────────────────────────────────────────────

    def _format_tools(self, provider_name: str, tool_schemas: list) -> list:
        """Convert unified tool schemas to the target provider's native format."""
        if not tool_schemas:
            return []
        adapter = get_adapter(provider_name)
        return adapter.format_tools(tool_schemas)

    # ── Core streaming ─────────────────────────────────────────────────────────

    def _stream_with_key(
        self,
        provider: LLMProvider,
        model: str,
        key: APIKey,
        messages: list,
        system_prompt: str,
        tools: list,
        max_tokens: int,
    ) -> Generator[StreamChunk, None, None]:
        """Single-attempt stream using one specific key."""
        adapter = get_adapter(provider.name)
        native_tools = adapter.format_tools(tools)
        yield from adapter.stream(
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            api_key=key.key_value,
            tools=native_tools,
            max_tokens=max_tokens,
            base_url=provider.base_url,
        )

    def stream(
        self,
        messages: list,
        system_prompt: str,
        model: Optional[str] = None,
        provider_name: Optional[str] = None,
        tool_schemas: Optional[list] = None,
        max_tokens: int = 1024,
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream one LLM turn with automatic key rotation and provider fallback.

        Args:
            messages      : Conversation history (provider-native dicts).
            system_prompt : Formatted FRIDAY system prompt.
            model         : Override model ID. If None, uses settings default.
            provider_name : Override provider. If None, uses DB default.
            tool_schemas  : List of unified {"name", "description", "parameters"} dicts.
            max_tokens    : Max tokens to generate per turn.

        Yields:
            StreamChunk objects — text first, then a final chunk.

        Raises:
            LLMExhaustedError: If every provider and key in the chain fails.
        """
        tools = tool_schemas or []

        # Build the ordered chain of (provider_name, model) to try
        if provider_name:
            resolved_model = model or settings.default_model
            chain = [(provider_name, resolved_model)]
        else:
            chain = self._build_fallback_chain()
            if model:
                # Apply model override to first entry
                if chain:
                    chain[0] = (chain[0][0], model)

        last_error = None

        for p_name, p_model in chain:
            provider = self._get_provider(p_name)
            if not provider:
                continue

            pool = KeyPool(provider_id=provider.id, strategy=self._strategy)

            # Try every healthy key for this provider
            while True:
                key = pool.get_key()
                if key is None:
                    break  # All keys exhausted for this provider → next in chain

                try:
                    yield from self._stream_with_key(
                        provider=provider,
                        model=p_model,
                        key=key,
                        messages=messages,
                        system_prompt=system_prompt,
                        tools=tools,
                        max_tokens=max_tokens,
                    )
                    pool.report_success(key)
                    return  # Success — we're done

                except Exception as e:
                    err_str = str(e).lower()
                    if "rate" in err_str or "429" in err_str or "rate_limit" in err_str:
                        pool.report_rate_limit(key, retry_after_seconds=60)
                    elif (
                        "auth" in err_str
                        or "401" in err_str
                        or "403" in err_str
                        or "invalid_api_key" in err_str
                    ):
                        pool.report_auth_error(key)
                    else:
                        pool.report_error(key)
                    last_error = e
                    # Loop continues → try next key for same provider

        raise LLMExhaustedError(
            f"All providers and keys exhausted. Last error: {last_error}"
        )
