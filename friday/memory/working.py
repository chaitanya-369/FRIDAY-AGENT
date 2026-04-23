"""
friday/memory/working.py

WorkingMemory — Tier 0 of the FRIDAY Memory Mesh.

Lives entirely in RAM. Zero latency. Session-scoped.

Responsibilities:
  - Sliding window conversation buffer (last 20 turns)
  - Ephemeral key-value store for session-local facts
  - Pre-loaded memory candidate cache (for fast context injection)
  - Turn counter for consolidation triggers

All data is LOST when the process restarts — that's intentional.
Persistence lives in EpisodeStore (Tier 1) and above.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ConversationTurn:
    """A single turn in the current conversation."""

    role: str  # "user" | "assistant" | "tool"
    content: Any  # str or structured content block
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None


class WorkingMemory:
    """
    Tier 0 — In-process, session-scoped memory.

    Thread-safety note: FridayBrain is single-threaded per session
    (one FastAPI request at a time). No locking needed.
    """

    # Sliding window size — 20 full turns = 40 messages (user+assistant)
    MAX_TURNS: int = 20

    def __init__(self) -> None:
        # Conversation buffer: ordered, size-limited
        self._turns: deque[ConversationTurn] = deque(maxlen=self.MAX_TURNS * 2)

        # Session state
        self.session_id: str = self._generate_session_id()
        self.session_start: datetime = datetime.utcnow()
        self.turn_count: int = 0

        # Ephemeral key-value store (facts valid only for this session)
        self._ephemeral: dict[str, Any] = {}

        # Pre-loaded memory candidates for fast injection
        # Populated by the retrieval engine between turns
        self._memory_candidates: list = []

    # ── Conversation buffer ───────────────────────────────────────────────────

    def add_turn(
        self,
        role: str,
        content: Any,
        *,
        tool_name: Optional[str] = None,
        tool_call_id: Optional[str] = None,
    ) -> ConversationTurn:
        """Add a turn to the conversation buffer."""
        turn = ConversationTurn(
            role=role,
            content=content,
            tool_name=tool_name,
            tool_call_id=tool_call_id,
        )
        self._turns.append(turn)
        if role == "user":
            self.turn_count += 1
        return turn

    def get_turns(self) -> list[ConversationTurn]:
        """Return all buffered turns in chronological order."""
        return list(self._turns)

    def get_last_n_turns(self, n: int) -> list[ConversationTurn]:
        """Return the most recent n turns."""
        turns = list(self._turns)
        return turns[-n:] if n < len(turns) else turns

    def get_raw_history(self) -> list[dict]:
        """
        Return conversation history in the format expected by FridayBrain
        (list of {role, content} dicts, compatible with LLMRouter).
        """
        result = []
        for t in self._turns:
            msg: dict = {"role": t.role, "content": t.content}
            if t.tool_name:
                msg["name"] = t.tool_name
            if t.tool_call_id:
                msg["tool_call_id"] = t.tool_call_id
            result.append(msg)
        return result

    def clear(self) -> None:
        """Clear the conversation buffer (e.g., on explicit /reset)."""
        self._turns.clear()
        self.turn_count = 0

    # ── Ephemeral key-value store ─────────────────────────────────────────────

    def set(self, key: str, value: Any) -> None:
        """Store a session-local fact."""
        self._ephemeral[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a session-local fact."""
        return self._ephemeral.get(key, default)

    def delete(self, key: str) -> None:
        """Remove a session-local fact."""
        self._ephemeral.pop(key, None)

    # ── Pre-loaded memory candidate cache ────────────────────────────────────

    def set_memory_candidates(self, candidates: list) -> None:
        """Cache pre-loaded memory candidates for fast context injection."""
        self._memory_candidates = candidates

    def get_memory_candidates(self) -> list:
        """Retrieve the pre-loaded memory candidate cache."""
        return self._memory_candidates

    # ── Session metadata ──────────────────────────────────────────────────────

    def should_consolidate(self) -> bool:
        """
        Return True if the session is long enough to warrant consolidation.
        Consolidation is triggered every 5 user turns.
        """
        return self.turn_count > 0 and self.turn_count % 5 == 0

    def get_session_duration_seconds(self) -> float:
        """Return how long this session has been active."""
        return (datetime.utcnow() - self.session_start).total_seconds()

    def snapshot(self) -> dict:
        """Return a JSON-serialisable snapshot for archiving."""
        return {
            "session_id": self.session_id,
            "started_at": self.session_start.isoformat(),
            "turn_count": self.turn_count,
            "turns": [
                {
                    "role": t.role,
                    "content": t.content
                    if isinstance(t.content, str)
                    else str(t.content),
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in self._turns
            ],
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _generate_session_id() -> str:
        import uuid

        return str(uuid.uuid4())

    def __repr__(self) -> str:
        return (
            f"WorkingMemory(session={self.session_id[:8]}..., "
            f"turns={len(self._turns)}, "
            f"user_turns={self.turn_count})"
        )
