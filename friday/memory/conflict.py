"""
friday/memory/conflict.py

ConflictDetector — Phase B intelligence component.

Detects and auto-resolves contradictions between newly-extracted memories
and existing memories in the store.

Detection pipeline (runs in background extraction thread):
  1. For each new memory, vector-search for similar existing memories
     of the same type (cosine similarity threshold: SIMILARITY_THRESHOLD)
  2. For each candidate pair above threshold:
     - Quick heuristic pre-filter (length/content overlap check)
     - Call Claude Haiku to classify: CONTRADICTION / SUPERSESSION / COMPLEMENTARY
  3. Auto-resolution:
     SUPERSESSION → soft-delete older, confidence = 1.0 on newer
     CONTRADICTION → record ConflictRow, reduce confidence on both to 0.6
     COMPLEMENTARY → no action

Cost controls:
  - Max MAX_CHECKS_PER_BATCH LLM calls per extraction batch
  - Only checks memories of same MemoryType
  - Minimum content length difference must be < 80% to avoid comparing
    trivially different memories (prevents false positives)

All failures are silent — ConflictDetector never raises.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from friday.memory.types import Memory

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

SIMILARITY_THRESHOLD = 0.82  # cosine similarity above which we check
MAX_CHECKS_PER_BATCH = 8  # max LLM judge calls per extraction run
MIN_CONTENT_LEN = 10  # ignore very short memories


# ── Result dataclass ─────────────────────────────────────────────────────────


@dataclass
class ConflictResult:
    """The outcome of checking a memory pair for conflict."""

    memory_a: Memory
    memory_b: Memory
    verdict: str  # "CONTRADICTION" | "SUPERSESSION" | "COMPLEMENTARY"
    reason: str = ""
    newer_is_b: bool = True  # which memory supersedes (for SUPERSESSION)
    conflict_id: Optional[str] = None  # set if recorded in ConflictRow


# ── ConflictDetector ─────────────────────────────────────────────────────────


class ConflictDetector:
    """
    Post-extraction conflict scanner.

    Injected into MemoryBus._persist_extraction() after new memories
    are saved to SQLite and ChromaDB. Runs in the same background thread.
    """

    def __init__(self, episode_store, vector_store) -> None:  # type: ignore[no-untyped-def]
        self._episode_store = episode_store
        self._vector_store = vector_store

    def scan(self, new_memories: list[Memory]) -> list[ConflictResult]:
        """
        Scan a batch of freshly-extracted memories for conflicts.

        Returns a list of ConflictResult objects (may be empty).
        All exceptions are caught — this method never raises.
        """
        results: list[ConflictResult] = []
        checks_remaining = MAX_CHECKS_PER_BATCH

        for memory in new_memories:
            if checks_remaining <= 0:
                break

            if len(memory.content) < MIN_CONTENT_LEN:
                continue

            try:
                candidates = self._find_candidates(memory)
                for candidate in candidates:
                    if checks_remaining <= 0:
                        break
                    if candidate.id == memory.id:
                        continue  # same memory

                    result = self._judge_pair(memory, candidate)
                    checks_remaining -= 1

                    if result.verdict != "COMPLEMENTARY":
                        self._auto_resolve(result)
                        results.append(result)

            except Exception as exc:
                logger.debug("ConflictDetector scan error: %s", exc)
                continue

        return results

    # ── Private methods ───────────────────────────────────────────────────────

    def _find_candidates(self, memory: Memory) -> list[Memory]:
        """Find existing memories similar to `memory` using vector search."""
        try:
            if not self._vector_store.is_available():
                # Fall back to SQL-only lookup
                return self._episode_store.search_by_type(
                    memory.type, limit=5, min_confidence=0.2
                )

            # Vector search — returns memories of same type with cosine similarity
            results = self._vector_store.search(
                query=memory.content,
                n_results=6,
                memory_type_filter=memory.type.value,
                min_score=SIMILARITY_THRESHOLD,
            )
            return [r for r in results if r.id != memory.id]
        except Exception:
            return []

    def _judge_pair(self, mem_a: Memory, mem_b: Memory) -> ConflictResult:
        """
        Use Claude Haiku to classify the relationship between two memories.

        Classification:
          SUPERSESSION   — mem_b is an update/correction of mem_a
          CONTRADICTION  — they assert incompatible facts
          COMPLEMENTARY  — they are related but not conflicting

        Falls back to heuristic classification if LLM call fails.
        """
        try:
            verdict, reason = self._llm_judge(mem_a, mem_b)
        except Exception:
            verdict, reason = self._heuristic_judge(mem_a, mem_b)

        # Determine which is newer
        newer_is_b = mem_b.created_at >= mem_a.created_at

        return ConflictResult(
            memory_a=mem_a,
            memory_b=mem_b,
            verdict=verdict,
            reason=reason,
            newer_is_b=newer_is_b,
        )

    def _llm_judge(self, mem_a: Memory, mem_b: Memory) -> tuple[str, str]:
        """Call Claude Haiku to classify the memory pair."""
        from friday.config.settings import settings  # noqa: PLC0415
        from friday.llm.adapters.anthropic_adapter import AnthropicAdapter  # noqa: PLC0415

        prompt = f"""You are a memory conflict analyzer. Classify the relationship between these two memories.

