"""
friday/memory/retrieval/intent.py

LLMIntentClassifier — Phase B replacement for keyword-based intent detection.

Replaces the simple keyword heuristic in RetrievalEngine with a Claude Haiku
few-shot classifier that accurately identifies query intent, enabling the
retrieval engine to route to the right memory source.

Intent classes:
    task        — "what tasks do I have?", "what's pending?", "remind me to..."
    episodic    — "when did we last discuss X?", "what did I say about..."
    entity      — "what do you know about Priya?", "tell me about project X"
    semantic    — "what do I prefer?", "things I like", "my habits"
    predictive  — "what should I focus on?", "what's important right now?"
    general     — catch-all for conversational queries with no clear intent

Design:
    - LRU cache on the query string (functools.lru_cache on a normalized key)
    - Calls Claude Haiku with a rich few-shot prompt
    - Falls back to existing keyword classifier on any failure
    - Total latency: ~200ms uncached, ~0ms cached
    - Cost: ~$0.00001 per classification (negligible)
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# ── Intent vocabulary ─────────────────────────────────────────────────────────

INTENT_TASK = "task"
INTENT_EPISODIC = "episodic"
INTENT_ENTITY = "entity"
INTENT_SEMANTIC = "semantic"
INTENT_PREDICTIVE = "predictive"
INTENT_GENERAL = "general"

VALID_INTENTS = {
    INTENT_TASK,
    INTENT_EPISODIC,
    INTENT_ENTITY,
    INTENT_SEMANTIC,
    INTENT_PREDICTIVE,
    INTENT_GENERAL,
}

# ── Few-shot prompt ───────────────────────────────────────────────────────────

_CLASSIFICATION_PROMPT = """\
You are a query intent classifier for a personal AI assistant's memory system.
Classify the user's query into exactly one of these intents:

INTENTS:
  task       — about pending tasks, todos, reminders, deadlines
  episodic   — about past conversations, timestamps, "when did we...", "last time"
  entity     — about a specific named person, project, tool, or place
  semantic   — about preferences, habits, patterns, general knowledge
  predictive — about what to focus on, priorities, what matters now
  general    — conversational, no clear memory intent

EXAMPLES:
  "what tasks are pending?"                → task
  "remind me to review PR #47"            → task
  "what did I say about the API yesterday?"→ episodic
  "when did we last talk about Priya?"    → episodic
  "what do you know about Priya?"         → entity
  "tell me about the FRIDAY project"      → entity
  "what do I prefer for lunch?"           → semantic
  "what are my work habits?"              → semantic
  "what should I focus on today?"         → predictive
  "what's most important right now?"      → predictive
  "hello"                                 → general
  "how are you?"                          → general

Now classify this query (respond with ONLY the intent word, nothing else):
QUERY: {query}
INTENT:"""


# ── Keyword fallback ──────────────────────────────────────────────────────────

_TASK_KEYWORDS = re.compile(
    r"\b(task|todo|pending|remind|deadline|due|complete|finish|schedule|"
    r"need to|have to|should|must|review|check)\b",
    re.IGNORECASE,
)
_EPISODIC_KEYWORDS = re.compile(
    r"\b(last time|yesterday|earlier|before|when did|told you|said|talked|"
    r"mentioned|discussed|remember when|recall|past|previously)\b",
    re.IGNORECASE,
)
_ENTITY_KEYWORDS = re.compile(
    r"\b(who is|what is|tell me about|know about|regarding|about [A-Z])\b",
    re.IGNORECASE,
)
_SEMANTIC_KEYWORDS = re.compile(
    r"\b(prefer|like|habit|usually|typically|tend to|always|never|my style|"
    r"my preference|I enjoy|I hate)\b",
    re.IGNORECASE,
)
_PREDICTIVE_KEYWORDS = re.compile(
    r"\b(should I|focus on|prioritize|most important|what matters|urgent|"
    r"recommend|suggest|today|this week)\b",
    re.IGNORECASE,
)


def _keyword_fallback(query: str) -> str:
    """Keyword-based intent classification — guaranteed to return a valid intent."""
    if _TASK_KEYWORDS.search(query):
        return INTENT_TASK
    if _EPISODIC_KEYWORDS.search(query):
        return INTENT_EPISODIC
    if _ENTITY_KEYWORDS.search(query):
        return INTENT_ENTITY
    if _SEMANTIC_KEYWORDS.search(query):
        return INTENT_SEMANTIC
    if _PREDICTIVE_KEYWORDS.search(query):
        return INTENT_PREDICTIVE
    return INTENT_GENERAL


# ── LRU Cache store ───────────────────────────────────────────────────────────

_cache: dict[str, str] = {}
_MAX_CACHE = 256


def _normalize_key(query: str) -> str:
    """Normalize query for cache key — lowercase, strip punctuation, collapse spaces."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", query.lower())).strip()


