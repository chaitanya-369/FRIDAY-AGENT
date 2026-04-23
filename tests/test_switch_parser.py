"""
tests/test_switch_parser.py

Parametrized tests for friday/llm/switch_parser.py — SwitchCommandParser.

Tests:
  - 25+ natural language switch phrases all resolve correctly
  - Status query phrases return StatusIntent
  - List query phrases return ListIntent
  - Reset phrases return ResetIntent
  - Ambiguous cases return AmbiguousIntent or SwitchIntent
  - False positives pass through as None
  - Convenience aliases (fastest, cheapest, claude, gpt, etc.)
"""

import pytest

from friday.llm.switch_parser import (
    SwitchCommandParser,
    SwitchIntent,
    StatusIntent,
    ListIntent,
    ResetIntent,
    AmbiguousIntent,
)


@pytest.fixture(scope="module")
def parser():
    return SwitchCommandParser()


# ── Switch command phrases ─────────────────────────────────────────────────────

SWITCH_PHRASES = [
    # Explicit model names
    ("switch to gpt-4o", "openai", "gpt-4o"),
    ("switch to GPT-4o", "openai", "gpt-4o"),
    ("use gpt-4o mini", "openai", "gpt-4o-mini"),
    ("change model to claude sonnet", "anthropic", "claude-sonnet-4-5-20250514"),
    ("change to claude haiku", "anthropic", "claude-haiku-4-5-20251001"),
    ("set model to llama 3.3", "groq", "llama-3.3-70b-versatile"),
    ("activate deepseek chat", "deepseek", "deepseek-chat"),
    ("run on gemini 2.0 flash", "gemini", "gemini-2.0-flash"),
    ("enable openai", "openai", "gpt-4o"),
    ("load gemini flash", "gemini", "gemini-2.0-flash"),
    ("pick llama", "groq", "llama-3.3-70b-versatile"),
    ("choose mixtral", "groq", "mixtral-8x7b-32768"),
    ("go with groq", "groq", "llama-3.3-70b-versatile"),
    (
        "move to anthropic",
        "anthropic",
        "claude-opus-4-5-20251101",
    ),  # first catalog entry
    ("I want to use deepseek", "deepseek", "deepseek-chat"),
    ("prefer claude opus", "anthropic", "claude-opus-4-5-20251101"),
    ("talk to openai gpt", "openai", "gpt-4o"),  # hits convenience alias 'openai gpt'
    (
        "try gemini pro",
        "gemini",
        "gemini-1.5-pro",
    ),  # hits convenience alias 'gemini pro'
    (
        "select llama 8b",
        "groq",
        "llama-3.1-8b-instant",
    ),  # hits convenience alias 'llama 8b'
    ("use the claude model", "anthropic", "claude-sonnet-4-5-20250514"),
]


@pytest.mark.parametrize("phrase,expected_provider,expected_model", SWITCH_PHRASES)
def test_switch_phrase(parser, phrase, expected_provider, expected_model):
    result = parser.parse(phrase)
    assert isinstance(
        result, SwitchIntent
    ), f"Expected SwitchIntent for '{phrase}', got {type(result).__name__}"
    assert (
        result.provider == expected_provider
    ), f"Provider mismatch for '{phrase}': got {result.provider}, expected {expected_provider}"
    assert (
        result.model == expected_model
    ), f"Model mismatch for '{phrase}': got {result.model}, expected {expected_model}"


# ── Convenience alias phrases ──────────────────────────────────────────────────

CONVENIENCE_PHRASES = [
    ("use the fastest model", "groq", "llama-3.1-8b-instant"),
    ("use cheapest", "groq", "llama-3.1-8b-instant"),
    ("use the best", "anthropic", "claude-sonnet-4-5-20250514"),
    ("use claude", "anthropic", "claude-sonnet-4-5-20250514"),
    ("use gpt", "openai", "gpt-4o"),
    ("use chatgpt", "openai", "gpt-4o"),
    ("use gemini", "gemini", "gemini-2.0-flash"),
    ("use groq", "groq", "llama-3.3-70b-versatile"),
    ("use deepseek", "deepseek", "deepseek-chat"),
    ("use llama", "groq", "llama-3.3-70b-versatile"),
    ("use mixtral", "groq", "mixtral-8x7b-32768"),
]


