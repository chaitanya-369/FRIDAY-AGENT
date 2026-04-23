"""
friday/memory/episodic.py

EpisodeStore — Tier 1 of the FRIDAY Memory Mesh.

SQLite-backed storage for:
  - Typed memory units (facts, preferences, patterns, tasks, relationships)
  - Conversation episodes (raw turns + LLM-generated summaries)
  - Structured tasks with priority, due dates, and block relationships

This is the primary persistent store. Everything flows through here
before being promoted to the Semantic Core (Tier 2: ChromaDB + KG).

Design principles:
  - All writes are idempotent (upsert by ID)
  - All reads return domain dataclasses, never raw SQLModel rows
  - Confidence and access counts are updated on every retrieval
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlmodel import Session, select

from friday.core.database import engine
from friday.memory.schema import (
    ConflictRow,
    EpisodeRow,
    MemoryRow,
    TaskRow,
)
from friday.memory.types import (
    ConflictResolution,
    Episode,
    Memory,
    MemorySource,
    MemoryType,
    Task,
    TaskPriority,
    TaskStatus,
)


# ── EpisodeStore ──────────────────────────────────────────────────────────────


class EpisodeStore:
    """
    Tier 1 persistent store.

    Responsible for:
      - Storing and retrieving Memory objects (typed facts, preferences, tasks, etc.)
      - Storing and summarising conversation Episode objects
      - Managing Task objects (CRUD + status transitions)
      - Detecting and recording memory conflicts
      - Applying basic confidence decay on retrieval
    """

    # ── Memory CRUD ───────────────────────────────────────────────────────────

    def save_memory(self, memory: Memory) -> None:
        """Upsert a Memory unit into the memories table."""
        with Session(engine) as db:
            existing = db.get(MemoryRow, memory.id)
            if existing:
                # Update mutable fields only
                existing.content = memory.content
                existing.confidence = memory.confidence
                existing.importance = memory.importance
                existing.emotional_valence = memory.emotional_valence
                existing.stability = memory.stability
                existing.last_accessed = memory.last_accessed
                existing.access_count = memory.access_count
                existing.next_review = memory.next_review
                existing.superseded_by = memory.superseded_by
                existing.version = memory.version
                existing.set_entities(memory.entities)
                db.add(existing)
            else:
                row = MemoryRow(
                    id=memory.id,
                    type=memory.type.value,
                    content=memory.content,
                    category=memory.category,
                    confidence=memory.confidence,
                    importance=memory.importance,
                    emotional_valence=memory.emotional_valence,
                    stability=memory.stability,
                    source=memory.source.value,
                    created_at=memory.created_at,
                    last_accessed=memory.last_accessed,
                    access_count=memory.access_count,
                    next_review=memory.next_review,
                    expires_at=memory.expires_at,
                    version=memory.version,
                    superseded_by=memory.superseded_by,
                    episode_id=memory.episode_id,
                )
                row.set_entities(memory.entities)
                db.add(row)
            db.commit()

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID, bumping access stats."""
        with Session(engine) as db:
            row = db.get(MemoryRow, memory_id)
            if row is None or row.superseded_by is not None:
                return None
            self._touch(db, row)
            return self._row_to_memory(row)

    def search_by_type(
        self,
        memory_type: MemoryType,
        *,
        limit: int = 20,
        min_confidence: float = 0.1,
        category: Optional[str] = None,
    ) -> list[Memory]:
        """Fetch top memories of a given type, ordered by effective score."""
        with Session(engine) as db:
            stmt = (
                select(MemoryRow)
                .where(MemoryRow.type == memory_type.value)
                .where(MemoryRow.confidence >= min_confidence)
                .where(MemoryRow.superseded_by.is_(None))
            )
            if category:
                stmt = stmt.where(MemoryRow.category == category)

            rows = db.exec(stmt).all()

            # Sort by composite importance (confidence × importance × recency)
            memories = [self._row_to_memory(r) for r in rows]
            memories.sort(key=lambda m: m.effective_score(), reverse=True)
            return memories[:limit]

    def get_recent_memories(
        self,
        hours: int = 24,
        limit: int = 30,
    ) -> list[Memory]:
        """Fetch memories created or accessed in the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        with Session(engine) as db:
            stmt = (
                select(MemoryRow)
                .where(MemoryRow.created_at >= cutoff)
                .where(MemoryRow.superseded_by.is_(None))
                .order_by(MemoryRow.created_at.desc())
                .limit(limit)
            )
            rows = db.exec(stmt).all()
            return [self._row_to_memory(r) for r in rows]

    def soft_delete_memory(self, memory_id: str, superseded_by: str) -> None:
        """
        Mark a memory as superseded (versioning — never hard-delete).
        The superseded_by ID should point to the newer memory.
        """
        with Session(engine) as db:
            row = db.get(MemoryRow, memory_id)
            if row:
                row.superseded_by = superseded_by
                db.add(row)
                db.commit()

    def forget_memory(self, memory_id: str) -> None:
        """
        Boss explicitly asked to forget this memory.
        We set confidence=0 and mark it expired rather than deleting,
        to preserve the audit trail.
        """
        with Session(engine) as db:
            row = db.get(MemoryRow, memory_id)
            if row:
                row.confidence = 0.0
                row.expires_at = datetime.utcnow()
                db.add(row)
                db.commit()

    def get_all_memories(self, min_confidence: float = 0.1) -> list[Memory]:
        """Return all active (non-superseded, non-expired) memories."""
        now = datetime.utcnow()
        with Session(engine) as db:
            stmt = (
                select(MemoryRow)
                .where(MemoryRow.superseded_by.is_(None))
                .where(MemoryRow.confidence >= min_confidence)
            )
            rows = db.exec(stmt).all()
            result = []
            for r in rows:
                if r.expires_at and r.expires_at < now:
                    continue  # Skip expired
                result.append(self._row_to_memory(r))
            return result

    # ── Task CRUD ─────────────────────────────────────────────────────────────

    def save_task(self, task: Task) -> None:
        """Upsert a task."""
        with Session(engine) as db:
            existing = db.get(TaskRow, task.id)
            if existing:
                existing.title = task.title
                existing.description = task.description
                existing.priority = task.priority.value
                existing.status = task.status.value
                existing.due_date = task.due_date
                existing.completed_at = task.completed_at
                existing.blocked_by_json = json.dumps(task.blocked_by)
                existing.tags_json = json.dumps(task.tags)
                db.add(existing)
            else:
                row = TaskRow(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority.value,
                    status=task.status.value,
                    due_date=task.due_date,
                    source_memory_id=task.source_memory_id,
                    blocked_by_json=json.dumps(task.blocked_by),
                    tags_json=json.dumps(task.tags),
                    created_at=task.created_at,
                    completed_at=task.completed_at,
                )
                db.add(row)
            db.commit()

    def get_active_tasks(
        self,
        priority: Optional[TaskPriority] = None,
        limit: int = 20,
    ) -> list[Task]:
        """Fetch all non-completed tasks, optionally filtered by priority."""
        with Session(engine) as db:
            stmt = select(TaskRow).where(TaskRow.status.in_(["pending", "in_progress"]))
            if priority:
                stmt = stmt.where(TaskRow.priority == priority.value)
            stmt = stmt.order_by(TaskRow.due_date.asc()).limit(limit)
            rows = db.exec(stmt).all()
            return [self._row_to_task(r) for r in rows]

    def get_overdue_tasks(self) -> list[Task]:
        """Return tasks past their due date that are still pending."""
        now = datetime.utcnow()
        with Session(engine) as db:
            stmt = (
                select(TaskRow)
                .where(TaskRow.status.in_(["pending", "in_progress"]))
                .where(TaskRow.due_date < now)
                .where(TaskRow.due_date.is_not(None))
            )
            rows = db.exec(stmt).all()
            return [self._row_to_task(r) for r in rows]

    def complete_task(self, task_id: str) -> None:
        """Mark a task as done."""
        with Session(engine) as db:
            row = db.get(TaskRow, task_id)
            if row:
                row.status = TaskStatus.DONE.value
                row.completed_at = datetime.utcnow()
                db.add(row)
                db.commit()

    # ── Episode CRUD ──────────────────────────────────────────────────────────

    def start_episode(self, session_id: str) -> Episode:
        """Create a new episode row for the current session."""
        episode = Episode(
            id=str(uuid.uuid4()),
            session_id=session_id,
            started_at=datetime.utcnow(),
        )
        with Session(engine) as db:
            row = EpisodeRow(
                id=episode.id,
                session_id=session_id,
                started_at=episode.started_at,
            )
            db.add(row)
            db.commit()
        return episode

    def update_episode_turns(self, episode_id: str, turns: list[dict]) -> None:
        """Persist the current conversation turns to the episode row."""
        with Session(engine) as db:
            row = db.get(EpisodeRow, episode_id)
            if row:
                row.raw_turns_json = json.dumps(turns)
                db.add(row)
                db.commit()

    def close_episode(
        self,
        episode_id: str,
        summary: str,
        topics: list[str],
        mood: Optional[str],
        memory_ids: list[str],
    ) -> None:
        """Mark an episode as complete with summary and extracted memory IDs."""
        with Session(engine) as db:
            row = db.get(EpisodeRow, episode_id)
            if row:
                row.ended_at = datetime.utcnow()
                row.summary = summary
                row.topics_json = json.dumps(topics)
                row.mood = mood
                row.memory_ids_json = json.dumps(memory_ids)
                db.add(row)
                db.commit()

    def get_recent_episode_summary(self, max_age_hours: int = 72) -> Optional[str]:
        """
        Return the summary from the most recent completed episode within
        max_age_hours. Returns None if no recent episode exists.
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        with Session(engine) as db:
            stmt = (
                select(EpisodeRow)
                .where(EpisodeRow.ended_at.is_not(None))
                .where(EpisodeRow.ended_at >= cutoff)
                .where(EpisodeRow.summary.is_not(None))
                .order_by(EpisodeRow.ended_at.desc())
                .limit(1)
            )
            row = db.exec(stmt).first()
            return row.summary if row else None

    # ── Conflict management ───────────────────────────────────────────────────

    def record_conflict(
        self,
        memory_a_id: str,
        memory_b_id: str,
        conflict_type: str = "contradiction",
    ) -> str:
        """Record a detected memory conflict for resolution."""
        conflict_id = str(uuid.uuid4())
        with Session(engine) as db:
            row = ConflictRow(
                id=conflict_id,
                memory_a_id=memory_a_id,
                memory_b_id=memory_b_id,
                conflict_type=conflict_type,
                resolution=ConflictResolution.PENDING.value,
            )
            db.add(row)
            db.commit()
        return conflict_id

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: ConflictResolution,
    ) -> None:
        """Mark a conflict as resolved."""
        with Session(engine) as db:
            row = db.get(ConflictRow, conflict_id)
            if row:
                row.resolution = resolution.value
                row.resolved_at = datetime.utcnow()
                db.add(row)
                db.commit()

    def get_pending_conflicts(self) -> list[dict]:
        """Return all unresolved conflicts as plain dicts."""
        with Session(engine) as db:
            stmt = select(ConflictRow).where(
                ConflictRow.resolution == ConflictResolution.PENDING.value
            )
            rows = db.exec(stmt).all()
            return [
                {
                    "id": r.id,
                    "memory_a_id": r.memory_a_id,
                    "memory_b_id": r.memory_b_id,
                    "conflict_type": r.conflict_type,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ]

    # ── Stats ─────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Return memory system health stats."""
        with Session(engine) as db:
            total = db.exec(select(MemoryRow)).all()
            active = [
                r for r in total if r.superseded_by is None and r.confidence > 0.1
            ]
            avg_confidence = (
                sum(r.confidence for r in active) / len(active) if active else 0.0
            )
            task_count = len(
                db.exec(
                    select(TaskRow).where(
                        TaskRow.status.in_(["pending", "in_progress"])
                    )
                ).all()
            )
            episode_count = len(db.exec(select(EpisodeRow)).all())

        type_counts: dict[str, int] = {}
        for m in active:
            type_counts[m.type] = type_counts.get(m.type, 0) + 1

        return {
            "total_memories": len(total),
            "active_memories": len(active),
            "avg_confidence": round(avg_confidence, 3),
            "memories_by_type": type_counts,
            "active_tasks": task_count,
            "total_episodes": episode_count,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _touch(db: Session, row: MemoryRow) -> None:
        """
        Update access stats on retrieval.
        Implements the spaced repetition stability increase:
          new_stability = old_stability × (1 + 0.2 / (1 + access_count))
        """
        row.last_accessed = datetime.utcnow()
        row.access_count = (row.access_count or 0) + 1
        row.stability = row.stability * (1 + 0.2 / (1 + row.access_count))
        # Bump confidence slightly on re-access (spaced repetition reinforcement)
        row.confidence = min(1.0, row.confidence + 0.02)
        db.add(row)
        db.commit()

    @staticmethod
    def _row_to_memory(row: MemoryRow) -> Memory:
        return Memory(
            id=row.id,
            type=MemoryType(row.type),
            content=row.content,
            entities=row.get_entities(),
            category=row.category,
            confidence=row.confidence,
            importance=row.importance,
            emotional_valence=row.emotional_valence,
            stability=row.stability,
            source=MemorySource(row.source),
            created_at=row.created_at,
            last_accessed=row.last_accessed,
            access_count=row.access_count or 0,
            next_review=row.next_review,
            expires_at=row.expires_at,
            version=row.version,
            superseded_by=row.superseded_by,
            episode_id=row.episode_id,
        )

    @staticmethod
    def _row_to_task(row: TaskRow) -> Task:
        return Task(
            id=row.id,
            title=row.title,
            description=row.description or "",
            priority=TaskPriority(row.priority),
            status=TaskStatus(row.status),
            due_date=row.due_date,
            source_memory_id=row.source_memory_id,
            blocked_by=row.get_blocked_by(),
            tags=row.get_tags(),
            created_at=row.created_at,
            completed_at=row.completed_at,
        )
