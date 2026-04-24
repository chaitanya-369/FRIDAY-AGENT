"""
friday/memory/extraction/pattern_generalizer.py

PatternGeneralizer synthesizes high-level patterns from discrete episodic facts and preferences.
It runs as a background process to find commonalities in the agent's memory mesh.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import List

from friday.config.settings import settings
from friday.memory.types import Memory, MemoryType, MemorySource

logger = logging.getLogger(__name__)

_PATTERN_SYSTEM = """You are FRIDAY's pattern generalization module.
Analyze the following discrete facts and preferences about the user.
Identify 1-3 high-level behavioral, cognitive, or lifestyle patterns.
Return ONLY valid JSON in the requested format, no markdown."""

_PATTERN_PROMPT = """Review these memories:
{memories}

Extract ONLY new or reinforced broad patterns. A pattern must be supported by multiple facts/preferences.

Return JSON:
{{
  "patterns": [
    {{
      "content": "Broad pattern observed (e.g. 'Boss tends to work late on Fridays')",
      "confidence": 0.0 to 1.0,
      "category": "work|personal|health|schedule",
      "entities": ["entity1"]
    }}
  ]
}}"""


class PatternGeneralizer:
    def __init__(self):
        self._model = settings.memory_extraction_model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def run_pass(self, recent_memories: List[Memory]) -> List[Memory]:
        """
        Analyze recent memories and return newly synthesized PATTERN memories.
        """
        if not recent_memories:
            return []

        # Filter to facts and preferences
        relevant = [
            m
            for m in recent_memories
            if m.type in (MemoryType.FACT, MemoryType.PREFERENCE)
        ]
        if len(relevant) < 3:
            return []  # Need at least a few to form a pattern

        lines = [f"- {m.type.value.upper()}: {m.content}" for m in relevant]
        prompt = _PATTERN_PROMPT.format(memories="\n".join(lines))

        try:
            client = self._get_client()
            response = client.messages.create(
                model=self._model,
                max_tokens=512,
                system=_PATTERN_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_json = response.content[0].text.strip()

            clean = raw_json
            if clean.startswith("```"):
                clean = "\n".join(clean.split("\n")[1:-1])

            data = json.loads(clean)

            new_patterns = []
            now = datetime.utcnow()
            for p in data.get("patterns", []):
                content = p.get("content", "").strip()
                if not content:
                    continue
                new_patterns.append(
                    Memory(
                        id=str(uuid.uuid4()),
                        type=MemoryType.PATTERN,
                        content=content,
                        entities=p.get("entities", []),
                        category=p.get("category", "general"),
                        confidence=float(p.get("confidence", 0.7)),
                        importance=0.8,  # Patterns are inherently important
                        source=MemorySource.INFERRED,
                        created_at=now,
                    )
                )
            return new_patterns
        except Exception as e:
            logger.warning(f"PatternGeneralizer failed: {e}")
            return []
