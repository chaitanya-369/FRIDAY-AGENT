"""
friday/memory/extraction/pipeline.py

ExtractionPipeline — converts raw conversation turns into typed Memory objects.

Phase A implementation: single-pass LLM extraction using Claude Haiku.
Returns a list of typed Memory + Task objects ready for persistence.

Pipeline:
  1. Build extraction prompt from the last N turns
  2. Call Claude Haiku (cheap, fast — ~$0.0002 per extraction)
  3. Parse JSON response into typed Memory and Task dataclasses
  4. Detect conflicts against existing memories (simple content similarity)
  5. Return extraction result

The LLM is instructed to extract:
  - facts       : objective statements about Boss or the world
  - preferences : subjective likes/dislikes/habits
  - tasks       : actionable items with optional due dates
  - relationships: named entities and their connection to Boss

Design:
  - Extraction is always async-friendly (called from background task)
  - Failure is silent (returns empty result, never crashes FridayBrain)
  - Deduplification happens in consolidator.py (Phase B)
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from friday.config.settings import settings
from friday.memory.types import (
    Memory,
    MemorySource,
    MemoryType,
    Task,
    TaskPriority,
    TaskStatus,
)

# ── Extraction prompt template ────────────────────────────────────────────────

_EXTRACTION_SYSTEM = """You are FRIDAY's memory extraction module.
Your ONLY job is to extract memorable information from a conversation and return it as JSON.
Be precise, be selective. Only extract things truly worth remembering long-term.
Never invent information not present in the conversation.
Always respond with ONLY valid JSON — no explanation, no markdown, no prose."""

_EXTRACTION_PROMPT_TEMPLATE = """Analyze the following conversation and extract memorable information.

CONVERSATION:
{conversation}

Extract and return ONLY the following JSON structure (no other text):
{{
  "facts": [
    {{
      "content": "concise factual statement about Boss or their world",
      "entities": ["entity1", "entity2"],
      "category": "work|personal|health|schedule|finance|tech",
      "importance": 0.0-1.0,
      "emotional_valence": -1.0 to 1.0
    }}
  ],
  "preferences": [
    {{
      "content": "Boss prefers/likes/dislikes something — inferred or stated",
      "entities": ["relevant entity"],
      "category": "work|personal|health|schedule|tech",
      "importance": 0.0-1.0,
      "strength": 0.0-1.0
    }}
  ],
  "tasks": [
    {{
      "title": "short task title",
      "description": "optional detail",
      "priority": "urgent|high|normal|low",
      "due_date": "ISO datetime string or null",
      "entities": ["relevant entities"]
    }}
  ],
  "relationships": [
    {{
      "content": "Person X is Boss's [role] with [attribute]",
      "entities": ["person/entity name"],
      "category": "work",
      "importance": 0.0-1.0
    }}
  ],
  "topics": ["topic1", "topic2"],
  "mood": "positive|neutral|negative|frustrated|excited|tired|focused"
}}

