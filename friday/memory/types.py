"""
friday/memory/types.py

Typed primitives for the FRIDAY Memory Mesh.

Every unit of memory is strongly typed — never a raw text blob.
The type determines storage tier, decay rate, and retrieval strategy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ── Memory type taxonomy ──────────────────────────────────────────────────────


class MemoryType(str, Enum):
    """
    The type of a memory unit.

    Each type has different:
      - decay rate     (patterns live longest; ephemeral shortest)
      - retrieval path (tasks → SQL; semantic → vector; graph → NetworkX)
      - extraction LLM (fact extraction vs preference inference)
    """

    FACT = "fact"  # Objective: "Boss works at Company X"
    PREFERENCE = "preference"  # Subjective: "Boss prefers dark themes"
    PATTERN = "pattern"  # Behavioural: "Boss works late on Sundays"
    EPISODE_REF = "episode"  # Pointer to a conversation episode
    TASK = "task"  # Actionable: "Review PR #47 by Friday"
    RELATIONSHIP = "relationship"  # Social: "Priya is Boss's manager"


class MemorySource(str, Enum):
    """Where did this memory originate?"""

    VOICE = "voice"
    TEXT = "text"
    INFERRED = "inferred"  # LLM-inferred from context
    CALENDAR = "calendar"
    EMAIL = "email"
    SYSTEM = "system"  # Auto-generated (e.g., session start)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
    SNOOZED = "snoozed"


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class ConflictResolution(str, Enum):
    PENDING = "pending"
    A_WINS = "a_wins"  # older memory takes precedence
    B_WINS = "b_wins"  # newer memory takes precedence
    BOTH_VALID = "both_valid"  # context-dependent, keep both
    USER_RESOLVED = "user_resolved"


# ── Core memory dataclass ─────────────────────────────────────────────────────


@dataclass
class Memory:
    """
    A single typed unit of FRIDAY's long-term memory.

    Scoring dimensions:
      confidence       – decays via Ebbinghaus forgetting curve
      importance       – set at extraction time, never decays
      emotional_valence – -1.0 (negative) to +1.0 (positive)
      stability        – spaced repetition stability score (increases on access)
    """

    # Identity
    id: str
    type: MemoryType
    content: str

    # Semantic tagging
    entities: list[str] = field(default_factory=list)  # entity names in KG
    category: str = "general"  # work | personal | health | schedule

    # Scoring
    confidence: float = 1.0  # 0.0–1.0; degrades via forgetting curve
    importance: float = 0.5  # 0.0–1.0; set at extraction, never decays
    emotional_valence: float = 0.0  # -1.0 (negative) → +1.0 (positive)
    stability: float = 1.0  # spaced repetition stability (days)

    # Lifecycle
    source: MemorySource = MemorySource.TEXT
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    next_review: Optional[datetime] = None  # when decay engine next checks
    expires_at: Optional[datetime] = None  # None = never expires

    # Versioning chain
    version: int = 1
    superseded_by: Optional[str] = None  # ID of the newer memory that replaced this

    # Source episode
    episode_id: Optional[str] = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def effective_score(self) -> float:
        """
        Composite score used for retrieval ranking.

        Weights:
          40% confidence (recency + access frequency)
          30% importance (set at extraction)
          20% emotional salience (abs value — both positive and negative stick)
          10% access recency (log-scaled)
        """
        import math

        recency_bonus = 0.0
        if self.last_accessed:
            hours_since = (
                datetime.utcnow() - self.last_accessed
            ).total_seconds() / 3600
            recency_bonus = max(0.0, 1.0 - math.log1p(hours_since) / 10)

        return (
            self.confidence * 0.40
            + self.importance * 0.30
            + abs(self.emotional_valence) * 0.20
            + recency_bonus * 0.10
        )


# ── Task dataclass ────────────────────────────────────────────────────────────


@dataclass
class Task:
    """A structured, actionable task extracted from conversation."""

    id: str
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    source_memory_id: Optional[str] = None
    blocked_by: list[str] = field(default_factory=list)  # task IDs
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ── Episode dataclass ─────────────────────────────────────────────────────────


@dataclass
class Episode:
    """
    A complete conversation session.

    Raw turns are stored for archive/audit. The summary is what gets
    retrieved for context injection.
    """

    id: str
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    raw_turns: list[dict] = field(default_factory=list)  # [{role, content}]
    summary: Optional[str] = None  # LLM-generated at session end
    topics: list[str] = field(default_factory=list)
    mood: Optional[str] = None  # inferred from emotional_valence
    memory_ids: list[str] = field(default_factory=list)  # memories extracted from this


# ── Entity dataclass (Knowledge Graph node) ───────────────────────────────────


@dataclass
class Entity:
    """A named entity in the knowledge graph (person, project, tool, concept)."""

    id: str
    name: str
    type: str  # person | project | tool | place | concept
    attributes: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None


# ── Context output for prompt injection ──────────────────────────────────────


@dataclass
class MemoryContext:
    """
    The assembled, ranked, deduplicated memory context ready for
    injection into FRIDAY's system prompt.
    """

    facts: list[Memory] = field(default_factory=list)
    preferences: list[Memory] = field(default_factory=list)
    active_tasks: list[Task] = field(default_factory=list)
    recent_episode_summary: Optional[str] = None
    entities: list[Entity] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)  # conflict warning strings
    total_memories_searched: int = 0
    retrieval_time_ms: float = 0.0

    def to_prompt_string(self) -> str:
        """
        Format the context for injection into the FRIDAY system prompt.
        Returns empty string if no memory is available.
        """
        if not any(
            [
                self.facts,
                self.preferences,
                self.active_tasks,
                self.recent_episode_summary,
                self.entities,
            ]
        ):
            return ""

        lines: list[str] = ["=== MEMORY CONTEXT ===", ""]

        if self.facts:
            lines.append("[FACTS]")
            for m in self.facts[:5]:  # top 5
                conf_pct = int(m.confidence * 100)
                lines.append(f"- {m.content} [confidence: {conf_pct}%]")
            lines.append("")

        if self.preferences:
            lines.append("[PREFERENCES]")
            for m in self.preferences[:5]:
                lines.append(f"- {m.content} [strength: {m.importance:.2f}]")
            lines.append("")

        if self.active_tasks:
            lines.append("[ACTIVE TASKS]")
            for t in self.active_tasks[:5]:
                urgency = " [URGENT]" if t.priority == TaskPriority.URGENT else ""
                due = f", due {t.due_date.strftime('%Y-%m-%d')}" if t.due_date else ""
                lines.append(f"- {t.title}{urgency}{due}")
            lines.append("")

        if self.recent_episode_summary:
            lines.append("[RECENT CONTEXT]")
            lines.append(self.recent_episode_summary)
            lines.append("")

        if self.entities:
            lines.append("[KEY PEOPLE & PROJECTS]")
            for e in self.entities[:5]:
                attrs = ", ".join(
                    f"{k}: {v}"
                    for k, v in e.attributes.items()
                    if k in ("role", "trust_level", "status", "deadline")
                )
                lines.append(
                    f"- {e.name} ({e.type})" + (f" — {attrs}" if attrs else "")
                )
            lines.append("")

        if self.conflicts:
            lines.append("[⚠ MEMORY CONFLICTS DETECTED]")
            for c in self.conflicts:
                lines.append(f"- {c}")
            lines.append("")

        return "\n".join(lines)
