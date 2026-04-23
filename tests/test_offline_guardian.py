"""
tests/test_offline_guardian.py

Unit tests for friday/llm/offline_guardian.py — OfflineGuardian.

Tests:
  - When Ollama is unavailable → deterministic fallback is returned
  - When Ollama is available but chat fails → deterministic fallback
  - When Ollama is available and works → response includes model name
  - Deterministic response includes provider status and next steps
  - Key health analysis correctly categorizes keys
"""

from unittest.mock import patch

import pytest

from friday.llm.offline_guardian import OfflineGuardian, OllamaNotAvailable
from friday.llm.router import LLMExhaustedError


@pytest.fixture()
def guardian():
    return OfflineGuardian()


# ── Ollama unavailable ─────────────────────────────────────────────────────────


def test_ollama_not_running_uses_deterministic(guardian):
    """When Ollama probe fails, deterministic response is returned."""
    with patch.object(
        guardian, "_probe_ollama", side_effect=OllamaNotAvailable("not running")
    ):
        with patch.object(
            guardian,
            "_analyze_key_health",
            return_value={
                "provider_summaries": ["  Groq: 0 healthy keys"],
                "earliest_recovery": None,
                "has_any_active": False,
            },
        ):
            response = guardian.respond(
                user_input="Hello FRIDAY",
                error=LLMExhaustedError("all exhausted"),
            )

    assert "unable to reach" in response.lower() or "unavailable" in response.lower()
    assert "Boss" in response


def test_ollama_chat_fails_falls_back_to_deterministic(guardian):
    """Ollama detected but chat endpoint fails → still get deterministic response."""
    with patch.object(guardian, "_probe_ollama", return_value=["llama3"]):
        with patch.object(
            guardian, "_stream_ollama", side_effect=OllamaNotAvailable("chat failed")
        ):
            with patch.object(
                guardian,
                "_analyze_key_health",
                return_value={
                    "provider_summaries": ["  Groq: rate-limited"],
                    "earliest_recovery": None,
                    "has_any_active": False,
                },
            ):
                response = guardian.respond(
                    user_input="What's the time?",
                    error=LLMExhaustedError("all exhausted"),
                )

    assert "Boss" in response


# ── Ollama available and working ───────────────────────────────────────────────


def test_ollama_available_returns_local_response(guardian):
    """When Ollama works, response includes the local model indicator."""
    with patch.object(guardian, "_probe_ollama", return_value=["llama3"]):
        with patch.object(
            guardian, "_stream_ollama", return_value="Hello Boss, how can I help?"
        ):
            response = guardian.respond(
                user_input="Hello",
                error=LLMExhaustedError("cloud exhausted"),
            )

    assert "Ollama" in response or "llama" in response.lower()
    assert "Hello Boss" in response


def test_ollama_model_selection_prefers_quality_order(guardian):
    """Model selection should prefer llama3.3 over tinyllama."""
    available = ["tinyllama", "phi3", "llama3.3", "gemma"]
    best = guardian._pick_ollama_model(available)
    assert best == "llama3.3"


def test_ollama_model_selection_falls_back_to_first(guardian):
    """If no preferred model is available, use the first one."""
    available = ["custom-model-xyz"]
    best = guardian._pick_ollama_model(available)
    assert best == "custom-model-xyz"


# ── Deterministic response content ────────────────────────────────────────────


def test_deterministic_response_includes_provider_status(guardian):
    health = {
        "provider_summaries": [
            "  Groq: 1 key(s) rate-limited — recovers in ~10 min",
            "  Anthropic: 1 key(s) have auth errors",
        ],
        "earliest_recovery": None,
        "has_any_active": False,
    }
    with patch.object(
        guardian, "_probe_ollama", side_effect=OllamaNotAvailable("not running")
    ):
        with patch.object(guardian, "_analyze_key_health", return_value=health):
            response = guardian.respond(
                user_input="Can you help me?",
                error=LLMExhaustedError("test"),
            )

    assert "Groq" in response
    assert "Anthropic" in response


def test_deterministic_response_includes_next_steps(guardian):
    with patch.object(
        guardian, "_probe_ollama", side_effect=OllamaNotAvailable("not running")
    ):
        with patch.object(
            guardian,
            "_analyze_key_health",
            return_value={
                "provider_summaries": ["  test: no keys"],
                "earliest_recovery": None,
                "has_any_active": False,
            },
        ):
            response = guardian.respond(
                user_input="help",
                error=LLMExhaustedError("test"),
            )

    # Should mention how to fix the situation
    assert any(
        word in response.lower() for word in ["add", "key", "ollama", "retry", "wait"]
    )


def test_deterministic_response_echoes_user_input(guardian):
    user_msg = "What is the capital of France?"
    with patch.object(
        guardian, "_probe_ollama", side_effect=OllamaNotAvailable("not running")
    ):
        with patch.object(
            guardian,
            "_analyze_key_health",
            return_value={
                "provider_summaries": [],
                "earliest_recovery": None,
                "has_any_active": False,
            },
        ):
            response = guardian.respond(
                user_input=user_msg,
                error=LLMExhaustedError("test"),
            )

    assert "What is the capital of France?" in response


def test_deterministic_response_handles_empty_user_input(guardian):
    """Empty user_input (tool re-entry loop) should not crash."""
    with patch.object(
        guardian, "_probe_ollama", side_effect=OllamaNotAvailable("not running")
    ):
        with patch.object(
            guardian,
            "_analyze_key_health",
            return_value={
                "provider_summaries": [],
                "earliest_recovery": None,
                "has_any_active": False,
            },
        ):
            response = guardian.respond(
                user_input="",
                error=LLMExhaustedError("test"),
            )

    assert isinstance(response, str) and len(response) > 0