@pytest.mark.parametrize("phrase,expected_provider,expected_model", CONVENIENCE_PHRASES)
def test_convenience_alias(parser, phrase, expected_provider, expected_model):
    result = parser.parse(phrase)
    assert isinstance(
        result, SwitchIntent
    ), f"Expected SwitchIntent for convenience phrase '{phrase}', got {type(result).__name__}"
    assert result.provider == expected_provider
    assert result.model == expected_model


# ── Status intent phrases ──────────────────────────────────────────────────────

STATUS_PHRASES = [
    "what model are you using",
    "which model are you using",
    "current model",
    "active model",
    "what are you running on",
    "what are you using",
    "llm status",
    "model status",
    "provider status",
    "who are you powered by",
]


@pytest.mark.parametrize("phrase", STATUS_PHRASES)
def test_status_phrase(parser, phrase):
    result = parser.parse(phrase)
    assert isinstance(
        result, StatusIntent
    ), f"Expected StatusIntent for '{phrase}', got {type(result).__name__}"


# ── List intent phrases ────────────────────────────────────────────────────────

LIST_PHRASES = [
    "list all models",
    "list models",
    "show available models",
    "what models do you have",
    "what llms can I use",
    "available providers",
]


@pytest.mark.parametrize("phrase", LIST_PHRASES)
def test_list_phrase(parser, phrase):
    result = parser.parse(phrase)
    assert isinstance(
        result, ListIntent
    ), f"Expected ListIntent for '{phrase}', got {type(result).__name__}"


# ── Reset intent phrases ───────────────────────────────────────────────────────

RESET_PHRASES = [
    "switch back",
    "revert",
    "reset",
    "use the default model",
    "go back to default",
    "reset the model",
]


@pytest.mark.parametrize("phrase", RESET_PHRASES)
def test_reset_phrase(parser, phrase):
    result = parser.parse(phrase)
    assert isinstance(
        result, ResetIntent
    ), f"Expected ResetIntent for '{phrase}', got {type(result).__name__}"


# ── False positives — should return None ──────────────────────────────────────

FALSE_POSITIVES = [
    "what's the weather today",
    "search for the best Python tutorials",
    "hey FRIDAY what time is it",
    "can you help me with my code",
    "switch off the lights",
    "use caution when deleting files",
    "change the subject please",
    "enable dark mode",
    "I want a coffee",
    "tell me a joke",
]


@pytest.mark.parametrize("phrase", FALSE_POSITIVES)
def test_false_positive_passes_through(parser, phrase):
    result = parser.parse(phrase)
    assert (
        result is None
    ), f"Expected None (pass-through) for '{phrase}', got {type(result).__name__}: {result}"


# ── Confidence scores ─────────────────────────────────────────────────────────


def test_confidence_is_between_zero_and_one(parser):
    result = parser.parse("switch to gpt-4o")
    assert isinstance(result, SwitchIntent)
    assert 0.0 <= result.confidence <= 1.0


def test_exact_convenience_has_full_confidence(parser):
    result = parser.parse("use claude")
    assert isinstance(result, SwitchIntent)
    assert result.confidence == 1.0


# ── Format helpers ────────────────────────────────────────────────────────────


def test_format_switch_confirmation(parser):
    intent = SwitchIntent(
        provider="openai", model="gpt-4o", display="GPT-4o", confidence=1.0
    )
    msg = parser.format_switch_confirmation(intent, ("groq", "llama-3.3-70b-versatile"))
    assert "GPT-4o" in msg
    assert "Boss" in msg


def test_format_ambiguous_response(parser):
    intent = AmbiguousIntent(
        query="claude",
        candidates=[("anthropic", "claude-sonnet-4-5-20250514", "Claude Sonnet 4.5")],
    )
    msg = parser.format_ambiguous_response(intent)
    assert "claude" in msg.lower()
    assert "Boss" in msg


def test_format_not_found_response(parser):
    msg = parser.format_not_found_response("quantum llm turbo 9000")
    assert "quantum llm turbo 9000" in msg
    assert "Boss" in msg
