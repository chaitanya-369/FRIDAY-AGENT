"""
friday/memory/graph.py

KnowledgeGraph — Tier 2b of the FRIDAY Memory Mesh.

A NetworkX directed, weighted multigraph backed by EntityRow/RelationshipRow
in SQLite. The graph lives hot in RAM; all writes are persisted to SQLite first,
then reflected in-memory.

Design:
  - Nodes  → EntityRow records (people, projects, tools, concepts, places)
  - Edges  → RelationshipRow records (typed, weighted, temporal)
  - Graph is loaded from SQLite at construction time (~5ms for hundreds of nodes)
  - Thread-safe reads; writes use a threading.Lock

Graph capabilities:
  1. get_neighbors()         — 1-hop: "who does Boss work with?"
  2. get_subgraph_context()  — formatted entity card for prompt injection
  3. find_entity_memories()  — all SQLite memories mentioning an entity
  4. get_central_entities()  — most-connected nodes (Boss's key people)
  5. multi_hop_paths()       — "how is X connected to Y?"
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from friday.core.database import engine
from friday.memory.schema import EntityRow, RelationshipRow
from friday.memory.types import Entity


class KnowledgeGraph:
    """
    NetworkX-backed relational graph over EntityRow / RelationshipRow.

    Usage:
        kg = KnowledgeGraph(episode_store)
        kg.load_from_db()
        ctx = kg.get_subgraph_context("Priya")
    """

    # Relationship types — canonical vocabulary
    REL_KNOWS = "KNOWS"
    REL_WORKS_ON = "WORKS_ON"
    REL_REPORTS_TO = "REPORTS_TO"
    REL_MANAGES = "MANAGES"
    REL_PART_OF = "PART_OF"
    REL_USES = "USES"
    REL_MENTIONED_IN = "MENTIONED_IN"
    REL_CREATED = "CREATED"
    REL_BLOCKED_BY = "BLOCKED_BY"
    REL_SUPERSEDES = "SUPERSEDES"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._graph = None  # lazy-init networkx DiGraph
        self._loaded = False

    # ── Initialisation ────────────────────────────────────────────────────────

    def _get_graph(self):
        """Lazy-init NetworkX graph on first use."""
        if self._graph is None:
            try:
                import networkx as nx  # noqa: PLC0415

                self._graph = nx.MultiDiGraph()
            except ImportError:
                raise RuntimeError(
                    "networkx is not installed. Run: pip install networkx"
                )
        return self._graph

    def load_from_db(self) -> None:
        """
        Load all EntityRow and RelationshipRow records from SQLite into
        the in-memory NetworkX graph. Call once at MemoryBus startup.
        """
        G = self._get_graph()
        with self._lock:
            try:
                with Session(engine) as db:
                    # Load entities as nodes
                    entities = db.exec(select(EntityRow)).all()
                    for e in entities:
                        attrs = e.get_attributes()
                        G.add_node(
                            e.name,
                            entity_id=e.id,
                            entity_type=e.type,
                            **attrs,
                        )

                    # Load relationships as edges
                    relationships = db.exec(select(RelationshipRow)).all()
                    for r in relationships:
                        # We need entity names for edge endpoints
                        from_ent = db.get(EntityRow, r.from_entity_id)
                        to_ent = db.get(EntityRow, r.to_entity_id)
                        if from_ent and to_ent:
                            rel_attrs = r.get_attributes()
                            G.add_edge(
                                from_ent.name,
                                to_ent.name,
                                key=r.id,
                                relation_type=r.relation_type,
                                weight=r.weight,
                                confidence=r.confidence,
                                **rel_attrs,
                            )
                self._loaded = True
            except Exception:
                pass  # Fail silently — KG is best-effort

    # ── Entity operations ─────────────────────────────────────────────────────

    def upsert_entity(
        self,
        name: str,
        entity_type: str = "concept",
        attributes: Optional[dict] = None,
    ) -> Optional[Entity]:
        """
        Add or update an entity node in the graph and SQLite.

        Returns the Entity dataclass, or None on failure.
        """
        attrs = attributes or {}
        try:
            with Session(engine) as db:
                existing = db.exec(
                    select(EntityRow).where(EntityRow.name == name)
                ).first()

                if existing:
                    # Merge attributes (new values overwrite old)
                    old_attrs = existing.get_attributes()
                    old_attrs.update(attrs)
                    existing.set_attributes(old_attrs)
                    existing.last_seen = datetime.utcnow()
                    if entity_type != "concept":  # Don't downgrade type
                        existing.type = entity_type
                    db.add(existing)
                    db.commit()
                    db.refresh(existing)
                    entity_id = existing.id
                    merged_attrs = old_attrs
                else:
                    entity_id = str(uuid.uuid4())
                    row = EntityRow(
                        id=entity_id,
                        name=name,
                        type=entity_type,
                        created_at=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                    )
                    row.set_attributes(attrs)
                    db.add(row)
                    db.commit()
                    merged_attrs = attrs

            # Update in-memory graph
            with self._lock:
                G = self._get_graph()
                G.add_node(
                    name, entity_id=entity_id, entity_type=entity_type, **merged_attrs
                )

            return Entity(
                id=entity_id,
                name=name,
                type=entity_type,
                attributes=merged_attrs,
                created_at=datetime.utcnow(),
            )
        except Exception:
            return None

    def get_entity(self, name: str) -> Optional[Entity]:
        """Retrieve an entity by name from SQLite."""
        try:
            with Session(engine) as db:
                row = db.exec(select(EntityRow).where(EntityRow.name == name)).first()
                if row:
                    return Entity(
                        id=row.id,
                        name=row.name,
                        type=row.type,
                        attributes=row.get_attributes(),
                        created_at=row.created_at,
                        last_seen=row.last_seen,
                    )
        except Exception:
            pass
        return None

    # ── Relationship operations ───────────────────────────────────────────────

    def upsert_relationship(
        self,
        from_name: str,
        to_name: str,
        relation_type: str,
        weight: float = 1.0,
        attributes: Optional[dict] = None,
        confidence: float = 1.0,
    ) -> Optional[str]:
        """
        Add or strengthen a typed relationship between two entities.

        If a relationship of the same type already exists between these
        entities, its weight is averaged upward (reinforcement learning).

        Returns relationship ID or None on failure.
        """
        attrs = attributes or {}
        try:
            # Ensure both entity nodes exist
            from_entity = self.get_entity(from_name)
            to_entity = self.get_entity(to_name)

            if not from_entity:
                from_entity = self.upsert_entity(from_name)
            if not to_entity:
                to_entity = self.upsert_entity(to_name)

            if not from_entity or not to_entity:
                return None

            with Session(engine) as db:
                # Check for existing relationship of same type
                existing = db.exec(
                    select(RelationshipRow)
                    .where(RelationshipRow.from_entity_id == from_entity.id)
                    .where(RelationshipRow.to_entity_id == to_entity.id)
                    .where(RelationshipRow.relation_type == relation_type)
                ).first()

                if existing:
                    # Reinforce — weight creeps toward 1.0
                    existing.weight = min(1.0, (existing.weight + weight) / 2 + 0.05)
                    existing.confidence = min(
                        1.0, (existing.confidence + confidence) / 2 + 0.02
                    )
                    existing.last_updated = datetime.utcnow()
                    old_attrs = existing.get_attributes()
                    old_attrs.update(attrs)
                    existing.attributes_json = json.dumps(old_attrs)
                    db.add(existing)
                    db.commit()
                    rel_id = existing.id
                    final_weight = existing.weight
                else:
                    rel_id = str(uuid.uuid4())
                    row = RelationshipRow(
                        id=rel_id,
                        from_entity_id=from_entity.id,
                        to_entity_id=to_entity.id,
                        relation_type=relation_type,
                        weight=weight,
                        confidence=confidence,
                        created_at=datetime.utcnow(),
                    )
                    row.attributes_json = json.dumps(attrs)
                    db.add(row)
                    db.commit()
                    final_weight = weight

            # Update in-memory graph
            with self._lock:
                G = self._get_graph()
                G.add_edge(
                    from_name,
                    to_name,
                    key=rel_id,
                    relation_type=relation_type,
                    weight=final_weight,
                    confidence=confidence,
                    **attrs,
                )

            return rel_id
        except Exception:
            return None

    # ── Traversal + Context generation ────────────────────────────────────────

    def get_neighbors(self, entity_name: str, depth: int = 1) -> list[str]:
        """Return entity names reachable within `depth` hops."""
        try:
            import networkx as nx  # noqa: PLC0415

            G = self._get_graph()
            if entity_name not in G:
                return []
            with self._lock:
                subgraph_nodes = nx.ego_graph(G, entity_name, radius=depth).nodes()
                return [n for n in subgraph_nodes if n != entity_name]
        except Exception:
            return []

    def get_subgraph_context(self, entity_name: str) -> str:
        """
        Generate a formatted entity card for injection into the LLM prompt.

        Example output:
            [ENTITY: Priya]
            Type: person | Role: manager | Trust: high
            Connections: Boss (REPORTS_TO), FRIDAY project (WORKS_ON)
        """
        try:
            G = self._get_graph()
            if entity_name not in G:
                return ""

            lines = [f"[ENTITY: {entity_name}]"]

            # Node attributes
            node_data = G.nodes[entity_name]
            entity_type = node_data.get("entity_type", "unknown")
            attrs = {
                k: v
                for k, v in node_data.items()
                if k not in ("entity_id", "entity_type")
            }
            attr_str = " | ".join(f"{k}: {v}" for k, v in list(attrs.items())[:5])
            if attr_str:
                lines.append(f"Type: {entity_type} | {attr_str}")
            else:
                lines.append(f"Type: {entity_type}")

            # Outgoing edges
            connections = []
            with self._lock:
                for _, target, edge_data in G.out_edges(entity_name, data=True):
                    rel_type = edge_data.get("relation_type", "RELATES_TO")
                    connections.append(f"{target} ({rel_type})")
                # Incoming edges
                for source, _, edge_data in G.in_edges(entity_name, data=True):
                    rel_type = edge_data.get("relation_type", "RELATES_TO")
                    connections.append(f"{source} →[{rel_type}]→ {entity_name}")

            if connections:
                lines.append(f"Connections: {', '.join(connections[:6])}")

            return "\n".join(lines)
        except Exception:
            return ""

    def get_central_entities(self, top_n: int = 5) -> list[str]:
        """
        Return the most-connected entity names (highest degree centrality).
        These represent Boss's key people, projects, and concepts.
        """
        try:
            import networkx as nx  # noqa: PLC0415

            G = self._get_graph()
            if len(G.nodes) == 0:
                return []
            with self._lock:
                centrality = nx.degree_centrality(G)
            # Sort descending, skip "Boss" itself if present
            ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            return [name for name, _ in ranked[:top_n] if name.lower() != "boss"]
        except Exception:
            return []

    def multi_hop_paths(
        self,
        from_name: str,
        to_name: str,
        max_hops: int = 3,
    ) -> list[list[str]]:
        """
        Find paths between two entity names up to max_hops.
        Returns list of node-name paths. Empty list if no path found.
        """
        try:
            import networkx as nx  # noqa: PLC0415

            G = self._get_graph()
            if from_name not in G or to_name not in G:
                return []
            with self._lock:
                paths = list(
                    nx.all_simple_paths(G, from_name, to_name, cutoff=max_hops)
                )
            return paths[:5]  # return at most 5 paths
        except Exception:
            return []

    def has_entity(self, name: str) -> bool:
        """Return True if an entity with this name exists in the graph."""
        try:
            return name in self._get_graph()
        except Exception:
            return False

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        """Return graph health statistics."""
        try:
            G = self._get_graph()
            return {
                "nodes": len(G.nodes),
                "edges": len(G.edges),
                "loaded": self._loaded,
                "central_entities": self.get_central_entities(3),
            }
        except Exception:
            return {"nodes": 0, "edges": 0, "loaded": False}

    def is_available(self) -> bool:
        """Return True if NetworkX is installed and graph is usable."""
        try:
            import networkx  # noqa: F401, PLC0415

            return True
        except ImportError:
            return False
