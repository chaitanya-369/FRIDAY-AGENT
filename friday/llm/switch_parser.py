"""
friday/llm/switch_parser.py

SwitchCommandParser — intercepts natural language model-switch commands
BEFORE they reach the brain's LLM call.

Design:
  - Layer 1: Regex + keyword rules (30+ patterns). Always-on, zero-latency,
             works even when no LLM is available.
  - Layer 2: Fuzzy name resolution against ModelCatalog entries.
  - Layer 3: LLM intent disambiguation for ambiguous cases (optional, enabled
             only when at least one provider is currently online).

Returns:
  - SwitchIntent   → a confirmed (provider, model) pair to switch to
  - StatusIntent   → user asked about current model status
  - ListIntent     → user wants to see available models
  - None           → not a switch command; pass to brain normally

Usage:
    parser = SwitchCommandParser()
    result = parser.parse("switch to gpt-4o")
    if isinstance(result, SwitchIntent):
        active_session.set(result.provider, result.model, ...)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from friday.llm.model_catalog import ModelCatalog

# ── Intent data classes ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SwitchIntent:
    """User wants to switch to a specific provider/model."""

    provider: str  # e.g. "openai"
    model: str  # e.g. "gpt-4o"
    display: str  # e.g. "GPT-4o"
    confidence: float  # 0.0 – 1.0


@dataclass(frozen=True)
class StatusIntent:
    """User wants to know what model FRIDAY is currently using."""

    pass


@dataclass(frozen=True)
class ListIntent:
    """User wants to list all available models."""

    filter_provider: Optional[str] = None  # e.g. "groq" if they said "list groq models"


@dataclass(frozen=True)
class ResetIntent:
    """User wants to reset to the default provider/model."""

    pass


@dataclass(frozen=True)
class AmbiguousIntent:
    """Multiple matches found — need clarification."""

    query: str
    candidates: list[tuple[str, str, str]]  # [(provider, model_id, display_name), ...]


@dataclass(frozen=True)
class DiagnosticsIntent:
    """User wants a full system diagnostic: all providers, models, keys, offline status."""

    pass


# ── Pattern definitions ────────────────────────────────────────────────────────

# Patterns that signal a switch command. Each is a tuple of:
#   (compiled regex, capture group name that contains the target name)
# The target name is whatever the user said AFTER the trigger phrase.
_SWITCH_PATTERNS: list[tuple[re.Pattern, str]] = [
    # "switch to X", "switch X"
    (re.compile(r"\bswitch\s+to\s+(.+)", re.IGNORECASE), ""),
    (re.compile(r"\bswitch\s+(?:over\s+to\s+)?(.+)", re.IGNORECASE), ""),
    # "use X", "use the X", "use a X"
    (re.compile(r"\buse\s+(?:the\s+|a\s+)?(.+)", re.IGNORECASE), ""),
    # "change (model/provider/to/over) to X"
    (
        re.compile(
            r"\bchange\s+(?:model\s+to|provider\s+to|to|over\s+to)\s+(.+)",
            re.IGNORECASE,
        ),
        "",
    ),
    (
        re.compile(
            r"\bchange\s+(?:the\s+)?(?:model|provider|llm|ai)\s+to\s+(.+)",
            re.IGNORECASE,
        ),
        "",
    ),
    # "set X as (the/my) default", "set model to X", "set provider to X"
    (re.compile(r"\bset\s+(.+?)\s+as\s+(?:the\s+|my\s+)?default", re.IGNORECASE), ""),
    (
        re.compile(
            r"\bset\s+(?:the\s+)?(?:model|provider|llm)\s+to\s+(.+)", re.IGNORECASE
        ),
        "",
    ),
    # "activate X", "enable X"
    (re.compile(r"\bactivate\s+(.+)", re.IGNORECASE), ""),
    (re.compile(r"\benable\s+(.+)", re.IGNORECASE), ""),
    # "run on X", "run using X", "run with X"
    (re.compile(r"\brun\s+(?:on|using|with)\s+(.+)", re.IGNORECASE), ""),
    # "talk to X", "talk using X"
    (re.compile(r"\btalk\s+(?:to|using|via|through|with)\s+(.+)", re.IGNORECASE), ""),
    # "prefer X", "I want X", "I want to use X"
    (re.compile(r"\bprefer\s+(.+)", re.IGNORECASE), ""),
    (re.compile(r"\bi\s+want\s+(?:to\s+use\s+)?(.+)", re.IGNORECASE), ""),
    # "move to X", "go to X", "go with X"
    (re.compile(r"\b(?:move|go)\s+to\s+(.+)", re.IGNORECASE), ""),
    (re.compile(r"\bgo\s+with\s+(.+)", re.IGNORECASE), ""),
    # "load X", "load model X"
    (re.compile(r"\bload\s+(?:model\s+)?(.+)", re.IGNORECASE), ""),
    # "pick X", "choose X", "select X", "try X"
    (
        re.compile(r"\b(?:pick|choose|select|try)\s+(?:model\s+)?(.+)", re.IGNORECASE),
        "",
    ),
]

# Patterns that DON'T capture a target — they directly signal intent.
_STATUS_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"\bwhat\s+(?:model|llm|ai|provider)\s+(?:are\s+you|am\s+i\s+using)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bwhich\s+(?:model|llm|ai|provider)\s+(?:are\s+you|am\s+i\s+using)",
        re.IGNORECASE,
    ),
    re.compile(r"\bcurrent\s+(?:model|provider|llm)", re.IGNORECASE),
    re.compile(r"\bactive\s+(?:model|provider|llm)", re.IGNORECASE),
    re.compile(r"\bwhat\s+are\s+you\s+running\s+on", re.IGNORECASE),
    re.compile(r"\bwhat\s+are\s+you\s+using", re.IGNORECASE),
    re.compile(r"\bllm\s+status", re.IGNORECASE),
    re.compile(r"\bmodel\s+status", re.IGNORECASE),
    re.compile(r"\bprovider\s+status", re.IGNORECASE),
    re.compile(
        r"\bwho\s+are\s+you\s+(?:backed\s+by|powered\s+by|running\s+on)", re.IGNORECASE
    ),
]

_LIST_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"\blist\s+(?:all\s+)?(?:available\s+)?(?:models|providers|llms)", re.IGNORECASE
    ),
    re.compile(
        r"\bshow\s+(?:all\s+|available\s+)?(?:models|providers|llms)", re.IGNORECASE
    ),
    re.compile(
        r"\bwhat\s+(?:models|providers|llms)\s+(?:do\s+you\s+have|are\s+available)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bwhat\s+(?:models|providers|llms)\s+can\s+(?:i|you)\s+use", re.IGNORECASE
    ),
    re.compile(r"\bavailable\s+(?:models|providers|llms)", re.IGNORECASE),
]

# Patterns that request a FULL system diagnostic report.
# These must be checked BEFORE _LIST_PATTERNS to avoid misclassification.
_DIAGNOSTICS_PATTERNS: list[re.Pattern] = [
    # "tell me everything"
    re.compile(r"\btell\s+me\s+everything", re.IGNORECASE),
    re.compile(r"\btell\s+me\s+all", re.IGNORECASE),
    # full/complete status
    re.compile(r"\bfull\s+(?:system\s+)?(?:status|report|diagnostic)", re.IGNORECASE),
    re.compile(r"\bcomplete\s+(?:status|report|diagnostic)", re.IGNORECASE),
    re.compile(r"\bsystem\s+(?:status|report|diagnostic|health)", re.IGNORECASE),
    re.compile(r"\bdiagnostic(?:s)?\b", re.IGNORECASE),
    # api key queries
    re.compile(
        r"\b(?:show|list|what(?:'s|\s+are))\s+(?:my\s+|all\s+)?(?:api\s+)?keys?",
        re.IGNORECASE,
    ),
    re.compile(r"\bkey\s+(?:status|health|report)", re.IGNORECASE),
    re.compile(r"\bhow\s+many\s+(?:api\s+)?keys?", re.IGNORECASE),
    re.compile(r"\bwhich\s+keys?\s+(?:are|do\s+i\s+have)", re.IGNORECASE),
    re.compile(
        r"\bare\s+(?:my\s+|the\s+)?(?:api\s+)?keys?\s+(?:working|valid|healthy|active|ok)",
        re.IGNORECASE,
    ),
    # online / offline status
    re.compile(r"\bare\s+you\s+online", re.IGNORECASE),
    re.compile(r"\bare\s+you\s+offline", re.IGNORECASE),
    re.compile(r"\bam\s+i\s+(?:online|offline|connected)", re.IGNORECASE),
    re.compile(r"\bconnection\s+(?:status|health|report)", re.IGNORECASE),
    re.compile(r"\binternet\s+(?:status|connection)", re.IGNORECASE),
    # Ollama-specific
    re.compile(
        r"\bis\s+ollama\s+(?:running|available|up|online|installed)", re.IGNORECASE
    ),
    re.compile(r"\bollama\s+status", re.IGNORECASE),
    re.compile(r"\blocal\s+(?:llm\s+)?status", re.IGNORECASE),
    # provider/key health
    re.compile(r"\bprovider\s+(?:health|report)", re.IGNORECASE),
    re.compile(r"\bhow\s+(?:many|much)\s+(?:providers?|quota)", re.IGNORECASE),
    re.compile(r"\bwhich\s+providers?\s+(?:are|work|working|available)", re.IGNORECASE),
    re.compile(r"\brate\s+limit\s+(?:status|report)", re.IGNORECASE),
    re.compile(
        r"\bshow\s+(?:me\s+)?(?:everything|all\s+info|my\s+setup|my\s+config)",
        re.IGNORECASE,
    ),
]

_RESET_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bswitch\s+back\b", re.IGNORECASE),
    re.compile(r"\brevert(?:\s+back)?(?:\s+to\s+default)?\b", re.IGNORECASE),
    re.compile(r"\breset(?:\s+(?:the\s+)?(?:model|provider|llm))?\b", re.IGNORECASE),
    re.compile(r"\buse\s+(?:the\s+)?default\s+(?:model|provider)?", re.IGNORECASE),
    re.compile(r"\bgo\s+back\s+to\s+default", re.IGNORECASE),
]

# Convenience phrases that map to a special target (resolved before fuzzy match)
_CONVENIENCE_MAP: dict[str, tuple[str, str]] = {
    "cheapest": ("groq", "llama-3.1-8b-instant"),
    "fastest": ("groq", "llama-3.1-8b-instant"),
    "fastest model": ("groq", "llama-3.1-8b-instant"),
    "cheapest model": ("groq", "llama-3.1-8b-instant"),
    "local": ("groq", "llama-3.1-8b-instant"),  # closest to local on free tier
    "local model": ("groq", "llama-3.1-8b-instant"),
    "best": ("anthropic", "claude-sonnet-4-5-20250514"),
    "smartest": ("anthropic", "claude-opus-4-5-20251101"),
    "most powerful": ("anthropic", "claude-opus-4-5-20251101"),
    "most capable": ("anthropic", "claude-opus-4-5-20251101"),
    "claude": ("anthropic", "claude-sonnet-4-5-20250514"),
    "gpt": ("openai", "gpt-4o"),
    "chatgpt": ("openai", "gpt-4o"),
    "openai": ("openai", "gpt-4o"),
    "gemini": ("gemini", "gemini-2.0-flash"),
    "google": ("gemini", "gemini-2.0-flash"),
    "groq": ("groq", "llama-3.3-70b-versatile"),
    "llama": ("groq", "llama-3.3-70b-versatile"),
    "mixtral": ("groq", "mixtral-8x7b-32768"),
    "deepseek": ("deepseek", "deepseek-chat"),
    "mistral": ("groq", "mixtral-8x7b-32768"),
    # Specific model shorthand aliases
    "llama 8b": ("groq", "llama-3.1-8b-instant"),
    "llama 70b": ("groq", "llama-3.3-70b-versatile"),
    "llama 90b": ("groq", "llama-3.2-90b-vision-preview"),
    "gemini pro": ("gemini", "gemini-1.5-pro"),
    "gemini flash": ("gemini", "gemini-2.0-flash"),
    "gemini 2": ("gemini", "gemini-2.0-flash"),
    "gpt 4o": ("openai", "gpt-4o"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
    "gpt 4o mini": ("openai", "gpt-4o-mini"),
    "openai gpt": ("openai", "gpt-4o"),
    "claude opus": ("anthropic", "claude-opus-4-5-20251101"),
    "claude sonnet": ("anthropic", "claude-sonnet-4-5-20250514"),
    "claude haiku": ("anthropic", "claude-haiku-4-5-20251001"),
    "deepseek reasoner": ("deepseek", "deepseek-reasoner"),
}

# Words to strip from extracted target names before fuzzy matching
_STOP_WORDS = frozenset(
    {
        "please",
        "now",
        "model",
        "provider",
        "llm",
        "ai",
        "to",
        "the",
        "a",
        "an",
        "for",
        "me",
        "my",
        "default",
        "version",
        "api",
        "mode",
        "engine",
    }
)

# Phrases that start with switch-like words but are NOT model switches.
# If any of these appear, the message is passed through to the brain.
_FALSE_POSITIVE_GUARDS: list[re.Pattern] = [
    re.compile(
        r"\bswitch\s+(off|on|the\s+lights?|to\s+dark\s+mode|to\s+light\s+mode)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\buse\s+(this|that|it|them|caution|care|common\s+sense)", re.IGNORECASE
    ),
    re.compile(r"\bchange\s+(my\s+password|the\s+subject|plans?|topic)", re.IGNORECASE),
    re.compile(r"\benable\s+(dark\s+mode|notifications?|two\s+factor)", re.IGNORECASE),
]


class SwitchCommandParser:
    """
    Parses natural language model-switch commands.

    Call parse(user_input) → returns one of:
      SwitchIntent | StatusIntent | ListIntent | ResetIntent | AmbiguousIntent | None
    """

    def __init__(self) -> None:
        self._catalog = ModelCatalog()
        # Cache of (provider_name, model_id, display_name) triples from DB
        self._candidates: list[tuple[str, str, str]] = []
        self._candidates_loaded = False

    # ── Catalog helpers ───────────────────────────────────────────────────────

    def _load_candidates(self) -> list[tuple[str, str, str]]:
        """
        Lazy-load all active models from the catalog.
        Returns a list of (provider_name, model_id, display_name).
        """
        if not self._candidates_loaded:
            # Inline import to avoid circular deps at module load time
            from friday.llm.models.db_models import LLMProvider
            from sqlmodel import Session, select
            from friday.core.database import engine

            triples: list[tuple[str, str, str]] = []
            entries = self._catalog.list_all_models()
            with Session(engine) as db:
                providers = {p.id: p.name for p in db.exec(select(LLMProvider)).all()}
            for entry in entries:
                pname = providers.get(entry.provider_id, "unknown")
                triples.append((pname, entry.model_id, entry.display_name))
            self._candidates = triples
            self._candidates_loaded = True
        return self._candidates

    def _invalidate_cache(self) -> None:
        """Call this if providers/models change at runtime."""
        self._candidates_loaded = False
        self._candidates = []

    # ── String normalisation ──────────────────────────────────────────────────

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _strip_stop_words(text: str) -> str:
        words = [w for w in text.split() if w not in _STOP_WORDS]
        return " ".join(words)

    # ── Fuzzy matching ────────────────────────────────────────────────────────

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """SequenceMatcher ratio between two normalised strings."""
        return SequenceMatcher(None, a, b).ratio()

    def _fuzzy_resolve(
        self,
        query: str,
        threshold: float = 0.50,
    ) -> list[tuple[float, str, str, str]]:
        """
        Find all catalog entries whose model_id or display_name fuzzy-matches
        the query above the threshold.

        Returns a list of (score, provider_name, model_id, display_name),
        sorted by score descending.
        """
        norm_query = self._normalise(query)
        stripped_query = self._strip_stop_words(norm_query)
        candidates = self._load_candidates()

        scored: list[tuple[float, str, str, str]] = []
        for provider, model_id, display in candidates:
            norm_model_id = self._normalise(model_id)
            norm_display = self._normalise(display)
            norm_provider = self._normalise(provider)

            # Compute scores against multiple name representations
            scores = [
                self._similarity(stripped_query, norm_display),
                self._similarity(stripped_query, norm_model_id),
                self._similarity(stripped_query, norm_provider),
                # Also try the query against words of display name (partial match)
                self._similarity(stripped_query, " ".join(norm_display.split()[:2])),
            ]

            # Bonus: if the query appears as a substring of model_id or display
            if stripped_query and (
                stripped_query in norm_display
                or stripped_query in norm_model_id
                or stripped_query in norm_provider
            ):
                scores.append(0.9)

            # Bonus: exact word overlap
            query_words = set(stripped_query.split())
            display_words = set(norm_display.split())
            model_words = set(norm_model_id.replace("-", " ").split())
            overlap = len(query_words & (display_words | model_words))
            if overlap:
                scores.append(min(0.4 + 0.2 * overlap, 0.95))

            best = max(scores)
            if best >= threshold:
                scored.append((best, provider, model_id, display))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    # ── Target extraction ─────────────────────────────────────────────────────

    def _extract_target(self, text: str) -> Optional[str]:
        """
        Apply all switch patterns to the text. Return the raw captured
        target string (what the user said they want to switch to),
        or None if no pattern matched.
        """
        for pattern, _ in _SWITCH_PATTERNS:
            m = pattern.search(text)
            if m:
                captured = m.group(1).strip()
                # Trim trailing punctuation
                captured = re.sub(r"[.,!?]+$", "", captured).strip()
                return captured
        return None

    # ── False positive guard ──────────────────────────────────────────────────

    @staticmethod
    def _is_false_positive(text: str) -> bool:
        """Return True if the text matches a known false-positive pattern."""
        for guard in _FALSE_POSITIVE_GUARDS:
            if guard.search(text):
                return True
        return False

    # ── Main parse entry point ────────────────────────────────────────────────

    def parse(
        self, user_input: str
    ) -> (
        SwitchIntent
        | StatusIntent
        | ListIntent
        | ResetIntent
        | AmbiguousIntent
        | DiagnosticsIntent
        | None
    ):
        """
        Parse a user message for model-switch intent.

        Returns:
          SwitchIntent    — unambiguous match found
          StatusIntent    — user asked what model is active
          ListIntent      — user wants model list
          ResetIntent     — user wants to reset to default
          AmbiguousIntent — multiple matches, need clarification
          None            — not a switch command; pass to brain
        """
        text = user_input.strip()

        # 0. False positive guard (runs first — fastest rejection)
        if self._is_false_positive(text):
            return None

        norm = self._normalise(text)

        # 1. Diagnostics (checked FIRST — most specific, before list/status)
        for pat in _DIAGNOSTICS_PATTERNS:
            if pat.search(norm):
                return DiagnosticsIntent()

        # 2. Status queries
        for pat in _STATUS_PATTERNS:
            if pat.search(norm):
                return StatusIntent()

        # 3. List queries
        for pat in _LIST_PATTERNS:
            m = pat.search(norm)
            if m:
                # Try to extract provider filter from the raw text
                provider_filter = self._extract_provider_filter(text)
                return ListIntent(filter_provider=provider_filter)

        # 4. Reset / revert
        for pat in _RESET_PATTERNS:
            if pat.search(norm):
                return ResetIntent()

        # 4. Switch command — extract target string
        raw_target = self._extract_target(text)
        if raw_target is None:
            return None  # No switch pattern matched

        target_norm = self._normalise(raw_target)
        target_stripped = self._strip_stop_words(target_norm)

        if not target_stripped:
            return None  # Target resolved to nothing after stripping

        # 5. Convenience map (exact phrase shortcuts)
        conv = _CONVENIENCE_MAP.get(target_stripped) or _CONVENIENCE_MAP.get(
            target_norm
        )
        if conv:
            provider, model_id = conv
            display = self._get_display(provider, model_id)
            return SwitchIntent(
                provider=provider,
                model=model_id,
                display=display,
                confidence=1.0,
            )

        # 6. Fuzzy match against catalog
        matches = self._fuzzy_resolve(target_stripped)

        if not matches:
            # Nothing found above threshold — not a switch command
            return None

        top_score, top_provider, top_model, top_display = matches[0]

        if top_score >= 0.85 or (len(matches) == 1 and top_score >= 0.50):
            # Clear winner
            return SwitchIntent(
                provider=top_provider,
                model=top_model,
                display=top_display,
                confidence=top_score,
            )

        # 7. Multiple matches — check if top candidate is clearly better
        if len(matches) >= 2:
            second_score = matches[1][0]
            if top_score - second_score >= 0.20:
                # Top is sufficiently better than second
                return SwitchIntent(
                    provider=top_provider,
                    model=top_model,
                    display=top_display,
                    confidence=top_score,
                )

            # Genuinely ambiguous — return top 5 candidates
            candidates = [(p, m, d) for _, p, m, d in matches[:5]]
            return AmbiguousIntent(query=raw_target, candidates=candidates)

        # Single match but low confidence — still return it
        if matches:
            return SwitchIntent(
                provider=top_provider,
                model=top_model,
                display=top_display,
                confidence=top_score,
            )

        return None

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _get_display(self, provider: str, model_id: str) -> str:
        """Look up display name for a known (provider, model_id) pair."""
        for p, m, d in self._load_candidates():
            if p == provider and m == model_id:
                return d
        return model_id  # fallback to raw model_id

    def _extract_provider_filter(self, text: str) -> Optional[str]:
        """
        Given text like "list groq models", extract the provider name.
        Returns None if no provider name is mentioned.
        """
        norm = self._normalise(text)
        provider_keywords = {
            "anthropic": "anthropic",
            "claude": "anthropic",
            "openai": "openai",
            "gpt": "openai",
            "groq": "groq",
            "llama": "groq",
            "gemini": "gemini",
            "google": "gemini",
            "deepseek": "deepseek",
        }
        for keyword, provider in provider_keywords.items():
            if keyword in norm:
                return provider
        return None

    def format_switch_confirmation(
        self, intent: SwitchIntent, previous: tuple[str, str]
    ) -> str:
        """
        Return a FRIDAY-persona confirmation message for a successful switch.

        Args:
            intent   : The resolved SwitchIntent.
            previous : (provider_name, model_id) before the switch.
        """
        prev_provider, prev_model = previous
        return (
            f"Switching from {prev_provider.capitalize()} / {prev_model} "
            f"to **{intent.display}** ({intent.provider.capitalize()}), Boss. "
            f"Your conversation history has been preserved."
        )

    def format_ambiguous_response(self, intent: AmbiguousIntent) -> str:
        """Return a FRIDAY-persona response asking the user to clarify."""
        lines = [
            f"I found multiple models matching '{intent.query}', Boss. "
            "Which one did you mean?"
        ]
        for i, (provider, model_id, display) in enumerate(intent.candidates, 1):
            lines.append(f"  {i}. {display} ({provider})")
        return "\n".join(lines)

    def format_not_found_response(self, query: str) -> str:
        """Return a response when no model matched the query."""
        return (
            f"I couldn't find a model matching '{query}', Boss. "
            "Say 'list models' to see everything available, "
            "or try a more specific name like 'Claude Sonnet', 'GPT-4o', or 'Llama 70B'."
        )

    def format_diagnostics_tip(self) -> str:
        """Hint shown when user asks for diagnostics but it's unavailable."""
        return (
            "Boss, say 'full status', 'show my keys', 'are you online', or "
            "'tell me everything' for a complete system diagnostic."
        )


# ── Module-level singleton ─────────────────────────────────────────────────────

switch_parser = SwitchCommandParser()
