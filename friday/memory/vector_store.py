"""
friday/memory/vector_store.py

VectorStore — half of Tier 2 (Semantic Core) in the FRIDAY Memory Mesh.

Uses ChromaDB in embedded/persistent mode (no external server needed).
Each memory is stored as:
  - document text (the memory content)
  - embedding (auto-computed by ChromaDB's default embedding function)
  - rich metadata (type, category, confidence, importance, emotional_valence, etc.)

Metadata is stored alongside vectors so reranking can happen purely
in Python without a second DB round-trip.

Design notes:
  - Collection name: "friday_memory_v1"
  - ChromaDB uses sentence-transformers by default for embeddings
    (all-MiniLM-L6-v2, runs locally, no API key needed)
  - Updates are upserts — same ID always overwrites
"""

from __future__ import annotations

import os
from typing import Optional

from friday.config.settings import settings
from friday.memory.types import Memory, MemoryType


class VectorStore:
    """
    Tier 2a — Semantic vector index over all memory content.

    Enables similarity search across the full memory corpus.
    Used by RetrievalEngine as one of three parallel search paths.
    """

    COLLECTION_NAME = "friday_memory_v1"
    DEFAULT_N_RESULTS = 10

    def __init__(self) -> None:
        self._client = None
        self._collection = None

    def _ensure_init(self) -> None:
        """Lazy-init ChromaDB so it doesn't block startup if not needed."""
        if self._collection is not None:
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            # Ensure the data directory exists
            os.makedirs(settings.chromadb_path, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=settings.chromadb_path,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},  # cosine similarity
            )
        except ImportError:
            raise RuntimeError(
                "chromadb is not installed. Run: pip install chromadb>=0.5.0"
            )

    # ── Write operations ──────────────────────────────────────────────────────

    def upsert(self, memory: Memory) -> None:
        """
        Add or update a memory in the vector index.

        Metadata stored alongside the vector enables fast reranking
        without secondary DB queries.
        """
        self._ensure_init()

        metadata = {
            "type": memory.type.value,
            "category": memory.category,
            "confidence": memory.confidence,
            "importance": memory.importance,
            "emotional_valence": memory.emotional_valence,
            "stability": memory.stability,
            "source": memory.source.value,
            "created_at": memory.created_at.isoformat(),
            "access_count": memory.access_count,
            "entities": ",".join(memory.entities),  # ChromaDB requires str metadata
        }

        self._collection.upsert(
            ids=[memory.id],
            documents=[memory.content],
            metadatas=[metadata],
        )

    def upsert_many(self, memories: list[Memory]) -> None:
        """Batch upsert for efficiency during consolidation."""
        if not memories:
            return
        self._ensure_init()

        ids = []
        documents = []
        metadatas = []

        for memory in memories:
            ids.append(memory.id)
            documents.append(memory.content)
            metadatas.append(
                {
                    "type": memory.type.value,
                    "category": memory.category,
                    "confidence": memory.confidence,
                    "importance": memory.importance,
                    "emotional_valence": memory.emotional_valence,
                    "stability": memory.stability,
                    "source": memory.source.value,
                    "created_at": memory.created_at.isoformat(),
                    "access_count": memory.access_count,
                    "entities": ",".join(memory.entities),
                }
            )

        self._collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def delete(self, memory_id: str) -> None:
        """Remove a memory from the vector index."""
        self._ensure_init()
        try:
            self._collection.delete(ids=[memory_id])
        except Exception:
            pass  # Ignore if not found

    # ── Search operations ─────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        n_results: int = DEFAULT_N_RESULTS,
        *,
        memory_type: Optional[MemoryType] = None,
        min_confidence: float = 0.1,
        category: Optional[str] = None,
    ) -> list[VectorSearchResult]:
        """
        Semantic similarity search over all stored memories.

        Returns results sorted by cosine distance (closest first).
        Applies metadata filters for type, confidence, and category.
        """
        self._ensure_init()

        # Build ChromaDB where clause
        where_clauses: list[dict] = [
            {"confidence": {"$gte": min_confidence}},
        ]
        if memory_type:
            where_clauses.append({"type": {"$eq": memory_type.value}})
        if category:
            where_clauses.append({"category": {"$eq": category}})

        # ChromaDB requires $and wrapper for multiple conditions
        where = (
            {"$and": where_clauses}
            if len(where_clauses) > 1
            else where_clauses[0]
            if where_clauses
            else None
        )

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, self._collection.count() or 1),
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            # Collection might be empty
            return []

        # Unpack results
        search_results = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            for memory_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
                # Convert cosine distance to similarity score (0–1)
                similarity = 1.0 - dist
                search_results.append(
                    VectorSearchResult(
                        memory_id=memory_id,
                        content=doc,
                        similarity=similarity,
                        metadata=meta,
                    )
                )

        return search_results

    def count(self) -> int:
        """Return the total number of memories in the vector index."""
        self._ensure_init()
        try:
            return self._collection.count()
        except Exception:
            return 0

    def is_available(self) -> bool:
        """Return True if ChromaDB is installed and the collection is accessible."""
        try:
            self._ensure_init()
            return self._collection is not None
        except RuntimeError:
            return False


# ── Result dataclass ──────────────────────────────────────────────────────────


class VectorSearchResult:
    """A single result from a vector similarity search."""

    __slots__ = ("memory_id", "content", "similarity", "metadata")

    def __init__(
        self,
        memory_id: str,
        content: str,
        similarity: float,
        metadata: dict,
    ) -> None:
        self.memory_id = memory_id
        self.content = content
        self.similarity = similarity
        self.metadata = metadata

    def get_type(self) -> MemoryType:
        return MemoryType(self.metadata.get("type", "fact"))

    def get_confidence(self) -> float:
        return float(self.metadata.get("confidence", 1.0))

    def get_importance(self) -> float:
        return float(self.metadata.get("importance", 0.5))

    def get_emotional_valence(self) -> float:
        return float(self.metadata.get("emotional_valence", 0.0))

    def combined_score(self) -> float:
        """
        Combined score for reranking:
          35% vector similarity + 30% confidence + 20% importance + 15% emotional salience
        """
        return (
            self.similarity * 0.35
            + self.get_confidence() * 0.30
            + self.get_importance() * 0.20
            + abs(self.get_emotional_valence()) * 0.15
        )

    def __repr__(self) -> str:
        return (
            f"VectorSearchResult(id={self.memory_id[:8]}..., "
            f"sim={self.similarity:.3f}, score={self.combined_score():.3f})"
        )
