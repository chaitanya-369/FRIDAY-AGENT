"""
friday/memory/retrieval/engine.py

RetrievalEngine — multi-modal memory retrieval orchestrator.

Phase A implementation uses two parallel search paths:
  1. Vector search (ChromaDB)  — semantic similarity
  2. SQL structured search     — tasks, recent memories, type-filtered facts

Results are merged, deduplicated, and returned as a unified ranked list.
The ContextAssembler then selects and formats the final context string.

Phase B will add a third path: Knowledge Graph traversal (NetworkX).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from friday.config.settings import settings
from friday.memory.episodic import EpisodeStore
from friday.memory.types import Memory, MemoryContext, MemoryType, Task
from friday.memory.vector_store import VectorStore, VectorSearchResult


# ── Query intent taxonomy ─────────────────────────────────────────────────────


class QueryIntent:
    """Rough classification of what the user's query needs from memory."""

    EPISODIC = "episodic"  # "what did we discuss yesterday?"
    SEMANTIC = "semantic"  # "what does Boss prefer?"
    TASK = "task"  # "what's pending?" / "what do I need to do?"
    ENTITY = "entity"  # "what do you know about Priya?"
    PREDICTIVE = "predictive"  # "what will I need next?"
    GENERAL = "general"  # catch-all


# ── Merged result dataclass ───────────────────────────────────────────────────


@dataclass
class RetrievalResult:
    """A single memory returned from the retrieval engine with its final score."""

    memory: Memory
    score: float  # final combined score for ranking
    source: str  # "vector" | "sql" | "graph"
    vector_similarity: float = 0.0


# ── RetrievalEngine ───────────────────────────────────────────────────────────


class RetrievalEngine:
    """
    Multi-modal retrieval: vector similarity + structured SQL queries.

    Usage:
        engine = RetrievalEngine(episode_store, vector_store)
        ctx = engine.retrieve(query="what should I work on?")
    """

    def __init__(
        self,
        episode_store: EpisodeStore,
        vector_store: VectorStore,
    ) -> None:
        self.episode_store = episode_store
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        *,
        intent: str = QueryIntent.GENERAL,
        max_facts: Optional[int] = None,
        max_preferences: Optional[int] = None,
        max_tasks: Optional[int] = None,
    ) -> MemoryContext:
        """
        Run multi-modal retrieval and return an assembled MemoryContext.

        Args:
            query:           The user's current input (used for semantic search)
            intent:          Query intent type for path prioritisation
            max_facts:       Override settings.memory_max_facts
            max_preferences: Override settings.memory_max_preferences
            max_tasks:       Override settings.memory_max_tasks

        Returns:
            MemoryContext ready for ContextAssembler.
        """
        t_start = time.perf_counter()

        _max_facts = max_facts or settings.memory_max_facts
        _max_preferences = max_preferences or settings.memory_max_preferences
        _max_tasks = max_tasks or settings.memory_max_tasks

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

        # ── Path 2: SQL structured retrieval ─────────────────────────────────
        sql_results = self._sql_search(query, intent)

        # ── Merge: SQL results enrich or add to vector results ────────────────
        merged: dict[str, RetrievalResult] = dict(vector_by_id)
        for memory in sql_results:
            if memory.id in merged:
                # Boost score if found in both paths
                merged[memory.id].score = min(1.0, merged[memory.id].score + 0.15)
                merged[memory.id].memory = memory  # Use full memory object from SQL
            else:
                # SQL-only result — use effective_score as base
                merged[memory.id] = RetrievalResult(
                    memory=memory,
                    score=memory.effective_score(),
                    source="sql",
                )

        # ── Sort all results by final score ───────────────────────────────────
        ranked = sorted(merged.values(), key=lambda r: r.score, reverse=True)

        # ── Separate by type ──────────────────────────────────────────────────
        facts: list[Memory] = []
        preferences: list[Memory] = []

        for result in ranked:
            m = result.memory
            if m.type == MemoryType.FACT and len(facts) < _max_facts:
                facts.append(m)
            elif (
                m.type == MemoryType.PREFERENCE and len(preferences) < _max_preferences
            ):
                preferences.append(m)
            elif m.type == MemoryType.RELATIONSHIP and len(facts) < _max_facts:
                # Relationships shown in facts section
                facts.append(m)
            elif m.type == MemoryType.PATTERN and len(facts) < _max_facts:
                facts.append(m)

        # ── Always retrieve active tasks separately (not similarity-dependent) ─
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
        self,
        query: str,
        n_results: int = 20,
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
        Structured SQL-based retrieval.

        Fetches:
          - High-importance facts (importance >= 0.7)
          - All preferences (sorted by importance)
          - Recently created/accessed memories (last 24h)

        The intent drives which memory types to prioritise.
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

        # Recent memories (last 24h) — always fresh
        recent = self.episode_store.get_recent_memories(hours=24, limit=10)
        add_memories(recent)

        # Intent-specific additions
        if intent == QueryIntent.TASK:
            task_memories = self.episode_store.search_by_type(MemoryType.TASK, limit=10)
            add_memories(task_memories)

        elif intent == QueryIntent.ENTITY:
            relationships = self.episode_store.search_by_type(
                MemoryType.RELATIONSHIP, limit=10
            )
            add_memories(relationships)

        elif intent == QueryIntent.EPISODIC:
            # Recent episode memories
            add_memories(recent)

        return results

    # ── Intent classification ─────────────────────────────────────────────────

    @staticmethod
    def classify_intent(query: str) -> str:
        """
        Lightweight keyword-based intent classification.
        Phase B will replace this with an LLM classifier.
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

        if any(s in q for s in task_signals):
            return QueryIntent.TASK
        if any(s in q for s in episodic_signals):
            return QueryIntent.EPISODIC
        if any(s in q for s in entity_signals):
            return QueryIntent.ENTITY

        return QueryIntent.GENERAL
