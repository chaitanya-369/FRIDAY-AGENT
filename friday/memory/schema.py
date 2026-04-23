"""
friday/memory/schema.py

SQLModel table definitions for the FRIDAY Memory Mesh.

Tables:
  MemoryRow        — core typed memory units (facts, preferences, patterns, etc.)
  TaskRow          — structured actionable tasks
  EpisodeRow       — raw conversation sessions + summaries
  EntityRow        — knowledge graph nodes
  RelationshipRow  — knowledge graph edges
  ConflictRow      — detected memory contradictions awaiting resolution

All tables use the shared engine from friday.core.database.
Import this module in database.py to ensure tables are created.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


# ── Memory table ──────────────────────────────────────────────────────────────


class MemoryRow(SQLModel, table=True):
    """
    Persistent store for a single typed memory unit.

    confidence, stability, and next_review drive the Ebbinghaus
    forgetting curve and spaced repetition logic in DecayEngine.
    """

    __tablename__ = "memories"

    id: str = Field(primary_key=True)  # UUID string
    type: str  # MemoryType enum value
    content: str  # The memory text

    # Semantic tagging (JSON-encoded lists)
    entities_json: str = Field(default="[]")  # JSON list of entity names
    category: str = Field(default="general")  # work | personal | health | schedule

    # Scoring
    confidence: float = Field(default=1.0)
    importance: float = Field(default=0.5)
    emotional_valence: float = Field(default=0.0)
    stability: float = Field(default=1.0)  # spaced repetition stability (days)

    # Lifecycle
    source: str = Field(default="text")  # MemorySource enum value
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = Field(default=0)
    next_review: Optional[datetime] = None  # when DecayEngine next checks this
    expires_at: Optional[datetime] = None  # None = never expires

    # Versioning
    version: int = Field(default=1)
    superseded_by: Optional[str] = Field(default=None, foreign_key="memories.id")

    # Back-reference to source episode
    episode_id: Optional[str] = Field(default=None, foreign_key="episodes.id")

    # ── Convenience helpers ────────────────────────────────────────────────────

    def get_entities(self) -> list[str]:
        try:
            return json.loads(self.entities_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_entities(self, entities: list[str]) -> None:
        self.entities_json = json.dumps(entities)


# ── Task table ────────────────────────────────────────────────────────────────


class TaskRow(SQLModel, table=True):
    """Structured actionable task extracted from conversation."""

    __tablename__ = "tasks"

    id: str = Field(primary_key=True)
    title: str
    description: str = Field(default="")
    priority: str = Field(default="normal")  # TaskPriority enum value
    status: str = Field(default="pending")  # TaskStatus enum value
    due_date: Optional[datetime] = None
    source_memory_id: Optional[str] = Field(default=None, foreign_key="memories.id")
    blocked_by_json: str = Field(default="[]")  # JSON list of task IDs
    tags_json: str = Field(default="[]")  # JSON list of strings
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def get_blocked_by(self) -> list[str]:
        try:
            return json.loads(self.blocked_by_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_tags(self) -> list[str]:
        try:
            return json.loads(self.tags_json)
        except (json.JSONDecodeError, TypeError):
            return []


# ── Episode table ─────────────────────────────────────────────────────────────


class EpisodeRow(SQLModel, table=True):
    """
    A complete conversation session.

    raw_turns_json is the full conversation log.
    summary is a compressed, LLM-generated digest (generated async at session end).
    memory_ids_json lists the IDs of memories extracted from this episode.
    """

    __tablename__ = "episodes"

    id: str = Field(primary_key=True)
    session_id: str = Field(index=True)
    started_at: datetime
    ended_at: Optional[datetime] = None
    raw_turns_json: str = Field(default="[]")  # JSON list of {role, content}
    summary: Optional[str] = None  # generated at session end
    topics_json: str = Field(default="[]")  # JSON list of topic strings
    mood: Optional[str] = None  # inferred mood label
    memory_ids_json: str = Field(default="[]")  # JSON list of memory IDs

    def get_raw_turns(self) -> list[dict]:
        try:
            return json.loads(self.raw_turns_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_topics(self) -> list[str]:
        try:
            return json.loads(self.topics_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_memory_ids(self) -> list[str]:
        try:
            return json.loads(self.memory_ids_json)
        except (json.JSONDecodeError, TypeError):
            return []


# ── Entity table (Knowledge Graph nodes) ──────────────────────────────────────


class EntityRow(SQLModel, table=True):
    """A named entity node in the knowledge graph."""

    __tablename__ = "entities"

    id: str = Field(primary_key=True)
    name: str = Field(index=True, unique=True)
    type: str  # person | project | tool | place | concept
    attributes_json: str = Field(default="{}")  # JSON dict of entity attributes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None

    def get_attributes(self) -> dict:
        try:
            return json.loads(self.attributes_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_attributes(self, attrs: dict) -> None:
        self.attributes_json = json.dumps(attrs)


# ── Relationship table (Knowledge Graph edges) ────────────────────────────────


class RelationshipRow(SQLModel, table=True):
    """
    A typed, weighted, temporal edge between two entity nodes.

    Relation type examples:
      WORKS_ON, KNOWS, PREFERS, BLOCKED_BY, PART_OF, REQUIRES, MENTIONS, SUPERSEDES
    """

    __tablename__ = "relationships"

    id: str = Field(primary_key=True)
    from_entity_id: str = Field(foreign_key="entities.id", index=True)
    to_entity_id: str = Field(foreign_key="entities.id", index=True)
    relation_type: str  # e.g., "WORKS_ON", "KNOWS"
    weight: float = Field(default=1.0)  # strength of relationship
    attributes_json: str = Field(default="{}")  # JSON dict (trust_level, freq, etc.)
    confidence: float = Field(default=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: Optional[datetime] = None

    def get_attributes(self) -> dict:
        try:
            return json.loads(self.attributes_json)
        except (json.JSONDecodeError, TypeError):
            return {}


# ── Conflict table ────────────────────────────────────────────────────────────


class ConflictRow(SQLModel, table=True):
    """
    A detected contradiction between two memories, pending resolution.

    conflict_type examples:
      contradiction  — the two memories assert opposite things
      supersession   — memory_b updates/replaces memory_a
      uncertainty    — unclear which is correct
    """

    __tablename__ = "memory_conflicts"

    id: str = Field(primary_key=True)
    memory_a_id: str = Field(foreign_key="memories.id")
    memory_b_id: str = Field(foreign_key="memories.id")
    conflict_type: str = Field(default="contradiction")
    resolution: str = Field(default="pending")  # ConflictResolution enum value
    resolved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
