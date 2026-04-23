"""
friday/memory/__init__.py

MemoryBus — the single public facade for the entire FRIDAY Memory Mesh.

All of FridayBrain's memory interactions go through this class.
Internal implementation details (EpisodeStore, VectorStore, ExtractionPipeline,
RetrievalEngine) are hidden behind this clean API.

Public API:
  observe(content, role)          → buffer a turn for async extraction
  get_context_for(query)          → retrieve ranked memory context (fast)
  consolidate_session(turns)      → run extraction + persist (called async)
  get_active_tasks()              → structured task list
  get_stats()                     → memory health report
  forget(memory_id)               → Boss asked to forget something
  search(query)                   → direct memory search for introspection

Usage in FridayBrain:
    self.memory = MemoryBus()
    # On each turn:
    ctx = self.memory.get_context_for(user_input)
    system = build_prompt_with(ctx.to_prompt_string())
    # After response:
    self.memory.observe_turn(user_input, response_text)
    # Every 5 turns (fire-and-forget):
    threading.Thread(target=self.memory.consolidate_session,
                     args=(self.working.get_raw_history(),), daemon=True).start()
"""

from __future__ import annotations

import threading
import uuid
from typing import Optional

from friday.config.settings import settings
from friday.memory.episodic import EpisodeStore
from friday.memory.extraction.pipeline import ExtractionPipeline, ExtractionResult
from friday.memory.retrieval.engine import QueryIntent as QueryIntent, RetrievalEngine
from friday.memory.types import Memory, MemoryContext, MemorySource, Task
from friday.memory.vector_store import VectorStore
from friday.memory.working import WorkingMemory


class MemoryBus:
    """
    Single facade for the FRIDAY Memory Mesh.

    Lifecycle:
      1. Created once per FridayBrain instance (shared across turns).
      2. observe_turn() buffers each user + assistant turn.
      3. get_context_for() retrieves and ranks context before each LLM call.
      4. consolidate_session() runs extraction in a background thread.
    """

    def __init__(self) -> None:
        self._enabled = settings.memory_enabled

        # Storage layers
        self.working = WorkingMemory()
        self.episode_store = EpisodeStore()
        self.vector_store = VectorStore()

        # Extraction + retrieval
        self.extractor = ExtractionPipeline()
        self.retriever = RetrievalEngine(self.episode_store, self.vector_store)

        # Episode tracking
        self._current_episode_id: Optional[str] = None
        self._start_episode()

        # Background consolidation lock (one at a time)
        self._consolidation_lock = threading.Lock()

    # ── Observation (buffering turns) ─────────────────────────────────────────

    def observe_turn(self, user_input: str, assistant_response: str) -> None:
        """
        Buffer a completed turn (user message + assistant reply).
        Call after each exchange — this is fast (RAM only).
        """
        if not self._enabled:
            return

        self.working.add_turn("user", user_input)
        self.working.add_turn("assistant", assistant_response)

    # ── Context retrieval (on critical path — must be fast) ──────────────────

    def get_context_for(self, query: str) -> MemoryContext:
        """
        Retrieve a ranked, assembled MemoryContext for the given query.

        Uses parallel vector + SQL search. Typical latency: 50–200ms.
        Returns an empty MemoryContext if memory is disabled or DB is empty.
        """
        if not self._enabled:
            return MemoryContext()

        try:
            intent = RetrievalEngine.classify_intent(query)
            return self.retriever.retrieve(query, intent=intent)
        except Exception:
            # Never crash FridayBrain due to memory failure
            return MemoryContext()

    # ── Consolidation (background, off critical path) ─────────────────────────

    def consolidate_session(self, turns: list[dict]) -> ExtractionResult:
        """
        Run extraction pipeline on the given turns and persist results.

        Called in a background thread — never blocks the LLM response stream.
        Uses a lock to prevent concurrent consolidation runs.

        Returns the ExtractionResult for diagnostics.
        """
        if not self._enabled or not turns:
            return ExtractionResult(success=True)

        if not self._consolidation_lock.acquire(blocking=False):
            # Already running — skip this round
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
        """
        Fire-and-forget wrapper for consolidate_session().
        Runs in a daemon thread — safe to call from FridayBrain.
        """
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
        Called when the user disconnects or /reset is issued.
        Runs synchronously because we want the summary before the episode closes.
        """
        if not self._enabled:
            return

        # Generate session summary
        summary = self.extractor.extract_session_summary(turns)

        # Extract final memories from this session
        result = self.consolidate_session(turns)

        # Close the episode row
        if self._current_episode_id:
            self.episode_store.close_episode(
                episode_id=self._current_episode_id,
                summary=summary or "",
                topics=result.topics if result.success else [],
                mood=result.mood if result.success else None,
                memory_ids=[m.id for m in result.memories] if result.success else [],
            )

        # Start a fresh episode for the next session
        self._start_episode()

    # ── Direct access (for autopilot, tools, introspection) ──────────────────

    def get_active_tasks(self) -> list[Task]:
        """Return all active (pending/in-progress) tasks."""
        if not self._enabled:
            return []
        try:
            return self.episode_store.get_active_tasks()
        except Exception:
            return []

    def get_stats(self) -> dict:
        """Return memory system health stats for diagnostics."""
        base = {
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
        return base

    def search(self, query: str, limit: int = 10) -> list[Memory]:
        """Direct memory search — used for introspection commands."""
        if not self._enabled:
            return []
        try:
            ctx = self.retriever.retrieve(query)
            all_memories = ctx.facts + ctx.preferences
            return all_memories[:limit]
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
        """Save extracted memories and tasks to all storage tiers."""
        memories_to_upsert: list[Memory] = []

        for memory in result.memories:
            # Skip empty content
            if not memory.content.strip():
                continue
            try:
                # Tier 1: SQLite
                self.episode_store.save_memory(memory)
                memories_to_upsert.append(memory)
            except Exception:
                pass

        # Tier 2a: ChromaDB (batch for efficiency)
        if memories_to_upsert and self.vector_store.is_available():
            try:
                self.vector_store.upsert_many(memories_to_upsert)
            except Exception:
                pass

        # Tasks → SQLite only (not vectorised)
        for task in result.tasks:
            try:
                self.episode_store.save_task(task)
            except Exception:
                pass
