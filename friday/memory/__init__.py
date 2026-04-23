"""
friday/memory/__init__.py

MemoryBus — the single public facade for the entire FRIDAY Memory Mesh.

Phase A: Foundation
  - WorkingMemory (RAM buffer)
  - EpisodeStore (SQLite)
  - VectorStore (ChromaDB)
  - ExtractionPipeline (Claude Haiku → typed memories)
  - RetrievalEngine (parallel vector + SQL)

Phase B: Intelligence Layer (added here)
  - KnowledgeGraph (NetworkX + SQLite entity graph)
  - EntityLinker (post-extraction → KG upsert)
  - ConflictDetector (post-extraction → contradiction scan)
  - DecayEngine (APScheduler → Ebbinghaus forgetting curve)
  - LLMIntentClassifier (replaces keyword intent heuristic in retriever)

Public API (unchanged from Phase A — fully backward compatible):
  observe_turn(user_input, assistant_response)
  get_context_for(query) → MemoryContext
  consolidate_session(turns) → ExtractionResult
  consolidate_session_async(turns)
  close_session(turns)
  get_active_tasks() → list[Task]
  get_stats() → dict
  forget(memory_id) → bool
  search(query, limit) → list[Memory]

Phase B additions:
  get_entity_context(entity_name) → str        ← KG subgraph for prompt
  get_conflict_report() → list[dict]           ← pending conflicts
  run_decay_now() → dict                       ← manual decay trigger
  graph: KnowledgeGraph                        ← direct KG access
"""

from __future__ import annotations

import threading
import uuid
from typing import Optional

from friday.config.settings import settings
from friday.memory.conflict import ConflictDetector
from friday.memory.decay import DecayEngine
from friday.memory.episodic import EpisodeStore
from friday.memory.extraction.entity_linker import EntityLinker
from friday.memory.extraction.pipeline import ExtractionPipeline, ExtractionResult
from friday.memory.graph import KnowledgeGraph
from friday.memory.retrieval.engine import QueryIntent as QueryIntent, RetrievalEngine
from friday.memory.retrieval.intent import LLMIntentClassifier
from friday.memory.types import Memory, MemoryContext, MemorySource, Task
from friday.memory.vector_store import VectorStore
from friday.memory.working import WorkingMemory


