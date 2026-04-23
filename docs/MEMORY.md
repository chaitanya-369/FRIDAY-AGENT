# 🧠 FRIDAY Memory Mesh — Technical Documentation

> *"The difference between this and storing text in ChromaDB is the difference between a human brain and a USB drive."*

---

## Overview

The **Memory Mesh** is FRIDAY's multi-tiered, graph-aware, asynchronous memory system. It transforms FRIDAY from a stateless chatbot wrapper into a persistent, context-aware intelligence that remembers, learns, and reasons across sessions.

Every memory is **typed**, **confidence-scored**, **versioned**, and **graph-connected**. Retrieval is **multi-modal** (vector + SQL in parallel). Formation is **asynchronous** — memory writing never blocks FRIDAY's response stream.

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│  TIER 0 — Working Memory                                         │
│  Python deque (RAM only) · <1ms · Session-scoped                 │
│  Sliding window of last 40 turns + pre-loaded memory candidates  │
└──────────────────────────────┬───────────────────────────────────┘
                               │ session end / overflow
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  TIER 1 — Episode Store                                          │
│  SQLite via SQLModel · <10ms · Persistent                        │
│  Typed memory rows, tasks, episodes, entities, relationships      │
└──────────────────────────────┬───────────────────────────────────┘
                               │ consolidation (async)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  TIER 2 — Semantic Core                                          │
│  ChromaDB (vector) + NetworkX/SQLite (graph) · <100ms            │
│  Semantic similarity search + multi-hop relational reasoning     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Memory Primitives

All memories are strongly typed — never raw text blobs:

| Type | Example | Decay Rate | Storage |
|---|---|---|---|
| `fact` | "Boss works at Company X" | Medium | SQLite + Vector |
| `preference` | "Boss prefers dark themes" | Slow | SQLite + Vector |
| `pattern` | "Boss works late on Sundays" | Very slow | SQLite + Vector |
| `task` | "Review PR #47 by Friday" | On completion | SQLite only |
| `relationship` | "Priya is Boss's manager" | Slow | SQLite + Vector + Graph |
| `episode` | Pointer to raw conversation | Archive | SQLite |

Each memory carries a **multi-dimensional score**:

```python
@dataclass
class Memory:
    confidence: float       # 0.0–1.0  — degrades via Ebbinghaus curve
    importance: float       # 0.0–1.0  — set at extraction, never decays
    emotional_valence: float # -1.0–+1.0 — negative/positive association
    stability: float        # spaced repetition stability score (days)
```

The **effective score** for retrieval ranking:
```
score = confidence × 0.40
      + importance × 0.30
      + |emotional_valence| × 0.20
      + recency_bonus × 0.10
```

---

## File Structure

```
friday/memory/
├── __init__.py              ← MemoryBus — single public facade
├── types.py                 ← Typed dataclasses (Memory, Task, Episode, etc.)
├── schema.py                ← SQLModel table definitions (6 tables)
├── working.py               ← Tier 0: RAM-only sliding window
├── episodic.py              ← Tier 1: SQLite CRUD + spaced repetition
├── vector_store.py          ← Tier 2a: ChromaDB semantic search
│
├── extraction/
│   ├── __init__.py
│   └── pipeline.py          ← Claude Haiku → typed JSON → Memory objects
│
└── retrieval/
    ├── __init__.py
    └── engine.py            ← Multi-modal: vector + SQL, intent classification
```

---

## The Formation Pipeline

When a conversation turn completes, `MemoryBus.consolidate_session_async()` fires in a **background daemon thread**:

```
Raw Conversation Turns
        │
        ▼
┌──────────────────────────┐
│  ExtractionPipeline      │  Claude Haiku (~$0.0002/call)
│                          │
│  Extracts:               │
│  • facts (objective)     │
│  • preferences (inferred)│
│  • tasks (actionable)    │
│  • relationships (social)│
└──────────┬───────────────┘
           │ typed Memory + Task objects
           ▼
┌──────────────────────────┐
│  EpisodeStore.save()     │  Tier 1: SQLite (always)
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  VectorStore.upsert()    │  Tier 2a: ChromaDB (if available)
└──────────────────────────┘
```

**Trigger**: Every 5 user turns (`working.should_consolidate()` returns True).  
**Model used**: `claude-haiku-4-5-20251001` (configurable via `MEMORY_EXTRACTION_MODEL` in `.env`).

---

## The Retrieval Pipeline

Called before every LLM invocation — must be fast:

```
User Input
    │
    ▼
┌──────────────────────────────────────────────┐
│  RetrievalEngine.retrieve(query, intent)      │
│                                              │
│  ┌────────────────┐  ┌──────────────────┐   │
│  │ Vector Search  │  │ SQL Search       │   │
│  │ (ChromaDB)     │  │ top preferences  │   │
│  │ cosine sim     │  │ high-importance  │   │
│  │ top-20 results │  │ recent memories  │   │
│  └────────────────┘  └──────────────────┘   │
│              ↓ merge + deduplicate           │
│         ┌──────────────────┐                 │
│         │  Result Fusion   │                 │
│         │  + score boost   │                 │
│         │  if found in both│                 │
│         └──────────────────┘                 │
└──────────────────────────────────────────────┘
    │
    ▼
MemoryContext.to_prompt_string()
    → injected into FRIDAY system prompt
```

**Typical latency**: 50–200ms (after ChromaDB model download on first run).

---

## The Spaced Repetition Model

