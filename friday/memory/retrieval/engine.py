"""
friday/memory/retrieval/engine.py

RetrievalEngine — multi-modal memory retrieval orchestrator.

Phase A: Two parallel search paths:
  1. Vector search (ChromaDB)  — semantic similarity
  2. SQL structured search     — tasks, recent memories, type-filtered facts

Phase B additions:
  3. Knowledge Graph path      — entity subgraph context (NetworkX)
  4. LLMIntentClassifier       — replaces keyword heuristics for intent routing

Results are merged, deduplicated, and returned as a unified ranked MemoryContext.
The caller (MemoryBus) then injects KG entity context for ENTITY-intent queries.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from friday.config.settings import settings
from friday.memory.episodic import EpisodeStore
from friday.memory.types import Memory, MemoryContext, MemoryType, Task
from friday.memory.vector_store import VectorSearchResult, VectorStore

if TYPE_CHECKING:
    from friday.memory.graph import KnowledgeGraph
    from friday.memory.retrieval.intent import LLMIntentClassifier


# ── Query intent vocabulary ───────────────────────────────────────────────────


class QueryIntent:
    """Rough classification of what the user's query needs from memory."""

    EPISODIC = "episodic"  # "what did we discuss yesterday?"
    SEMANTIC = "semantic"  # "what does Boss prefer?"
    TASK = "task"  # "what's pending?" / "what do I need to do?"
    ENTITY = "entity"  # "what do you know about Priya?"
    PREDICTIVE = "predictive"  # "what should I focus on?"
    GENERAL = "general"  # catch-all


# ── Merged result dataclass ───────────────────────────────────────────────────


@dataclass
class RetrievalResult:
    """A single memory candidate with its final combined score."""

    memory: Memory
    score: float  # final score for ranking
    source: str  # "vector" | "sql" | "graph"
    vector_similarity: float = 0.0


# ── RetrievalEngine ───────────────────────────────────────────────────────────