Rules:
- importance: 0.9+ = essential (name, key decision), 0.5 = normal fact, 0.1 = minor detail
- emotional_valence: +1.0 = very positive, 0.0 = neutral, -1.0 = very negative
- If nothing meaningful to extract, return all arrays as []
- Max 5 facts, 5 preferences, 10 tasks, 5 relationships per call"""


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class ExtractionResult:
    """Result of a single extraction pipeline run."""

    memories: list[Memory] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    mood: Optional[str] = None
    episode_id: Optional[str] = None

    # Diagnostics
    raw_response: Optional[str] = None
    extraction_model: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    def is_empty(self) -> bool:
        return not self.memories and not self.tasks


# ── ExtractionPipeline ────────────────────────────────────────────────────────


class ExtractionPipeline:
    """
    Converts raw conversation turns into typed Memory and Task objects.

    Called asynchronously after each batch of turns — never on the
    critical path of the LLM response stream.
    """

    # How many recent turns to include in extraction context
    MAX_TURNS_FOR_EXTRACTION = 10

    def __init__(self) -> None:
        self._model = settings.memory_extraction_model
        self._client = None

    def _get_client(self):
        """Lazy-init Anthropic client."""
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    # ── Public API ────────────────────────────────────────────────────────────

    def extract(
        self,
        turns: list[dict],
        *,
        episode_id: Optional[str] = None,
        source: MemorySource = MemorySource.TEXT,
    ) -> ExtractionResult:
        """
        Run extraction on a list of conversation turns.

        Args:
            turns: list of {role, content} dicts
            episode_id: ID of the originating episode (for back-references)
            source: where the conversation came from

        Returns:
            ExtractionResult with typed memories and tasks.
            Always returns a result — never raises.
        """
        if not turns:
            return ExtractionResult(success=True)

        # Trim to last N turns for extraction
        recent_turns = turns[-self.MAX_TURNS_FOR_EXTRACTION :]

        try:
            conversation_text = self._format_turns(recent_turns)
            raw_json = self._call_llm(conversation_text)
            return self._parse_result(raw_json, episode_id=episode_id, source=source)
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=str(e),
            )

    def extract_session_summary(self, turns: list[dict]) -> Optional[str]:
        """
        Generate a compressed session summary for episode archiving.
        Called at session end. Returns None on failure.
        """
        if not turns:
            return None

        conversation_text = self._format_turns(turns[-20:])
        prompt = (
            f"Summarize the following conversation in 2-3 sentences. "
            f"Focus on what was discussed, decisions made, and tasks created. "
            f"Write from FRIDAY's perspective. Be concise.\n\n"
            f"CONVERSATION:\n{conversation_text}"
        )

        try:
            client = self._get_client()
            response = client.messages.create(
                model=self._model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception:
            return None

    # ── Private helpers ───────────────────────────────────────────────────────

    def _call_llm(self, conversation_text: str) -> str:
        """Call Claude Haiku and return the raw JSON response."""
        client = self._get_client()
        response = client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=_EXTRACTION_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": _EXTRACTION_PROMPT_TEMPLATE.format(
                        conversation=conversation_text
                    ),
                }
            ],
        )
        return response.content[0].text.strip()

    def _parse_result(
        self,
        raw_json: str,
        *,
        episode_id: Optional[str],
        source: MemorySource,
    ) -> ExtractionResult:
        """Parse the LLM JSON output into typed Memory and Task objects."""
        # Strip markdown code fences if present
        clean = raw_json.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")
            clean = "\n".join(lines[1:-1])

        try:
            data = json.loads(clean)
        except json.JSONDecodeError as e:
            return ExtractionResult(
                success=False,
                raw_response=raw_json,
                error=f"JSON parse error: {e}",
            )

        now = datetime.utcnow()
        memories: list[Memory] = []
        tasks: list[Task] = []

        # ── Facts ─────────────────────────────────────────────────────────────
        for item in data.get("facts", []):
            content = item.get("content", "").strip()
            if not content:
                continue
            memories.append(
                Memory(
                    id=str(uuid.uuid4()),
                    type=MemoryType.FACT,
                    content=content,
                    entities=item.get("entities", []),
                    category=item.get("category", "general"),
                    importance=float(item.get("importance", 0.5)),
                    emotional_valence=float(item.get("emotional_valence", 0.0)),
                    source=source,
                    created_at=now,
                    episode_id=episode_id,
                )
            )

        # ── Preferences ───────────────────────────────────────────────────────
        for item in data.get("preferences", []):
            content = item.get("content", "").strip()
            if not content:
                continue
            strength = float(item.get("strength", 0.7))
            memories.append(
                Memory(
                    id=str(uuid.uuid4()),
                    type=MemoryType.PREFERENCE,
                    content=content,
                    entities=item.get("entities", []),
                    category=item.get("category", "general"),
                    importance=float(item.get("importance", strength)),
                    source=source,
                    created_at=now,
                    episode_id=episode_id,
                )
            )

        # ── Relationships ─────────────────────────────────────────────────────
        for item in data.get("relationships", []):
            content = item.get("content", "").strip()
            if not content:
                continue
            memories.append(
                Memory(
                    id=str(uuid.uuid4()),
                    type=MemoryType.RELATIONSHIP,
                    content=content,
                    entities=item.get("entities", []),
                    category=item.get("category", "work"),
                    importance=float(item.get("importance", 0.7)),
                    source=source,
                    created_at=now,
                    episode_id=episode_id,
                )
            )

        # ── Tasks ─────────────────────────────────────────────────────────────
        for item in data.get("tasks", []):
            title = item.get("title", "").strip()
            if not title:
                continue

            # Parse due date
            due_date: Optional[datetime] = None
            if item.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(str(item["due_date"]))
                except (ValueError, TypeError):
                    pass

            # Parse priority
            priority_str = item.get("priority", "normal").lower()
            try:
                priority = TaskPriority(priority_str)
            except ValueError:
                priority = TaskPriority.NORMAL

            tasks.append(
                Task(
                    id=str(uuid.uuid4()),
                    title=title,
                    description=item.get("description", ""),
                    priority=priority,
                    status=TaskStatus.PENDING,
                    due_date=due_date,
                    tags=item.get("entities", []),
                    created_at=now,
                )
            )

        return ExtractionResult(
            memories=memories,
            tasks=tasks,
            topics=data.get("topics", []),
            mood=data.get("mood"),
            episode_id=episode_id,
            raw_response=raw_json,
            extraction_model=self._model,
            success=True,
        )

    @staticmethod
    def _format_turns(turns: list[dict]) -> str:
        """Format conversation turns into a readable string for the LLM."""
        lines = []
        for turn in turns:
            role = turn.get("role", "unknown").upper()
            content = turn.get("content", "")

            # Handle structured content (Anthropic tool-use blocks)
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            text_parts.append(f"[Used tool: {block.get('name', '?')}]")
                        elif block.get("type") == "tool_result":
                            text_parts.append("[Tool result]")
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = " ".join(text_parts)
            elif not isinstance(content, str):
                content = str(content)

            if content.strip():
                lines.append(f"{role}: {content.strip()}")

        return "\n".join(lines)
