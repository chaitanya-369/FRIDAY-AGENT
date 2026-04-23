"""
friday/memory/extraction/entity_linker.py

EntityLinker — post-extraction step that connects freshly extracted
Memory objects to canonical Knowledge Graph nodes.

How it works:
  1. After ExtractionPipeline runs, MemoryBus calls link() with the
     new memories and the KnowledgeGraph instance.
  2. EntityLinker iterates every entity name listed in memory.entities.
  3. For each entity name:
     a. Upsert an EntityRow in the KG (deduplicated by name)
     b. Infer entity type from context clues (person/project/tool/concept)
  4. For RELATIONSHIP-type memories specifically:
     - Parse the relationship direction from the memory content
     - Create a typed RelationshipRow between the two entities

Entity type inference rules (heuristic, no LLM needed):
  - Contains title words (Mr/Mrs/Dr/Prof) → person
  - Contains tool/framework/library keywords → tool
  - Contains version numbers → tool
  - CamelCase proper noun without spaces → project or tool
  - Otherwise → concept (fallback)

Relationship inference rules (pattern-based for common phrases):
  - "X is Y's manager/boss/lead" → X MANAGES Y
  - "X reports to Y"            → X REPORTS_TO Y
  - "X works on Y" / "X owns Y" → X WORKS_ON Y
  - "X uses Y" / "X built Y"   → X USES Y
  - Default for RELATIONSHIP memory → X KNOWS Y
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from friday.memory.types import Memory, MemoryType

if TYPE_CHECKING:
    from friday.memory.graph import KnowledgeGraph

# ── Type inference patterns ───────────────────────────────────────────────────

_PERSON_SIGNALS = re.compile(
    r"\b(Mr|Mrs|Ms|Dr|Prof|Sir|Captain|Director|CEO|CTO|VP|Engineer|"
    r"Developer|Designer|Manager|Lead|Head|Founder|Boss)\b",
    re.IGNORECASE,
)
_TOOL_SIGNALS = re.compile(
    r"\b(v\d+|\d+\.\d+|js|py|sdk|api|cli|lib|library|framework|platform|"
    r"database|db|cloud|saas|tool|service|app|plugin|extension|module)\b",
    re.IGNORECASE,
)

# ── Relationship inference patterns ──────────────────────────────────────────

_REL_PATTERNS: list[tuple[re.Pattern, str, bool]] = [
    # (pattern, relation_type, reversed_direction)
    (
        re.compile(
            r"\b(manages?|is the (lead|head|boss) of|directs?)\b", re.IGNORECASE
        ),
        "MANAGES",
        False,
    ),
    (
        re.compile(r"\b(reports? to|works? (for|under))\b", re.IGNORECASE),
        "REPORTS_TO",
        False,
    ),
    (
        re.compile(r"\b(works? on|owns?|is responsible for|leads?)\b", re.IGNORECASE),
        "WORKS_ON",
        False,
    ),
    (
        re.compile(
            r"\b(uses?|builds?|built|created?|developed?|maintains?)\b", re.IGNORECASE
        ),
        "USES",
        False,
    ),
    (
        re.compile(r"\b(is part of|belongs? to|member of)\b", re.IGNORECASE),
        "PART_OF",
        False,
    ),
    (
        re.compile(
            r"\b(knows?|met|introduced?|works? with|collaborates?)\b", re.IGNORECASE
        ),
        "KNOWS",
        False,
    ),
]


def _infer_entity_type(name: str, context: str) -> str:
    """Infer entity type from name and surrounding context."""
    full_text = f"{name} {context}"
    if _PERSON_SIGNALS.search(full_text) or (
        name[0].isupper() and " " in name and not any(c.isdigit() for c in name)
    ):
        return "person"
    if _TOOL_SIGNALS.search(full_text):
        return "tool"
    if name[0].isupper() and " " not in name and len(name) > 2:
        # CamelCase single word → likely a project or tool
        return "project"
    return "concept"


def _infer_relation_type(content: str) -> str:
    """Infer the canonical relationship type from memory content."""
    for pattern, rel_type, _ in _REL_PATTERNS:
        if pattern.search(content):
            return rel_type
    return "KNOWS"


# ── EntityLinker ──────────────────────────────────────────────────────────────


class EntityLinker:
    """
    Connects freshly-extracted Memory objects to canonical Knowledge Graph nodes.

    Thread-safe: each call to link() is independent and self-contained.
    Always fails silently — KG enrichment is best-effort.
    """

    def link(
        self,
        memories: list[Memory],
        graph: "KnowledgeGraph",
    ) -> list[str]:
        """
        Process all entity names in the given memories and upsert them
        into the Knowledge Graph.

        Returns list of entity names successfully upserted.
        """
        if not graph.is_available():
            return []

        linked: list[str] = []

        for memory in memories:
            if not memory.entities:
                continue

            try:
                # Upsert each entity mentioned in this memory
                for entity_name in memory.entities:
                    if not entity_name or len(entity_name) < 2:
                        continue

                    entity_type = _infer_entity_type(entity_name, memory.content)

                    # Build attributes from memory metadata
                    attrs: dict = {"category": memory.category}
                    if memory.source:
                        attrs["last_source"] = memory.source.value

                    graph.upsert_entity(
                        entity_name, entity_type=entity_type, attributes=attrs
                    )
                    linked.append(entity_name)

                # For RELATIONSHIP memories: create an edge between the entities
                if memory.type == MemoryType.RELATIONSHIP and len(memory.entities) >= 2:
                    self._link_relationship(memory, graph)

                # For any memory with 2+ entities: create a weak MENTIONED_IN edge
                elif len(memory.entities) >= 2:
                    self._link_co_mention(memory, graph)

            except Exception:
                continue  # Always silent fail

        return linked

    def _link_relationship(self, memory: Memory, graph: "KnowledgeGraph") -> None:
        """Create a typed relationship edge for a RELATIONSHIP-type memory."""
        try:
            entities = memory.entities[:2]  # primary pair
            from_name, to_name = entities[0], entities[1]
            rel_type = _infer_relation_type(memory.content)

            graph.upsert_relationship(
                from_name=from_name,
                to_name=to_name,
                relation_type=rel_type,
                weight=memory.importance,
                confidence=memory.confidence,
                attributes={"source_memory": memory.id},
            )
        except Exception:
            pass

    def _link_co_mention(self, memory: Memory, graph: "KnowledgeGraph") -> None:
        """Create weak KNOWS edges for entities co-mentioned in a non-relationship memory."""
        try:
            entities = memory.entities[:3]  # limit to first 3 to avoid over-linking
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    graph.upsert_relationship(
                        from_name=entities[i],
                        to_name=entities[j],
                        relation_type="KNOWS",
                        weight=0.3,  # weak co-mention weight
                        confidence=0.6,
                        attributes={"co_mention": True, "memory_id": memory.id},
                    )
        except Exception:
            pass