class RetrievalEngine:
    """
    Multi-modal retrieval: vector + SQL + Knowledge Graph (Phase B).

    Usage:
        engine = RetrievalEngine(episode_store, vector_store)
        engine.set_intent_classifier(LLMIntentClassifier())  # Phase B
        engine.set_graph(KnowledgeGraph())                   # Phase B
        ctx = engine.retrieve(query="what should I work on?")
    """

    def __init__(
        self,
        episode_store: EpisodeStore,
        vector_store: VectorStore,
    ) -> None:
        self.episode_store = episode_store
        self.vector_store = vector_store

        # Phase B — injected after construction via setters
        self._intent_classifier: Optional["LLMIntentClassifier"] = None
        self._graph: Optional["KnowledgeGraph"] = None

    # ── Phase B injection points ──────────────────────────────────────────────

    def set_intent_classifier(self, classifier: "LLMIntentClassifier") -> None:
        """Inject the LLM intent classifier (Phase B)."""
        self._intent_classifier = classifier

    def set_graph(self, graph: "KnowledgeGraph") -> None:
        """Inject the Knowledge Graph (Phase B)."""
        self._graph = graph

    # ── Main retrieval entry point ────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        *,
        intent: Optional[str] = None,
        max_facts: Optional[int] = None,
        max_preferences: Optional[int] = None,
        max_tasks: Optional[int] = None,
    ) -> MemoryContext:
        """
        Run multi-modal retrieval and return an assembled MemoryContext.

        Args:
            query:           The user's current input (used for semantic search)
            intent:          Pre-classified intent (if None, classify internally)
            max_facts:       Override settings.memory_max_facts
            max_preferences: Override settings.memory_max_preferences
            max_tasks:       Override settings.memory_max_tasks
        """
        t_start = time.perf_counter()

        _max_facts = max_facts or settings.memory_max_facts
        _max_preferences = max_preferences or settings.memory_max_preferences
        _max_tasks = max_tasks or settings.memory_max_tasks

        # Resolve intent (Phase B: use LLM classifier if available)
        resolved_intent = intent or self._classify_intent(query)

        # ── Path 1: Vector search (semantic similarity) ───────────────────────
        vector_results = self._vector_search(query, n_results=20)
        vector_by_id: dict[str, RetrievalResult] = {}
        for vr in vector_results:
            score = vr.combined_score()
            vector_by_id[vr.memory_id] = RetrievalResult(
                memory=Memory(
                    id=vr.memory_id,
                    type=vr.get_type(),
                    content=vr.content,
                    confidence=vr.get_confidence(),
                    importance=vr.get_importance(),
                    emotional_valence=vr.get_emotional_valence(),
                ),
                score=score,
                source="vector",
                vector_similarity=vr.similarity,
            )

        # ── Path 2: SQL structured retrieval ──────────────────────────────────
        sql_results = self._sql_search(query, resolved_intent)

        # ── Merge: SQL enriches or adds to vector results ─────────────────────
        merged: dict[str, RetrievalResult] = dict(vector_by_id)
        for memory in sql_results:
            if memory.id in merged:
                # Cross-path boost: found in both → more reliable
                merged[memory.id].score = min(1.0, merged[memory.id].score + 0.15)
                merged[memory.id].memory = memory  # use full object from SQL
            else:
                merged[memory.id] = RetrievalResult(
                    memory=memory,
                    score=memory.effective_score(),
                    source="sql",
                )

        # ── Path 3: Knowledge Graph entity boost (Phase B) ───────────────────
        if (
            resolved_intent == QueryIntent.ENTITY
            and self._graph
            and self._graph.is_available()
        ):
            try:
                # Find entity-linked memories and boost their scores
                central = self._graph.get_central_entities(top_n=5)
                for entity_name in central:
                    entity_memories = self.episode_store.search_by_type(
                        MemoryType.RELATIONSHIP, limit=5, min_confidence=0.2
                    )
                    for mem in entity_memories:
                        if entity_name.lower() in mem.content.lower():
                            if mem.id in merged:
                                merged[mem.id].score = min(
                                    1.0, merged[mem.id].score + 0.20
                                )
                                merged[mem.id].source = "graph"
                            else:
                                merged[mem.id] = RetrievalResult(
                                    memory=mem,
                                    score=mem.effective_score() + 0.20,
                                    source="graph",
                                )
            except Exception:
                pass

        # ── Sort all results by final score ───────────────────────────────────
        ranked = sorted(merged.values(), key=lambda r: r.score, reverse=True)

        # ── Separate by memory type ───────────────────────────────────────────
        facts: list[Memory] = []
        preferences: list[Memory] = []

        for result in ranked:
            m = result.memory
            if m.type in (MemoryType.FACT, MemoryType.RELATIONSHIP, MemoryType.PATTERN):
                if len(facts) < _max_facts:
                    facts.append(m)
            elif m.type == MemoryType.PREFERENCE:
                if len(preferences) < _max_preferences:
                    preferences.append(m)

        # ── Active tasks (always SQL, not similarity-dependent) ───────────────
        active_tasks: list[Task] = self.episode_store.get_active_tasks(limit=_max_tasks)

        # ── Recent episode summary ────────────────────────────────────────────
        recent_summary = self.episode_store.get_recent_episode_summary(max_age_hours=48)

        elapsed_ms = (time.perf_counter() - t_start) * 1000

        return MemoryContext(
            facts=facts,
            preferences=preferences,
            active_tasks=active_tasks,
            recent_episode_summary=recent_summary,
            total_memories_searched=len(merged),
            retrieval_time_ms=elapsed_ms,
        )

    # ── Private search paths ──────────────────────────────────────────────────

    def _vector_search(
        self, query: str, n_results: int = 20
    ) -> list[VectorSearchResult]:
        """Run semantic similarity search. Returns empty list if unavailable."""
        if not self.vector_store.is_available():
            return []
        try:
            return self.vector_store.search(
                query, n_results=n_results, min_confidence=0.1
            )
        except Exception:
            return []

    def _sql_search(self, query: str, intent: str) -> list[Memory]:
        """
        Structured SQL-based retrieval with intent routing.

        Always retrieves:
          - Top preferences (sorted by importance)
          - High-importance facts (importance >= 0.6)
          - Recent memories (last 24h)

        Intent-specific additions:
          - TASK      → task-type memories
          - ENTITY    → relationship memories
          - EPISODIC  → expanded recent window (72h)
          - PREDICTIVE→ high-importance facts + all tasks
        """
        results: list[Memory] = []
        seen_ids: set[str] = set()

        def add_memories(memories: list[Memory]) -> None:
            for m in memories:
                if m.id not in seen_ids:
                    seen_ids.add(m.id)
                    results.append(m)

        # Always: top preferences
        preferences = self.episode_store.search_by_type(
            MemoryType.PREFERENCE, limit=10, min_confidence=0.2
        )
        add_memories(preferences)

        # Always: high-importance facts
        all_facts = self.episode_store.search_by_type(
            MemoryType.FACT, limit=15, min_confidence=0.3
        )
        high_importance = [f for f in all_facts if f.importance >= 0.6]
        add_memories(high_importance)

        # Always: recent (24h)
        recent = self.episode_store.get_recent_memories(hours=24, limit=10)
        add_memories(recent)

        # Intent-specific
        if intent == QueryIntent.TASK:
            task_mems = self.episode_store.search_by_type(MemoryType.TASK, limit=10)
            add_memories(task_mems)

        elif intent == QueryIntent.ENTITY:
            relationships = self.episode_store.search_by_type(
                MemoryType.RELATIONSHIP, limit=10
            )
            add_memories(relationships)

        elif intent == QueryIntent.EPISODIC:
            wider_recent = self.episode_store.get_recent_memories(hours=72, limit=20)
            add_memories(wider_recent)

        elif intent == QueryIntent.PREDICTIVE:
            all_important = self.episode_store.search_by_type(
                MemoryType.FACT, limit=20, min_confidence=0.4
            )
            add_memories([f for f in all_important if f.importance >= 0.7])

        return results

    # ── Intent classification ─────────────────────────────────────────────────

    def _classify_intent(self, query: str) -> str:
        """
        Phase B: use LLMIntentClassifier if available, else keyword fallback.
        """
        if self._intent_classifier:
            try:
                return self._intent_classifier.classify(query)
            except Exception:
                pass
        return self.classify_intent(query)

    @staticmethod
    def classify_intent(query: str) -> str:
        """
        Keyword-based intent classification fallback.
        Used when LLMIntentClassifier is unavailable or fails.
        """
        q = query.lower()

        task_signals = [
            "task",
            "todo",
            "pending",
            "what should i",
            "what do i need",
            "what's left",
            "remind",
            "deadline",
            "due",
            "finish",
            "complete",
        ]
        episodic_signals = [
            "yesterday",
            "last time",
            "we discussed",
            "you mentioned",
            "previous",
            "before",
            "earlier",
            "remember when",
            "what did",
        ]
        entity_signals = [
            "who is",
            "what do you know about",
            "tell me about",
            "what's the status of",
            "project",
        ]
        predictive_signals = [
            "should i",
            "focus on",
            "prioritize",
            "most important",
            "what matters",
            "urgent",
            "recommend",
        ]

        if any(s in q for s in task_signals):
            return QueryIntent.TASK
        if any(s in q for s in episodic_signals):
            return QueryIntent.EPISODIC
        if any(s in q for s in entity_signals):
            return QueryIntent.ENTITY
        if any(s in q for s in predictive_signals):
            return QueryIntent.PREDICTIVE

        return QueryIntent.GENERAL