class MemoryBus:
    """
    Single facade for the FRIDAY Memory Mesh (Phase A + B).

    Lifecycle:
      1. Created once per FridayBrain instance (shared across turns).
      2. observe_turn() buffers each user + assistant turn.
      3. get_context_for() retrieves ranked context before each LLM call.
      4. consolidate_session_async() runs extraction + KG + conflict detection
         in a background thread every 5 turns.
      5. DecayEngine runs automatically every MEMORY_DECAY_INTERVAL_HOURS.
    """

    def __init__(self) -> None:
        self._enabled = settings.memory_enabled

        # ── Phase A: Storage layers ───────────────────────────────────────────
        self.working = WorkingMemory()
        self.episode_store = EpisodeStore()
        self.vector_store = VectorStore()

        # ── Phase A: Extraction + retrieval ───────────────────────────────────
        self.extractor = ExtractionPipeline()
        self.retriever = RetrievalEngine(self.episode_store, self.vector_store)

        # ── Phase B: Intelligence layer ───────────────────────────────────────
        self.graph = KnowledgeGraph()
        self.entity_linker = EntityLinker()
        self.conflict_detector = ConflictDetector(self.episode_store, self.vector_store)
        self.decay_engine = DecayEngine(self.episode_store, self.vector_store)
        self.intent_classifier = LLMIntentClassifier()

        # Wire Phase B into retrieval engine
        self.retriever.set_intent_classifier(self.intent_classifier)
        self.retriever.set_graph(self.graph)

        # ── Episode tracking ──────────────────────────────────────────────────
        self._current_episode_id: Optional[str] = None
        self._consolidation_lock = threading.Lock()

        # ── Startup sequence ──────────────────────────────────────────────────
        if self._enabled:
            self._startup()

    def _startup(self) -> None:
        """
        Initialise Phase B components in a background thread to avoid
        blocking FridayBrain startup (KG load + scheduler start).
        """

        def _init_phase_b() -> None:
            try:
                # Load KG from SQLite into NetworkX RAM graph
                self.graph.load_from_db()
            except Exception:
                pass
            try:
                # Start Ebbinghaus decay scheduler
                interval = getattr(settings, "memory_decay_interval_hours", 24.0)
                self.decay_engine.start_scheduler(interval_hours=interval)
            except Exception:
                pass

        self._start_episode()
        t = threading.Thread(
            target=_init_phase_b, daemon=True, name="friday-memory-startup"
        )
        t.start()

    # ── Observation ───────────────────────────────────────────────────────────

    def observe_turn(self, user_input: str, assistant_response: str) -> None:
        """
        Buffer a completed turn in working memory.
        Call after each exchange — pure RAM, instant.
        """
        if not self._enabled:
            return
        self.working.add_turn("user", user_input)
        self.working.add_turn("assistant", assistant_response)

    # ── Context retrieval (critical path — must be fast) ─────────────────────

    def get_context_for(self, query: str) -> MemoryContext:
        """
        Retrieve a ranked, assembled MemoryContext for the given query.

        Phase B: uses LLMIntentClassifier (with LRU cache) instead of keywords.
        If intent == ENTITY, also injects KG subgraph context into MemoryContext.

        Typical latency: 50–200ms (0ms on cache hit for intent).
        Returns empty MemoryContext on any failure.
        """
        if not self._enabled:
            return MemoryContext()

        try:
            # Phase B: LLM intent classification (cached)
            intent, entity_names = self.intent_classifier.classify_with_entities(query)

            # Run multi-modal retrieval (vector + SQL + optional KG)
            ctx = self.retriever.retrieve(query, intent=intent)

            # Phase B: inject KG entity context for ENTITY queries
            if intent == "entity" and entity_names and self.graph.is_available():
                entities_from_kg = []
                for name in entity_names[:2]:
                    entity = self.graph.get_entity(name)
                    if entity:
                        entities_from_kg.append(entity)
                if entities_from_kg:
                    ctx.entities = entities_from_kg

            # Surface any pending conflict warnings
            try:
                pending = self.episode_store.get_pending_conflicts()
                if pending:
                    ctx.conflicts = [
                        f"Memory conflict detected (ID: {c['id'][:8]})"
                        for c in pending[:3]
                    ]
            except Exception:
                pass

            return ctx

        except Exception:
            return MemoryContext()

    # ── Consolidation (background, off critical path) ─────────────────────────

    def consolidate_session(self, turns: list[dict]) -> ExtractionResult:
        """
        Run the full extraction + Phase B enrichment pipeline on the given turns.

        Pipeline:
          1. ExtractionPipeline → typed Memory + Task objects
          2. EpisodeStore.save_memory() → SQLite (Tier 1)
          3. VectorStore.upsert_many() → ChromaDB (Tier 2a)
          4. EntityLinker.link() → KnowledgeGraph (Tier 2b)       [Phase B]
          5. ConflictDetector.scan() → ConflictRow if needed       [Phase B]

        Called in a background thread — never blocks the LLM stream.
        """
        if not self._enabled or not turns:
            return ExtractionResult(success=True)

        if not self._consolidation_lock.acquire(blocking=False):
            return ExtractionResult(success=True)

        try:
            result = self.extractor.extract(
                turns,
                episode_id=self._current_episode_id,
                source=MemorySource.TEXT,
            )

            if result.success:
                self._persist_extraction(result)

            return result

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))
        finally:
            self._consolidation_lock.release()

    def consolidate_session_async(self, turns: list[dict]) -> None:
        """Fire-and-forget wrapper for consolidate_session()."""
        t = threading.Thread(
            target=self.consolidate_session,
            args=(turns,),
            daemon=True,
            name="friday-memory-consolidation",
        )
        t.start()

    def close_session(self, turns: list[dict]) -> None:
        """
        Close the current episode with a summary.
        Called on user disconnect or /reset.
        """
        if not self._enabled:
            return

        summary = self.extractor.extract_session_summary(turns)
        result = self.consolidate_session(turns)

        if self._current_episode_id:
            self.episode_store.close_episode(
                episode_id=self._current_episode_id,
                summary=summary or "",
                topics=result.topics if result.success else [],
                mood=result.mood if result.success else None,
                memory_ids=[m.id for m in result.memories] if result.success else [],
            )

        self._start_episode()

    # ── Direct access ─────────────────────────────────────────────────────────

    def get_active_tasks(self) -> list[Task]:
        """Return all active (pending/in-progress) tasks."""
        if not self._enabled:
            return []
        try:
            return self.episode_store.get_active_tasks()
        except Exception:
            return []

    def get_stats(self) -> dict:
        """Return full memory system health stats including Phase B components."""
        base: dict = {
            "enabled": self._enabled,
            "session_id": self.working.session_id,
            "session_turns": self.working.turn_count,
            "current_episode_id": self._current_episode_id,
            "vector_store_count": self.vector_store.count() if self._enabled else 0,
        }
        if self._enabled:
            try:
                base.update(self.episode_store.get_stats())
            except Exception:
                pass
            # Phase B stats
            try:
                base["knowledge_graph"] = self.graph.stats()
            except Exception:
                base["knowledge_graph"] = {}
            try:
                base["intent_cache"] = self.intent_classifier.get_cache_stats()
            except Exception:
                pass
            try:
                last_decay = self.decay_engine.get_last_report()
                if last_decay:
                    base["last_decay_pass"] = last_decay
            except Exception:
                pass
        return base

    def search(self, query: str, limit: int = 10) -> list[Memory]:
        """Direct memory search for introspection commands."""
        if not self._enabled:
            return []
        try:
            ctx = self.retriever.retrieve(query)
            return (ctx.facts + ctx.preferences)[:limit]
        except Exception:
            return []

    def forget(self, memory_id: str) -> bool:
        """Mark a memory as forgotten (Boss explicitly asked)."""
        if not self._enabled:
            return False
        try:
            self.episode_store.forget_memory(memory_id)
            self.vector_store.delete(memory_id)
            return True
        except Exception:
            return False

    # ── Phase B additions ─────────────────────────────────────────────────────

    def get_entity_context(self, entity_name: str) -> str:
        """
        Return a formatted entity card from the Knowledge Graph.
        Useful for tool calls or explicit "tell me about X" queries.
        """
        if not self._enabled or not self.graph.is_available():
            return ""
        try:
            return self.graph.get_subgraph_context(entity_name)
        except Exception:
            return ""

    def get_conflict_report(self) -> list[dict]:
        """Return all pending memory conflicts."""
        if not self._enabled:
            return []
        try:
            return self.episode_store.get_pending_conflicts()
        except Exception:
            return []

    def run_decay_now(self) -> dict:
        """
        Manually trigger a decay pass (Boss command: 'run memory decay').
        Returns the DecayReport as a dict.
        """
        if not self._enabled:
            return {"enabled": False}
        try:
            report = self.decay_engine.run_decay_pass()
            return report.to_dict()
        except Exception as e:
            return {"error": str(e)}

    def shutdown(self) -> None:
        """
        Clean shutdown — stops the APScheduler gracefully.
        Call from FridayBrain.__del__ or app shutdown handler.
        """
        try:
            self.decay_engine.stop_scheduler()
        except Exception:
            pass

    # ── Internal ──────────────────────────────────────────────────────────────

    def _start_episode(self) -> None:
        """Create a new episode row for the current session."""
        if not self._enabled:
            return
        try:
            episode = self.episode_store.start_episode(
                session_id=self.working.session_id
            )
            self._current_episode_id = episode.id
        except Exception:
            self._current_episode_id = str(uuid.uuid4())

    def _persist_extraction(self, result: ExtractionResult) -> None:
        """
        Save extracted memories and tasks across all storage tiers.

        Phase B: after saving, run EntityLinker and ConflictDetector.
        """
        memories_saved: list[Memory] = []

        # Tier 1: SQLite
        for memory in result.memories:
            if not memory.content.strip():
                continue
            try:
                self.episode_store.save_memory(memory)
                memories_saved.append(memory)
            except Exception:
                pass

        # Tier 2a: ChromaDB (batch)
        if memories_saved and self.vector_store.is_available():
            try:
                self.vector_store.upsert_many(memories_saved)
            except Exception:
                pass

        # Tier 2b: Knowledge Graph — EntityLinker (Phase B)
        if memories_saved and self.graph.is_available():
            try:
                self.entity_linker.link(memories_saved, self.graph)
            except Exception:
                pass

        # Conflict detection (Phase B) — silent, best-effort
        if memories_saved:
            try:
                self.conflict_detector.scan(memories_saved)
            except Exception:
                pass

        # Tasks → SQLite only (not vectorised)
        for task in result.tasks:
            try:
                self.episode_store.save_task(task)
            except Exception:
                pass
