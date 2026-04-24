# 🧠 FRIDAY Memory Mesh — Technical Specification

> *"The difference between storing text in ChromaDB and the Memory Mesh is the difference between a USB drive and a human brain."*

**Status: Phase A ✅ + Phase B ✅ — Complete**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Memory Primitives](#memory-primitives)
3. [Tier 0 — Working Memory](#tier-0--working-memory)
4. [Tier 1 — Episode Store](#tier-1--episode-store)
5. [Tier 2a — Vector Store](#tier-2a--vector-store)
6. [Tier 2b — Knowledge Graph](#tier-2b--knowledge-graph-phase-b)
7. [Formation Pipeline](#formation-pipeline)
8. [Intelligence Layer](#intelligence-layer-phase-b)
   - [Entity Linker](#entity-linker)
   - [Conflict Detector](#conflict-detector)
   - [Decay Engine](#decay-engine)
   - [LLM Intent Classifier](#llm-intent-classifier)
9. [Retrieval Pipeline](#retrieval-pipeline)
10. [MemoryBus Public API](#memorybus-public-api)
11. [SQLite Schema](#sqlite-schema)
12. [Configuration Reference](#configuration-reference)
13. [Integration with FridayBrain](#integration-with-fridaybrain)
14. [Testing](#testing)
15. [Roadmap](#roadmap)

---

## Architecture Overview

The Memory Mesh is FRIDAY's multi-tiered, asynchronous, graph-aware intelligence layer. It transforms every conversation into structured, scored, typed memories that persist across sessions, decay gracefully over time, and connect into a relational knowledge graph.

```
┌──────────────────────────────────────────────────────────────┐
│  TIER 0 — Working Memory (RAM)                               │
│  Python deque · <1ms · Session-scoped                        │
│  Sliding window of last 40 turns                             │
└──────────────────────┬───────────────────────────────────────┘
                       │ async background thread
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  ExtractionPipeline (Claude Haiku)                           │
│  Raw turns → typed Memory + Task objects                     │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────┼────────────┬────────────────┐
          ▼            ▼            ▼                ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐
  │ Tier 1   │  │ Tier 2a  │  │ Tier 2b  │  │ ConflictDetect│
  │ SQLite   │  │ ChromaDB │  │ NetworkX │  │ (Phase B)     │
  │ EpisodeStore│ VectorStore│ KnowledgeGraph│              │
  └──────────┘  └──────────┘  └──────────┘  └───────────────┘

              ↑ Background: DecayEngine runs every 24h (APScheduler)
              ↑ Background: EntityLinker wires memories → KG on each consolidation
```

**Retrieval** (before every LLM call):
```
Query → LLMIntentClassifier (LRU cached)
      → [Vector Search] + [SQL Search] + [KG Entity Boost]
      → Merge + Deduplicate + Score Rank
      → MemoryContext → System Prompt Injection
```

---

## Memory Primitives

All memories are strongly typed — never raw text blobs.

### Memory Types

| Type | Example | Decay Rate | Stored In |
|---|---|---|---|
| `fact` | "Boss works at Stark Industries" | Medium (1.0×) | SQLite + ChromaDB |
| `preference` | "Boss prefers dark mode" | Slow (0.5×) | SQLite + ChromaDB |
| `pattern` | "Boss works late on Sundays" | Very slow (0.3×) | SQLite + ChromaDB |
| `relationship` | "Priya is Boss's manager" | Very slow (0.25×) | SQLite + ChromaDB + KG |
| `task` | "Review PR #47 by Friday" | **Never** (0.0×) | SQLite only |
| `episode_ref` | Pointer to raw conversation | Fast (0.8×) | SQLite |

### Memory Score Dimensions

Every memory carries four independent dimensions:

```python
@dataclass
class Memory:
    confidence: float        # 0.0–1.0 — decays via Ebbinghaus curve
    importance: float        # 0.0–1.0 — set at extraction, never decays
    emotional_valence: float # -1.0–+1.0 — negative/positive association
    stability: float         # spaced repetition stability in days
    next_review: datetime    # scheduled review time (decay timing)
```

**Effective retrieval score** (used for ranking):
```
score = confidence × 0.40
      + importance × 0.30
      + |emotional_valence| × 0.20
      + recency_bonus × 0.10
```

**Reinforcement** (on every retrieval):
```python
memory.stability  *= (1 + 0.2 / (1 + access_count))
memory.confidence  = min(1.0, memory.confidence + 0.02)
```

---

## Tier 0 — Working Memory

**File**: `friday/memory/working.py`

Pure RAM — the fastest possible memory tier. A `collections.deque` with a fixed-size sliding window of the current session's conversation turns.

- Holds the last **40 turns** (configurable)
- No I/O — reads and writes are in-memory only
- Tracks `should_consolidate()` → triggers background extraction every 5 turns
- Cleared on session close

---

## Tier 1 — Episode Store

**File**: `friday/memory/episodic.py`

Persistent SQLite storage via SQLModel. The source of truth for all typed memories, tasks, episodes, entities, and relationships.

Key operations:
- `save_memory(memory)` — upsert with spaced-repetition reinforcement on conflict
- `get_recent_memories(hours, limit)` — recency-first retrieval
- `search_by_type(type, limit, min_confidence)` — structured type-filtered query
- `get_active_tasks(limit)` — pending/in-progress tasks sorted by priority
- `soft_delete_memory(id, superseded_by)` — Phase B: mark superseded, preserve audit trail
- `record_conflict(a_id, b_id, type)` → `ConflictRow` — Phase B: contradiction log
- `get_pending_conflicts()` — Phase B: surface unresolved contradictions

---

## Tier 2a — Vector Store

**File**: `friday/memory/vector_store.py`

ChromaDB persistent store for semantic similarity search. FRIDAY embeds memory content at upsert time and retrieves top-N by cosine similarity at query time.

- Stores: content, `memory_type`, `confidence`, `importance`, `emotional_valence`
- Retrieval: `search(query, n_results=20, min_confidence=0.1, memory_type_filter=None)`
- Phase B: `update_confidence(id, new_confidence)` — DecayEngine keeps ChromaDB metadata in sync

---

## Tier 2b — Knowledge Graph (Phase B)

**File**: `friday/memory/graph.py`

A **NetworkX `MultiDiGraph`** loaded hot into RAM at startup from the existing `EntityRow` / `RelationshipRow` SQLite tables. Provides relational reasoning over named entities that flat vector search cannot.

### Graph Structure

- **Nodes** → `EntityRow` records: people, projects, tools, concepts, places
- **Edges** → `RelationshipRow` records with typed labels and weights

### Relationship Vocabulary

| Label | Meaning | Example |
|---|---|---|
| `KNOWS` | Acquaintance / co-mention | "Priya knows Boss" |
| `MANAGES` | Management relation | "Priya manages the team" |
| `REPORTS_TO` | Reporting line | "Boss reports to Priya" |
| `WORKS_ON` | Project ownership | "Boss works on FRIDAY" |
| `USES` | Tool / technology usage | "Boss uses Anthropic" |
| `PART_OF` | Membership / component | "FRIDAY is part of Stark" |
| `CREATED` | Authorship | "Boss created FRIDAY" |
| `BLOCKED_BY` | Dependency / blocker | "Task X blocked by task Y" |

### Reinforcement Averaging

When the same relationship is extracted multiple times, weight **averages upward** rather than duplicating:
```python
existing.weight = min(1.0, (existing.weight + new_weight) / 2 + 0.05)
```

### Context Card for Prompt Injection

For ENTITY-intent queries, FRIDAY generates a formatted entity card:
```
[ENTITY: Priya]
Type: person | role: manager | last_source: text
Connections: Boss (REPORTS_TO), FRIDAY Project (WORKS_ON), Anthropic (USES)
```

### API

```python
kg = KnowledgeGraph()
kg.load_from_db()                          # startup: load SQLite → NetworkX RAM
kg.upsert_entity(name, type, attributes)  # add/update node
kg.upsert_relationship(from, to, type, weight, confidence)  # add/strengthen edge
kg.get_entity(name) → Entity
kg.get_neighbors(name, depth=1) → list[str]
kg.get_subgraph_context(name) → str        # formatted prompt card
kg.get_central_entities(top_n=5) → list[str]  # degree centrality
kg.multi_hop_paths(from, to, max_hops=3) → list[list[str]]
kg.stats() → dict                          # nodes, edges, loaded, central
```

---

## Formation Pipeline

**File**: `friday/memory/extraction/pipeline.py`

Fires in a **background daemon thread** every 5 turns — never on the critical path.

```
Working Memory (raw turns)
        │
        ▼
ExtractionPipeline.extract(turns)
  └── Claude Haiku call (~$0.0002/run)
      JSON schema → Memory + Task objects
        │
        ▼
EpisodeStore.save_memory()      → Tier 1: SQLite
VectorStore.upsert_many()       → Tier 2a: ChromaDB
EntityLinker.link()             → Tier 2b: KnowledgeGraph  [Phase B]
ConflictDetector.scan()         → ConflictRow if needed    [Phase B]
```

---

## Intelligence Layer (Phase B)

### Entity Linker

**File**: `friday/memory/extraction/entity_linker.py`

Post-extraction step that wires freshly extracted `Memory` objects into the Knowledge Graph — no LLM call needed.

**Type inference** (heuristic):
- Title words (Mr, Dr, CEO, Manager) → `person`
- Tool keywords (v1.0, SDK, API, framework) → `tool`
- CamelCase single word → `project`
- Default → `concept`

**Relationship inference** (pattern-matching on memory content):
- "manages / is the lead of" → `MANAGES`
- "reports to / works under" → `REPORTS_TO`
- "works on / owns" → `WORKS_ON`
- "uses / built / developed" → `USES`
- Default → `KNOWS`

**Co-mention edges**: any two entities appearing in the same non-relationship memory receive a weak `KNOWS` edge (weight=0.3, confidence=0.6).

---

### Conflict Detector

**File**: `friday/memory/conflict.py`

Runs in the same background consolidation thread immediately after memories are saved. **Cost-controlled** — max 8 LLM judge calls per batch.

**Detection**:
1. For each new memory, vector-search for top-6 similar existing memories of the **same type**
2. Filter: cosine similarity > 0.82
3. For each candidate pair → Claude Haiku judge call

**Classification verdicts**:

| Verdict | Meaning | Auto-Resolution |
|---|---|---|
| `SUPERSESSION` | B is an update/correction of A | Soft-delete older; confidence=1.0 on newer |
| `CONTRADICTION` | They assert opposing facts | Record `ConflictRow`; reduce both to confidence=0.6 |
| `COMPLEMENTARY` | Related but not conflicting | No action |

**Heuristic fallback** (if LLM judge fails):
- Jaccard word overlap > 0.7 + different content → `SUPERSESSION`
- Negation keyword pairs ("is" / "is not") → `CONTRADICTION`
- Default → `COMPLEMENTARY`

Contradictions are surfaced in `MemoryContext.conflicts` and shown to FRIDAY before her next response.

---

### Decay Engine

**File**: `friday/memory/decay.py`

Applies the **Ebbinghaus forgetting curve** to all memories on a background schedule.

**Formula**:
```
R(t) = confidence × e^(-t × decay_rate / S)

Where:
  t             = elapsed days since last access
  S             = stability score (days; increases with repeated access)
  decay_rate    = per-type multiplier (TASK=0, RELATIONSHIP=0.25, FACT=1.0)
```

**Decay rates by type**:

| Type | Rate | Default Stability | Effective half-life |
|---|---|---|---|
| `task` | 0.0 | ∞ | Never decays |
| `relationship` | 0.25 | 30 days | ~83 days |
| `pattern` | 0.3 | 14 days | ~32 days |
| `preference` | 0.5 | 10 days | ~14 days |
| `episode_ref` | 0.8 | 3 days | ~2.6 days |
| `fact` | 1.0 | 2 days | ~1.4 days |

**Archival**: memories below **confidence=0.15** are archived — excluded from retrieval, preserved in SQLite for audit.

**Scheduler**: `APScheduler BackgroundScheduler` (daemon thread). First pass runs 60s after startup. Subsequent passes run every `MEMORY_DECAY_INTERVAL_HOURS` (default: 24h).

**Manual trigger** (Boss command):
```python
report = bus.run_decay_now()
# → {"total_checked": 42, "total_decayed": 18, "total_archived": 2, ...}
```

---

### LLM Intent Classifier

**File**: `friday/memory/retrieval/intent.py`

Replaces keyword heuristics with a **Claude Haiku few-shot classifier**, LRU-cached so identical queries never make a second API call.

**Intent vocabulary**:

| Intent | Triggers retrieval of... | Example queries |
|---|---|---|
| `task` | Task memories, active todos | "what tasks are pending?" |
| `episodic` | Recent episode history (72h window) | "when did we last discuss X?" |
| `entity` | KG subgraph + relationship memories | "what do you know about Priya?" |
| `semantic` | Preferences, patterns, habits | "what do I usually prefer?" |
| `predictive` | High-importance facts + all tasks | "what should I focus on?" |
| `general` | Standard vector + SQL | Conversational queries |

**Cache**: in-process `dict[normalized_query → intent]`, max 256 entries, FIFO eviction.

**Fallback**: full keyword classifier runs if the LLM call fails — guaranteed non-raising.

---

## Retrieval Pipeline

**File**: `friday/memory/retrieval/engine.py`

```python
engine = RetrievalEngine(episode_store, vector_store)
engine.set_intent_classifier(LLMIntentClassifier())  # Phase B
engine.set_graph(KnowledgeGraph())                   # Phase B

ctx = engine.retrieve(query="what should I work on?", intent="task")
```

**Three parallel retrieval paths**:

| Path | Source | Trigger | Score boost |
|---|---|---|---|
| Vector | ChromaDB | All intents | Base `combined_score()` |
| SQL | SQLite | All intents (preferences + high-importance + recent) | +0.15 if cross-path hit |
| KG | NetworkX | ENTITY intent only | +0.20 for entity-linked memories |

**Intent-specific SQL additions**:

| Intent | Extra SQL |
|---|---|
| `task` | `search_by_type(TASK)` |
| `entity` | `search_by_type(RELATIONSHIP)` |
| `episodic` | `get_recent_memories(hours=72)` (expanded window) |
| `predictive` | `FACT` memories with `importance >= 0.7` |

---

## MemoryBus Public API

**File**: `friday/memory/__init__.py`

`MemoryBus` is the **single public interface** for all memory operations. `FridayBrain` never touches individual tiers directly.

```python
bus = MemoryBus()  # initialised once in FridayBrain.__init__()

# ── Critical path (called every turn) ────────────────────────────────────────
ctx: MemoryContext = bus.get_context_for(query: str)
bus.observe_turn(user_input: str, assistant_response: str)

# ── Background (off critical path) ───────────────────────────────────────────
bus.consolidate_session_async(turns: list[dict])   # fire-and-forget
bus.close_session(turns: list[dict])               # on disconnect / reset

# ── Direct access (tools, autopilot, introspection) ──────────────────────────
tasks:    list[Task]   = bus.get_active_tasks()
stats:    dict         = bus.get_stats()
memories: list[Memory] = bus.search(query: str, limit: int = 10)
success:  bool         = bus.forget(memory_id: str)

# ── Phase B additions ─────────────────────────────────────────────────────────
entity_card:    str        = bus.get_entity_context(entity_name: str)
conflicts:      list[dict] = bus.get_conflict_report()
decay_report:   dict       = bus.run_decay_now()
bus.shutdown()              # graceful APScheduler stop
```

**`get_stats()` returns** (Phase B extended):
```python
{
    "enabled": True,
    "session_id": "...",
    "session_turns": 12,
    "total_memories": 147,
    "active_memories": 131,
    "avg_confidence": 0.74,
    "memories_by_type": {"fact": 89, "preference": 21, ...},
    "active_tasks": 4,
    "total_episodes": 18,
    "vector_store_count": 131,
    "knowledge_graph": {
        "nodes": 23,
        "edges": 41,
        "loaded": True,
        "central_entities": ["Priya", "FRIDAY", "Anthropic"]
    },
    "intent_cache": {"cached_intents": 14, "max_cache": 256},
    "last_decay_pass": {
        "run_at": "2026-04-23T08:00:00",
        "total_checked": 131,
        "total_decayed": 48,
        "total_archived": 2,
        "avg_confidence_before": 0.81,
        "avg_confidence_after": 0.74
    }
}
```

---

## SQLite Schema

**File**: `friday/memory/schema.py`

10 tables auto-created by SQLModel on first startup.

| Table | Purpose |
|---|---|
| `memories` | Core typed memory units with all scoring dimensions |
| `tasks` | Structured actionable items (priority, status, due date) |
| `episodes` | Conversation sessions with LLM-generated summaries |
| `entities` | KG nodes — people, projects, tools, concepts |
| `relationships` | KG edges — typed, weighted, confidence-scored |
| `memory_conflicts` | Detected contradictions pending resolution |
| `llm_providers` | Registered LLM provider records |
| `api_keys` | Health-tracked key pool per provider |
| `model_entries` | Model catalog per provider |
| `active_session` | Currently active (provider, model) selection |

---

## Configuration Reference

All settings live in `friday/config/settings.py` and are loaded from `.env`.

```env
# ── Phase A ──────────────────────────────────────────────────────────────────
MEMORY_ENABLED=true
CHROMADB_PATH=data/vectors
MEMORY_EXTRACTION_MODEL=claude-haiku-4-5-20251001
MEMORY_CONTEXT_TOKEN_BUDGET=1200
MEMORY_MAX_FACTS=5
MEMORY_MAX_PREFERENCES=5
MEMORY_MAX_TASKS=5

# ── Phase B ──────────────────────────────────────────────────────────────────
MEMORY_DECAY_INTERVAL_HOURS=24.0
MEMORY_CONFLICT_SIMILARITY_THRESHOLD=0.82
MEMORY_INTENT_CLASSIFIER_ENABLED=true
MEMORY_KG_MAX_NODES=500
MEMORY_CONFLICT_MAX_CHECKS=8
```

---

## Integration with FridayBrain

Memory integrates non-intrusively into the streaming pipeline:

```python
# brain.py — stream_process() augmented with Memory Mesh

def stream_process(self, user_input):
    # 1. [NEW] Retrieve ranked memory context (50–200ms, LRU-cached intent)
    mem_ctx = self.memory.get_context_for(user_input)
    memory_string = mem_ctx.to_prompt_string()

    # 2. Build system prompt with memory injection
    system = self._get_system_prompt(memory_string)

    # 3. Stream LLM
    for chunk in self.llm.stream(system=system, ...):
        yield chunk

    # 4. [NEW] Buffer turn in working memory (RAM only, instant)
    self.memory.observe_turn(user_input, full_response)

    # 5. [NEW] Background consolidation every 5 turns
    if self.memory.working.should_consolidate():
        self.memory.consolidate_session_async(conversation_history)
```

**Critical contract**: Memory failure is always silent. Every operation is wrapped in `try/except` — no memory bug can ever crash `FridayBrain`.

---

## Testing

```bash
# Full Phase A + B smoke test
python -c "
from friday.memory import MemoryBus
bus = MemoryBus()
print('MemoryBus stats:', bus.get_stats())
"

# KG smoke test
python -c "
from friday.memory.graph import KnowledgeGraph
kg = KnowledgeGraph()
kg.load_from_db()
e = kg.upsert_entity('Priya', entity_type='person', attributes={'role': 'manager'})
print('Entity:', e)
print('KG stats:', kg.stats())
"

# Intent classifier (keyword mode — no API key needed)
python -c "
from friday.memory.retrieval.intent import LLMIntentClassifier
clf = LLMIntentClassifier()
clf.disable_llm()
queries = [
    'what tasks are pending?',
    'what do you know about Priya?',
    'when did we last talk about the project?',
    'what should I focus on?',
    'hello'
]
for q in queries:
    print(f'  [{clf.classify(q):12s}] {q}')
"

# Decay pass
python -c "
from friday.memory.decay import DecayEngine
from friday.memory.episodic import EpisodeStore
from friday.memory.vector_store import VectorStore
report = DecayEngine(EpisodeStore(), VectorStore()).run_decay_pass()
print('Decay:', report.to_dict())
"
```

---

## Roadmap

### ✅ Phase A — Foundation (Complete)
- Typed memory primitives and SQLite schema (10 tables)
- Working Memory (RAM), EpisodeStore (SQLite), VectorStore (ChromaDB)
- ExtractionPipeline (Claude Haiku → typed JSON → Memory objects)
- Multi-modal retrieval (vector + SQL) with keyword intent classification
- Full `MemoryBus` facade wired into `FridayBrain`

### ✅ Phase B — Intelligence Layer (Complete)
- **KnowledgeGraph** — NetworkX MultiDiGraph backed by SQLite; multi-hop reasoning
- **EntityLinker** — heuristic entity type inference + typed KG edge creation
- **ConflictDetector** — vector similarity trigger + Claude Haiku judge + auto-resolution
- **DecayEngine** — Ebbinghaus curve + APScheduler background daemon + archival
- **LLMIntentClassifier** — Claude Haiku few-shot + LRU cache + keyword fallback
- **RetrievalEngine Phase B** — 3rd KG path + PREDICTIVE intent + EPISODIC 72h window
- **MemoryBus Phase B** — full wiring, new Phase B public methods, extended stats

### ✅ Phase C — Superhuman Memory (Complete)
- **Pattern Generalizer** — Claude Haiku synthesizes recurring behavioral patterns from facts/preferences every 48h.
- **Proactive Preloader** — Anticipatory background memory loading for upcoming calendar events/tasks.
- **Memory Audit API** — Self-surgery tool routing (`MemorySearchTool`, `MemoryUpdateTool`, `MemoryDeleteTool`) for direct memory maintenance.
- **Supabase Archive** — Asynchronous cloud backup for completed episodes (metrics and metadata).

---

*Part of the FRIDAY Agent — [github.com/chaitanya-369/FRIDAY-AGENT](https://github.com/chaitanya-369/FRIDAY-AGENT)*