Every memory access strengthens it. Non-accessed memories decay.

```python
# On every retrieval — stability increases logarithmically
memory.stability *= (1 + 0.2 / (1 + access_count))
memory.confidence = min(1.0, memory.confidence + 0.02)

# Forgetting curve (implemented in Phase B DecayEngine)
# R = e^(-t / S)   where t = days since access, S = stability
```

**Effect**: A fact mentioned daily stays at ~99% confidence. A one-off mention from 3 months ago fades below 10% and stops being injected into prompts.

---

## SQLite Schema (6 Tables)

| Table | Primary Purpose |
|---|---|
| `memories` | Core typed memory units with scoring dimensions |
| `tasks` | Structured actionable items with priority + status |
| `episodes` | Raw conversation sessions + LLM-generated summaries |
| `entities` | Knowledge graph nodes (people, projects, tools) |
| `relationships` | Typed weighted edges between entities |
| `memory_conflicts` | Detected contradictions pending resolution |

---

## Integration with FridayBrain

Memory integrates non-intrusively into the existing streaming pipeline:

```python
# brain.py — stream_process() augmented flow

def stream_process(self, user_input):
    # 1. Switch command interception (unchanged)

    # 2. [NEW] Retrieve ranked memory context
    mem_ctx = self.memory.get_context_for(user_input)
    memory_context_str = mem_ctx.to_prompt_string()

    # 3. Resolve provider/model (unchanged)

    # 4. Stream LLM with memory-enriched system prompt
    for chunk in self.llm.stream(
        system_prompt=self._get_system_prompt(memory_context_str),
        ...
    ):
        yield chunk

    # 5. [NEW] Buffer completed turn (RAM only, instant)
    self.memory.observe_turn(user_input, response_text)

    # 6. [NEW] Async consolidation every 5 turns (daemon thread)
    if self.memory.working.should_consolidate():
        self.memory.consolidate_session_async(conversation_history)
```

**Critical design rule**: Memory failure is always silent. The `try/except` blocks around every memory operation ensure that no memory bug can ever crash `FridayBrain`.

---

## Public API — `MemoryBus`

```python
bus = MemoryBus()  # initialised once per FridayBrain instance

# Called during conversation (critical path)
ctx: MemoryContext = bus.get_context_for(query: str)
bus.observe_turn(user_input: str, assistant_response: str)

# Called off critical path (background threads)
bus.consolidate_session_async(turns: list[dict])
bus.close_session(turns: list[dict])

# Direct access (for autopilot, tool integrations)
tasks: list[Task] = bus.get_active_tasks()
stats: dict = bus.get_stats()

# Boss-facing introspection
memories: list[Memory] = bus.search(query: str, limit: int)
success: bool = bus.forget(memory_id: str)
```

---

## Configuration (`.env`)

```env
# Memory system (all optional — defaults shown)
MEMORY_ENABLED=true
CHROMADB_PATH=data/vectors
MEMORY_EXTRACTION_MODEL=claude-haiku-4-5-20251001
MEMORY_CONTEXT_TOKEN_BUDGET=1200
MEMORY_MAX_FACTS=5
MEMORY_MAX_PREFERENCES=5
MEMORY_MAX_TASKS=5
MEMORY_DECAY_INTERVAL_HOURS=24
```

---

## Phase Roadmap

### ✅ Phase A — Foundation (Complete)
- Typed memory primitives and SQLite schema
- Working memory (RAM), EpisodeStore (SQLite), VectorStore (ChromaDB)
- Extraction pipeline (Claude Haiku → typed JSON → Memory objects)
- Multi-modal retrieval (vector + SQL) with intent classification
- Full `MemoryBus` facade wired into `FridayBrain`

### 🔄 Phase B — Intelligence Layer (Next)
- **Knowledge Graph** (NetworkX + SQLite persistence) — multi-hop reasoning
- **Entity Linker** — connect extracted facts to named entity graph nodes
- **Conflict Detector** — flag and auto-resolve contradicting memories
- **Decay Engine** — Ebbinghaus forgetting curve background job
- **LLM Intent Classifier** — replace keyword heuristics

### 🔮 Phase C — Superhuman Memory (Future)
- **Pattern Generalizer** — detect recurring behaviors from episodes
- **Proactive Preloader** — anticipatory background memory loading
- **Memory Audit API** — Boss can query/correct/forget specific memories
- **Supabase Archive** — cloud backup for cross-device sync

---

## Testing

```bash
# Quick smoke test — all imports + WorkingMemory
python -c "from friday.memory import MemoryBus; print(MemoryBus().get_stats())"

# EpisodeStore integration (saves + retrieves from SQLite)
python -c "
from friday.memory.episodic import EpisodeStore
from friday.memory.types import Memory, MemoryType
import uuid
store = EpisodeStore()
m = Memory(id=str(uuid.uuid4()), type=MemoryType.FACT, content='Test', importance=0.9)
store.save_memory(m)
print('OK:', store.get_memory(m.id).content)
"

# Full MemoryBus context retrieval
python -c "
from friday.memory import MemoryBus
bus = MemoryBus()
ctx = bus.get_context_for('what tasks do I have?')
print(ctx.to_prompt_string() or 'No memories yet (expected on fresh DB)')
"
```

---

*Part of the FRIDAY Agent project — [github.com/chaitanya-369/FRIDAY-AGENT](https://github.com/chaitanya-369/FRIDAY-AGENT)*