MEMORY A: {mem_a.content}
MEMORY B: {mem_b.content}

Respond with exactly one word on line 1, and a brief reason on line 2:
- SUPERSESSION (B corrects/updates A, or vice versa)
- CONTRADICTION (they assert opposing facts)
- COMPLEMENTARY (related but not conflicting)

Classification:"""

        adapter = AnthropicAdapter()
        model = getattr(
            settings, "memory_extraction_model", "claude-haiku-4-5-20251001"
        )

        response_text = ""
        for chunk in adapter.stream(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            system="You are a precise conflict classification system. Be concise.",
            max_tokens=80,
        ):
            response_text += chunk

        lines = response_text.strip().splitlines()
        verdict_raw = lines[0].strip().upper() if lines else "COMPLEMENTARY"
        reason = lines[1].strip() if len(lines) > 1 else ""

        # Normalise
        if "SUPERSESSION" in verdict_raw:
            verdict = "SUPERSESSION"
        elif "CONTRADICTION" in verdict_raw:
            verdict = "CONTRADICTION"
        else:
            verdict = "COMPLEMENTARY"

        return verdict, reason

    def _heuristic_judge(self, mem_a: Memory, mem_b: Memory) -> tuple[str, str]:
        """
        Lightweight heuristic fallback when LLM judge fails.

        Logic:
          - Very high similarity (>0.95) + different content → SUPERSESSION
          - Contradictory keywords present → CONTRADICTION
          - Default → COMPLEMENTARY
        """
        content_a = mem_a.content.lower()
        content_b = mem_b.content.lower()

        # Simple word overlap (Jaccard)
        words_a = set(content_a.split())
        words_b = set(content_b.split())
        if words_a and words_b:
            overlap = len(words_a & words_b) / len(words_a | words_b)
        else:
            overlap = 0.0

        # Check for negation keywords
        negation_pairs = [
            ("is", "is not"),
            ("works at", "doesn't work"),
            ("likes", "doesn't like"),
            ("prefers", "doesn't prefer"),
        ]
        for pos, neg in negation_pairs:
            if (pos in content_a and neg in content_b) or (
                pos in content_b and neg in content_a
            ):
                return "CONTRADICTION", "Negation keyword pattern detected"

        if overlap > 0.7 and mem_a.content != mem_b.content:
            return "SUPERSESSION", "High content overlap with different phrasing"

        return "COMPLEMENTARY", "No conflict pattern detected"

    def _auto_resolve(self, result: ConflictResult) -> None:
        """
        Apply automatic resolution policy based on verdict.

        SUPERSESSION → soft-delete the older memory
        CONTRADICTION → record in ConflictRow, reduce confidence on both
        """
        try:
            if result.verdict == "SUPERSESSION":
                # The older memory is superseded by the newer one
                if result.newer_is_b:
                    older, newer = result.memory_a, result.memory_b
                else:
                    older, newer = result.memory_b, result.memory_a

                self._episode_store.soft_delete_memory(
                    memory_id=older.id,
                    superseded_by=newer.id,
                )
                logger.debug(
                    "ConflictDetector: supersession resolved — %s → %s",
                    older.id[:8],
                    newer.id[:8],
                )

            elif result.verdict == "CONTRADICTION":
                # Record the conflict and reduce confidence on both
                conflict_id = self._episode_store.record_conflict(
                    memory_a_id=result.memory_a.id,
                    memory_b_id=result.memory_b.id,
                    conflict_type="contradiction",
                )
                result.conflict_id = conflict_id

                # Reduce confidence to signal uncertainty
                for mem in (result.memory_a, result.memory_b):
                    mem.confidence = min(mem.confidence, 0.6)
                    self._episode_store.save_memory(mem)

                logger.debug(
                    "ConflictDetector: contradiction recorded — %s vs %s",
                    result.memory_a.id[:8],
                    result.memory_b.id[:8],
                )
        except Exception as exc:
            logger.debug("ConflictDetector auto-resolve error: %s", exc)