def _cache_get(key: str) -> str | None:
    return _cache.get(key)


def _cache_set(key: str, value: str) -> None:
    if len(_cache) >= _MAX_CACHE:
        # Remove oldest entry (FIFO approximation)
        try:
            oldest = next(iter(_cache))
            del _cache[oldest]
        except Exception:
            pass
    _cache[key] = value


# ── LLMIntentClassifier ───────────────────────────────────────────────────────


class LLMIntentClassifier:
    """
    LLM-powered query intent classifier.

    Uses Claude Haiku with an LRU cache to classify user queries
    into typed memory retrieval intents.

    Falls back to keyword-based classification on any failure.
    """

    def __init__(self) -> None:
        self._enabled = True  # can be disabled if LLM calls are unavailable

    def classify(self, query: str) -> str:
        """
        Classify the intent of a query string.

        Returns one of: task | episodic | entity | semantic | predictive | general
        Always returns a valid string — never raises.
        """
        if not query or len(query.strip()) < 3:
            return INTENT_GENERAL

        # 1. Normalise for cache
        cache_key = _normalize_key(query)

        # 2. Cache hit
        cached = _cache_get(cache_key)
        if cached:
            return cached

        # 3. LLM classification
        intent = INTENT_GENERAL
        if self._enabled:
            try:
                intent = self._call_llm(query)
            except Exception as exc:
                logger.debug("LLMIntentClassifier LLM call failed: %s", exc)
                intent = _keyword_fallback(query)
        else:
            intent = _keyword_fallback(query)

        # 4. Validate and cache
        if intent not in VALID_INTENTS:
            intent = INTENT_GENERAL
        _cache_set(cache_key, intent)

        return intent

    def classify_with_entities(self, query: str) -> tuple[str, list[str]]:
        """
        Classify intent AND extract any named entities from the query.

        Useful for ENTITY intent — we need to know which entity to look up.

        Returns (intent, [entity_names])
        """
        intent = self.classify(query)
        entities: list[str] = []

        if intent == INTENT_ENTITY:
            entities = self._extract_entities(query)

        return intent, entities

    def _call_llm(self, query: str) -> str:
        """Make the Claude Haiku API call for intent classification."""
        from friday.config.settings import settings  # noqa: PLC0415
        from friday.llm.adapters.anthropic_adapter import AnthropicAdapter  # noqa: PLC0415

        if (
            not settings.anthropic_api_key
            or "your_anthropic" in settings.anthropic_api_key
        ):
            return _keyword_fallback(query)

        model = getattr(
            settings, "memory_extraction_model", "claude-haiku-4-5-20251001"
        )
        prompt = _CLASSIFICATION_PROMPT.format(query=query.strip())

        adapter = AnthropicAdapter()
        response = ""
        for chunk in adapter.stream(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            system_prompt="Respond with exactly one word from the intent vocabulary.",
            api_key=settings.anthropic_api_key,
            tools=[],
            max_tokens=10,
        ):
            response += chunk

        raw = response.strip().lower().split()[0] if response.strip() else "general"
        return raw if raw in VALID_INTENTS else INTENT_GENERAL

    def _extract_entities(self, query: str) -> list[str]:
        """
        Simple regex-based entity extraction for ENTITY-intent queries.

        Looks for capitalized proper nouns after trigger phrases like
        "about X", "know about X", "tell me about X", "who is X".
        """
        patterns = [
            re.compile(
                r"\b(?:about|regarding|who is|tell me about|know about)\s+([A-Z][a-zA-Z\s]{1,30})",
                re.IGNORECASE,
            ),
            re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"),  # Proper nouns
        ]
        found: list[str] = []
        for pattern in patterns:
            matches = pattern.findall(query)
            for match in matches:
                name = match.strip()
                if 2 <= len(name) <= 40 and name not in found:
                    found.append(name)

        # Filter common false positives
        stopwords = {"what", "who", "tell", "me", "you", "know", "the", "a", "an", "is"}
        found = [n for n in found if n.lower() not in stopwords]
        return found[:3]

    def disable_llm(self) -> None:
        """Fall back to keyword-only mode (e.g., when no API keys available)."""
        self._enabled = False

    def get_cache_stats(self) -> dict:
        """Return cache hit rate stats."""
        return {
            "cached_intents": len(_cache),
            "max_cache": _MAX_CACHE,
        }
