"""
friday/llm/offline_guardian.py

OfflineGuardian — FRIDAY's always-on resilience layer.

When every cloud LLM provider and API key is exhausted, the OfflineGuardian
ensures FRIDAY can still respond to Boss in a useful, FRIDAY-persona way.

Fallback chain (executed in order):
  1. Ollama (local, auto-detected — no config required)
     → Probes http://localhost:11434/api/tags to check if Ollama is running
     → Lists available models and picks the best one
     → Streams a response using the Ollama OpenAI-compat endpoint

  2. Deterministic Response Engine (zero-dependency fallback)
     → Generates a rich FRIDAY-persona response explaining:
         - Which providers failed and why (rate-limit / auth / network)
         - Which keys are exhausted and when rate-limits expire
         - Whether Ollama was detected (and what models are available)
         - Concrete next steps Boss can take
     → Always returns something useful, never goes silent

Usage:
    from friday.llm.offline_guardian import offline_guardian
    response = offline_guardian.respond(user_input="...", error=exhausted_error)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Ollama defaults — no config needed, auto-detected at runtime
_OLLAMA_BASE_URL = "http://localhost:11434"
_OLLAMA_TIMEOUT_SECONDS = 3  # fast probe; fail quickly if Ollama isn't running

# Preferred local model quality order (best → lightest)
_OLLAMA_PREFERRED_MODELS = [
    "llama3.3",
    "llama3.2",
    "llama3.1",
    "llama3",
    "mistral",
    "mixtral",
    "gemma2",
    "gemma",
    "phi3",
    "tinyllama",
]


class OllamaNotAvailable(Exception):
    """Raised when Ollama is not running or has no models available."""


class OfflineGuardian:
    """
    Always-on resilience layer. Called when LLMRouter raises LLMExhaustedError.

    Public interface:
        respond(user_input, error) → str   (complete response text)
    """

    # ── Ollama probe ──────────────────────────────────────────────────────────

    def _probe_ollama(self) -> list[str]:
        """
        Check if Ollama is running and return a list of available model names.
        Raises OllamaNotAvailable if not reachable or no models found.
        """
        try:
            import httpx

            resp = httpx.get(
                f"{_OLLAMA_BASE_URL}/api/tags",
                timeout=_OLLAMA_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            models = data.get("models", [])
            names = [m.get("name", "").split(":")[0].lower() for m in models]
            names = [n for n in names if n]  # filter empty
            if not names:
                raise OllamaNotAvailable(
                    "Ollama is running but has no models installed."
                )
            return names
        except ImportError:
            raise OllamaNotAvailable("httpx is not installed.")
        except Exception as e:
            raise OllamaNotAvailable(f"Ollama not reachable: {e}") from e

    def _pick_ollama_model(self, available: list[str]) -> str:
        """
        Select the best available Ollama model from our preferred list.
        Falls back to the first available model if none match preferences.
        """
        available_set = set(available)
        for preferred in _OLLAMA_PREFERRED_MODELS:
            if preferred in available_set:
                return preferred
        return available[0]  # anything is better than nothing

    def _stream_ollama(self, model: str, user_input: str) -> str:
        """
        Call Ollama's OpenAI-compat chat endpoint and return the full response.
        Non-streaming for simplicity (Ollama is local so latency is low).
        """
        try:
            import httpx

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are FRIDAY — Female Replacement Intelligent Digital Assistant Youth. "
                            "You are professional, precise, and sharp. Address the user as 'Boss'. "
                            "You are currently running locally via Ollama because cloud providers are unavailable."
                        ),
                    },
                    {"role": "user", "content": user_input},
                ],
                "stream": False,
            }
            resp = httpx.post(
                f"{_OLLAMA_BASE_URL}/v1/chat/completions",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise OllamaNotAvailable(f"Ollama chat failed: {e}") from e

    # ── Key health analysis ───────────────────────────────────────────────────

    def _analyze_key_health(self) -> dict:
        """
        Inspect the api_keys table to build a human-readable status summary.

        Returns a dict with:
          - provider_summaries: list of per-provider status strings
          - earliest_recovery: datetime when the first rate-limited key recovers (or None)
          - has_any_active: bool — whether any key is technically active (not deactivated)
        """
        try:
            from friday.llm.models.db_models import APIKey, LLMProvider
            from sqlmodel import Session, select
            from friday.core.database import engine

            now = datetime.now(timezone.utc)
            summaries: list[str] = []
            earliest_recovery: Optional[datetime] = None
            has_any_active = False

            with Session(engine) as db:
                providers = db.exec(
                    select(LLMProvider).where(LLMProvider.is_enabled)
                ).all()

                for prov in providers:
                    keys = db.exec(
                        select(APIKey).where(APIKey.provider_id == prov.id)
                    ).all()

                    if not keys:
                        summaries.append(f"  {prov.display_name}: no keys configured")
                        continue

                    auth_failed = [k for k in keys if not k.is_active]
                    rate_limited = [
                        k
                        for k in keys
                        if k.is_active
                        and k.rate_limited_until
                        and k.rate_limited_until.replace(tzinfo=timezone.utc) > now
                    ]
                    healthy = [
                        k
                        for k in keys
                        if k.is_active
                        and (
                            not k.rate_limited_until
                            or k.rate_limited_until.replace(tzinfo=timezone.utc) <= now
                        )
                    ]

                    if healthy:
                        has_any_active = True
                        summaries.append(
                            f"  {prov.display_name}: {len(healthy)} healthy key(s) ✓"
                        )
                    elif rate_limited:
                        # Find earliest recovery time
                        for k in rate_limited:
                            rt = k.rate_limited_until.replace(tzinfo=timezone.utc)
                            if earliest_recovery is None or rt < earliest_recovery:
                                earliest_recovery = rt
                        next_available = min(
                            k.rate_limited_until.replace(tzinfo=timezone.utc)
                            for k in rate_limited
                        )
                        wait_mins = max(
                            0, int((next_available - now).total_seconds() / 60)
                        )
                        summaries.append(
                            f"  {prov.display_name}: {len(rate_limited)} key(s) rate-limited "
                            f"— recovers in ~{wait_mins} min"
                        )
                    elif auth_failed:
                        summaries.append(
                            f"  {prov.display_name}: {len(auth_failed)} key(s) have auth errors "
                            "(invalid or revoked)"
                        )
                    else:
                        summaries.append(f"  {prov.display_name}: no usable keys")

            return {
                "provider_summaries": summaries,
                "earliest_recovery": earliest_recovery,
                "has_any_active": has_any_active,
            }
        except Exception as e:
            logger.warning("OfflineGuardian: failed to analyze key health: %s", e)
            return {
                "provider_summaries": ["  (key health analysis unavailable)"],
                "earliest_recovery": None,
                "has_any_active": False,
            }

    # ── Deterministic response builder ────────────────────────────────────────

    def _build_deterministic_response(
        self,
        user_input: str,
        error: Exception,
        ollama_status: str,
        health: dict,
    ) -> str:
        """
        Build a rich, FRIDAY-persona diagnostic response when no LLM is available.
        """
        now = datetime.now(timezone.utc)
        lines: list[str] = [
            "Boss, I'm currently unable to reach any of my cloud intelligence providers.",
            "",
            "**Provider Status:**",
        ]
        lines.extend(health["provider_summaries"])

        # Ollama status
        lines.append("")
        lines.append(f"**Local Fallback (Ollama):** {ollama_status}")

        # Recovery estimate
        lines.append("")
        if health["earliest_recovery"]:
            delta = health["earliest_recovery"] - now
            wait_mins = max(0, int(delta.total_seconds() / 60))
            if wait_mins <= 1:
                lines.append(
                    "**Recovery:** At least one provider should be available within a minute."
                )
            elif wait_mins <= 60:
                lines.append(
                    f"**Recovery:** Earliest rate-limit lifts in ~{wait_mins} minutes."
                )
            else:
                lines.append(
                    f"**Recovery:** Earliest rate-limit lifts in ~{wait_mins // 60}h {wait_mins % 60}m."
                )
        else:
            lines.append(
                "**Recovery:** No rate-limit expiry detected — "
                "this may be an auth error or network issue."
            )

        # Suggested actions
        lines.append("")
        lines.append("**What you can do, Boss:**")
        lines.append(
            "  1. Add or rotate API keys via the /api/keys endpoint or the FRIDAY control panel."
        )
        lines.append("  2. Wait for the rate-limit window to expire, then try again.")
        lines.append(
            "  3. Install Ollama (ollama.ai) and pull a model for local fallback."
        )
        lines.append(
            "  4. Say 'list models' to see configured providers, or 'status' for current model."
        )

        # Echo what Boss asked (so they know we received it)
        if user_input:
            lines.append("")
            lines.append(
                f'*(Your message was: "{user_input[:120]}{"..." if len(user_input) > 120 else ""}")*'
            )
            lines.append(
                "I'll be ready to process it as soon as a provider comes back online."
            )

        return "\n".join(lines)

    # ── Public entry point ────────────────────────────────────────────────────

    def respond(self, user_input: str, error: Exception) -> str:
        """
        Generate a response when all cloud providers are exhausted.

        Tries Ollama first, falls back to deterministic response.

        Args:
            user_input : The original user message (may be empty for tool re-entry).
            error      : The LLMExhaustedError (or other exception) that triggered this.

        Returns:
            A complete response string in FRIDAY's voice.
        """
        # ollama_available = False (unused variable removed)
        ollama_status = "not detected"

        # ── Attempt 1: Ollama ──────────────────────────────────────────────
        try:
            available_models = self._probe_ollama()
            best_model = self._pick_ollama_model(available_models)
            ollama_status = f"available — using **{best_model}** ({', '.join(available_models[:4])})"

            logger.info(
                "OfflineGuardian: Ollama available, using model '%s'", best_model
            )

            try:
                response = self._stream_ollama(best_model, user_input or "Hello")
                return f"*(Running locally via Ollama / {best_model})*\n\n{response}"
            except OllamaNotAvailable as chat_err:
                logger.warning("OfflineGuardian: Ollama chat failed: %s", chat_err)
                ollama_status = f"detected but chat failed: {chat_err}"

        except OllamaNotAvailable as probe_err:
            ollama_status = f"not running ({probe_err})"
            logger.info("OfflineGuardian: Ollama not available: %s", probe_err)

        # ── Attempt 2: Deterministic response ──────────────────────────────
        health = self._analyze_key_health()
        return self._build_deterministic_response(
            user_input=user_input,
            error=error,
            ollama_status=ollama_status,
            health=health,
        )


# ── Module-level singleton ─────────────────────────────────────────────────────

offline_guardian = OfflineGuardian()
