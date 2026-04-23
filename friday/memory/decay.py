"""
friday/memory/decay.py

DecayEngine — Phase B intelligence component.

Applies the Ebbinghaus forgetting curve to all memories on a scheduled
background pass, simulating natural memory decay.

Forgetting curve formula:
    R = e^(-t / S)

Where:
    R = new confidence (retrievability)
    t = elapsed time in days since last access
    S = stability score (stored in MemoryRow.stability)

Decay rate modifiers per memory type:
    FACT          → 1.0  (standard decay)
    EPISODE_REF   → 0.8  (decays fairly fast)
    PREFERENCE    → 0.5  (preferences are sticky — decay slowly)
    RELATIONSHIP  → 0.25 (relationships very stable)
    PATTERN       → 0.3  (patterns very stable)
    TASK          → 0.0  (tasks NEVER decay — they must be explicitly completed)

Archival threshold:
    Memories below ARCHIVE_THRESHOLD confidence are considered "forgotten"
    They remain in SQLite for audit trail but are excluded from retrieval.

Scheduling:
    APScheduler BackgroundScheduler runs run_decay_pass() every
    MEMORY_DECAY_INTERVAL_HOURS (default: 24h).
    The first pass runs 60s after startup to avoid blocking init.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from friday.memory.types import Memory, MemoryType

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

ARCHIVE_THRESHOLD = 0.15  # below this confidence → memory is "forgotten"
MINIMUM_CONFIDENCE = 0.05  # floor — never set confidence below this

# Per-type decay rate multipliers (1.0 = standard Ebbinghaus decay)
DECAY_RATES: dict[MemoryType, float] = {
    MemoryType.FACT: 1.0,
    MemoryType.EPISODE_REF: 0.8,
    MemoryType.PREFERENCE: 0.5,
    MemoryType.PATTERN: 0.3,
    MemoryType.RELATIONSHIP: 0.25,
    MemoryType.TASK: 0.0,  # tasks never decay
}

# Default stability for types that don't have one set yet
DEFAULT_STABILITY: dict[MemoryType, float] = {
    MemoryType.FACT: 2.0,  # 2-day natural stability
    MemoryType.PREFERENCE: 10.0,  # 10-day
    MemoryType.PATTERN: 14.0,  # 2-week
    MemoryType.RELATIONSHIP: 30.0,  # 1-month
    MemoryType.TASK: 999.0,  # effectively infinite
    MemoryType.EPISODE_REF: 3.0,
}


# ── Report dataclass ─────────────────────────────────────────────────────────


@dataclass
class DecayReport:
    """Summary of a completed decay pass."""

    run_at: datetime = field(default_factory=datetime.utcnow)
    total_checked: int = 0
    total_decayed: int = 0
    total_archived: int = 0
    skipped_tasks: int = 0
    average_confidence_before: float = 0.0
    average_confidence_after: float = 0.0
    errors: int = 0

    def to_dict(self) -> dict:
        return {
            "run_at": self.run_at.isoformat(),
            "total_checked": self.total_checked,
            "total_decayed": self.total_decayed,
            "total_archived": self.total_archived,
            "skipped_tasks": self.skipped_tasks,
            "avg_confidence_before": round(self.average_confidence_before, 3),
            "avg_confidence_after": round(self.average_confidence_after, 3),
            "errors": self.errors,
        }


# ── DecayEngine ──────────────────────────────────────────────────────────────


class DecayEngine:
    """
    Applies Ebbinghaus forgetting curve decay to all memories.

    Usage (via MemoryBus):
        engine = DecayEngine(episode_store, vector_store)
        engine.start_scheduler(interval_hours=24)
        # ... runs in background
        report = engine.run_decay_pass()  # manual trigger
    """

    def __init__(self, episode_store, vector_store) -> None:  # type: ignore[no-untyped-def]
        self._episode_store = episode_store
        self._vector_store = vector_store
        self._scheduler = None
        self._last_report: Optional[DecayReport] = None

    # ── Scheduler ────────────────────────────────────────────────────────────

    def start_scheduler(self, interval_hours: float = 24.0) -> None:
        """
        Start an APScheduler background job to run decay passes automatically.

        First pass runs after a 60s delay to allow system to warm up.
        Subsequent passes run every `interval_hours`.

        Fails silently if APScheduler is not installed.
        """
        try:
            from apscheduler.schedulers.background import BackgroundScheduler  # noqa: PLC0415
            from apscheduler.triggers.interval import IntervalTrigger  # noqa: PLC0415

            self._scheduler = BackgroundScheduler(daemon=True)
            self._scheduler.add_job(
                func=self._safe_decay_pass,
                trigger=IntervalTrigger(hours=interval_hours),
                next_run_time=datetime.utcnow() + timedelta(seconds=60),
                id="memory_decay",
                name="FRIDAY Memory Decay Engine",
                replace_existing=True,
            )
            self._scheduler.start()
            logger.info(
                "DecayEngine: scheduler started (interval=%sh, first run in 60s)",
                interval_hours,
            )
        except ImportError:
            logger.warning(
                "DecayEngine: APScheduler not installed — decay scheduling disabled. "
                "Run: pip install apscheduler"
            )
        except Exception as exc:
            logger.warning("DecayEngine: scheduler start failed: %s", exc)

    def stop_scheduler(self) -> None:
        """Gracefully stop the APScheduler."""
        try:
            if self._scheduler and self._scheduler.running:
                self._scheduler.shutdown(wait=False)
                logger.info("DecayEngine: scheduler stopped")
        except Exception:
            pass

    def _safe_decay_pass(self) -> None:
        """Wrapper for scheduled calls — catches all exceptions."""
        try:
            report = self.run_decay_pass()
            logger.info(
                "DecayEngine: pass complete — checked=%d decayed=%d archived=%d",
                report.total_checked,
                report.total_decayed,
                report.total_archived,
            )
        except Exception as exc:
            logger.warning("DecayEngine: pass failed: %s", exc)

    # ── Core decay logic ──────────────────────────────────────────────────────

    def run_decay_pass(self) -> DecayReport:
        """
        Run a full decay pass over all memories due for review.

        A memory is 'due' if its next_review timestamp is in the past,
        or if it has never been reviewed (next_review is None).

        Returns a DecayReport with statistics.
        """
        report = DecayReport()
        now = datetime.utcnow()

        try:
            all_memories = self._episode_store.get_all_memories(min_confidence=0.0)
        except Exception as exc:
            logger.warning("DecayEngine: failed to load memories: %s", exc)
            report.errors += 1
            return report

        conf_before_sum = 0.0
        conf_after_sum = 0.0
        processed = 0

        for memory in all_memories:
            try:
                report.total_checked += 1

                # Tasks never decay
                if memory.type == MemoryType.TASK:
                    report.skipped_tasks += 1
                    continue

                # Only process memories that are due for review
                if memory.next_review and memory.next_review > now:
                    continue

                conf_before = memory.confidence
                conf_before_sum += conf_before

                new_confidence, new_stability, new_next_review = self._apply_decay(
                    memory, now
                )

                conf_after = new_confidence
                conf_after_sum += conf_after

                # Only write back if confidence changed meaningfully
                if abs(conf_before - conf_after) > 0.001:
                    memory.confidence = conf_after
                    memory.stability = new_stability
                    memory.next_review = new_next_review

                    try:
                        self._episode_store.save_memory(memory)
                    except Exception:
                        pass

                    report.total_decayed += 1

                    if (
                        conf_after < ARCHIVE_THRESHOLD
                        and conf_before >= ARCHIVE_THRESHOLD
                    ):
                        report.total_archived += 1
                        logger.debug(
                            "DecayEngine: memory archived (confidence %.2f): %s",
                            conf_after,
                            memory.content[:60],
                        )

                    # Update ChromaDB metadata confidence too
                    if self._vector_store.is_available():
                        try:
                            self._vector_store.update_confidence(memory.id, conf_after)
                        except Exception:
                            pass

                processed += 1

            except Exception as exc:
                logger.debug("DecayEngine: error on memory %s: %s", memory.id[:8], exc)
                report.errors += 1
                continue

        report.average_confidence_before = (
            conf_before_sum / processed if processed else 0.0
        )
        report.average_confidence_after = (
            conf_after_sum / processed if processed else 0.0
        )
        self._last_report = report
        return report

    def _apply_decay(
        self,
        memory: Memory,
        now: datetime,
    ) -> tuple[float, float, datetime]:
        """
        Apply the Ebbinghaus forgetting curve to a single memory.

        Returns: (new_confidence, new_stability, next_review_time)
        """
        memory_type = memory.type
        decay_rate = DECAY_RATES.get(memory_type, 1.0)

        # No decay for tasks or zero-rate types
        if decay_rate == 0.0:
            return memory.confidence, memory.stability, now + timedelta(days=365)

        # Calculate elapsed time since last access
        last_event = memory.last_accessed or memory.created_at
        elapsed_days = (now - last_event).total_seconds() / 86400.0
        elapsed_days = max(0.001, elapsed_days)  # prevent division by zero

        # Use stored stability, or fallback to type default
        stability = (
            memory.stability
            if memory.stability > 0
            else DEFAULT_STABILITY.get(memory_type, 2.0)
        )

        # Ebbinghaus: R = e^(-t / S) × decay_rate_modifier
        # The decay_rate acts as a multiplier on t (faster t → faster decay)
        effective_t = elapsed_days * decay_rate
        new_confidence = memory.confidence * math.exp(-effective_t / stability)
        new_confidence = max(MINIMUM_CONFIDENCE, new_confidence)

        # Update stability slightly downward each cycle (memory gets weaker without use)
        new_stability = max(0.5, stability * 0.99)

        # Schedule next review based on stability (review sooner for low-stability)
        # Review interval = stability / 3 days (min 6h, max 30 days)
        review_interval_days = max(0.25, min(30.0, new_stability / 3.0))
        next_review = now + timedelta(days=review_interval_days)

        return new_confidence, new_stability, next_review

    # ── Reporting ─────────────────────────────────────────────────────────────

    def get_last_report(self) -> Optional[dict]:
        """Return the result of the last decay pass as a dict."""
        if self._last_report:
            return self._last_report.to_dict()
        return None

    def get_decay_preview(self, memory: Memory) -> dict:
        """
        Preview what decay would do to a memory without writing it.
        Useful for debugging and Boss-facing memory audit commands.
        """
        try:
            now = datetime.utcnow()
            new_conf, new_stab, next_review = self._apply_decay(memory, now)
            return {
                "memory_id": memory.id,
                "content_preview": memory.content[:80],
                "current_confidence": round(memory.confidence, 3),
                "projected_confidence": round(new_conf, 3),
                "would_archive": new_conf < ARCHIVE_THRESHOLD,
                "next_review": next_review.isoformat(),
                "stability": round(memory.stability, 2),
                "decay_rate_type": DECAY_RATES.get(memory.type, 1.0),
            }
        except Exception as exc:
            return {"error": str(exc)}
