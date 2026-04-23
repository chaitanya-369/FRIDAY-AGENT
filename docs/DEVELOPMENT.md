# 🛠️ FRIDAY Development Guide

> Reference for extending FRIDAY's capabilities — adding providers, tools, memory extractors, retrieval paths, and Knowledge Graph integrations.

---

## Table of Contents

1. [Codebase Structure](#codebase-structure)
2. [Adding a New LLM Provider](#adding-a-new-llm-provider)
3. [Creating a New Tool](#creating-a-new-tool)
4. [Extending the Memory System](#extending-the-memory-system)
   - [New Memory Extractor](#new-memory-extractor)
   - [New Retrieval Path](#new-retrieval-path)
   - [Knowledge Graph Extensions](#knowledge-graph-extensions)
   - [Conflict Detection Tuning](#conflict-detection-tuning)
   - [Decay Rate Tuning](#decay-rate-tuning)
5. [Memory Introspection from Tools](#memory-introspection-from-tools)
6. [Database Tables Reference](#database-tables-reference)
7. [Testing](#testing)
8. [Deployment](#deployment)

---

## Codebase Structure

```
friday/
├── core/
│   ├── brain.py            ← Central orchestrator — LLM + Memory + Tools
│   ├── database.py         ← SQLite engine init + table registration
│   └── persona.py          ← System prompt with memory injection slot
│
├── llm/
│   ├── router.py           ← Multi-provider routing + failover
│   ├── adapters/           ← One adapter class per provider
│   │   ├── base.py         ← BaseAdapter interface
│   │   ├── anthropic_adapter.py
│   │   ├── groq_adapter.py
│   │   └── gemini_adapter.py
│   ├── key_pool.py         ← Health-tracked API key rotation
│   ├── model_catalog.py    ← Available models per provider
│   └── session.py          ← Active (provider, model) selection
│
├── memory/                 ← Memory Mesh (Phase A + B complete)
│   ├── __init__.py         ← MemoryBus — single public facade
│   ├── types.py            ← Typed primitives (Memory, Task, Entity…)
│   ├── schema.py           ← SQLModel table definitions (10 tables)
│   ├── working.py          ← Tier 0: RAM sliding window
│   ├── episodic.py         ← Tier 1: SQLite CRUD + spaced repetition
│   ├── vector_store.py     ← Tier 2a: ChromaDB semantic search
│   ├── graph.py            ← Tier 2b: KnowledgeGraph (NetworkX + SQLite)
│   ├── conflict.py         ← ConflictDetector (LLM-judged)
│   ├── decay.py            ← DecayEngine (Ebbinghaus + APScheduler)
│   ├── extraction/
│   │   ├── pipeline.py     ← Claude Haiku → typed Memory objects
│   │   └── entity_linker.py← EntityLinker → KG node + edge creation
│   └── retrieval/
│       ├── engine.py       ← Multi-modal: vector + SQL + KG
│       └── intent.py       ← LLMIntentClassifier (LRU-cached Haiku)
│
├── tools/
│   ├── base.py             ← BaseTool interface
│   ├── router.py           ← Tool registration + execution
│   ├── system_stats.py     ← System monitoring
│   └── web_search.py       ← DuckDuckGo search
│
└── api/
    ├── routes/             ← FastAPI route handlers
    └── server.py           ← Uvicorn app + lifecycle
```

---

## Adding a New LLM Provider

1. **Create the adapter** in `friday/llm/adapters/`:

```python
# friday/llm/adapters/my_provider_adapter.py
from friday.llm.adapters.base import BaseAdapter

class MyProviderAdapter(BaseAdapter):
    def stream(self, model, messages, system, max_tokens, tools=None):
        # Yield string chunks
        client = MyProviderClient(api_key=self._get_api_key())
        for chunk in client.stream(...):
            yield chunk.text
```

2. **Register in `ModelCatalog`** — add the provider name and model list to `model_catalog.py` or seed via `seeder.py`.

3. **Add to `LLMRouter`** — map the provider string to your adapter class in `router.py`.

4. **Seed the DB** — run `task seed` to populate `LLMProvider` and `ModelEntry` tables.

---

## Creating a New Tool

1. **Inherit `BaseTool`** in `friday/tools/`:

```python
# friday/tools/my_tool.py
from friday.tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful for Boss"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Input query"}
        },
        "required": ["query"]
    }

    def execute(self, query: str) -> str:
        return f"Result for: {query}"
```

2. **Register** — add an instance to `ToolRouter.register_default_tools()` in `router.py`:

```python
self.register(MyTool())
```

That's it. The tool is now available to all LLM providers that support tool-use streaming.

---

## Extending the Memory System

### New Memory Extractor

The extraction pipeline calls Claude Haiku once per consolidation and parses a JSON schema. To add a new extraction dimension:

1. **Add a new `MemoryType`** in `friday/memory/types.py` if needed:
```python
class MemoryType(str, Enum):
    FACT = "fact"
    GOAL = "goal"   # ← new type
    ...
```

2. **Extend the JSON schema** in `extraction/pipeline.py → _EXTRACTION_PROMPT_TEMPLATE`:
```json
{
  "goals": [
    {"content": "...", "importance": 0.0-1.0, "entities": ["..."]}
  ]
}
```

3. **Parse the new field** in `ExtractionPipeline._parse_result()`:
```python
for g in raw.get("goals", []):
    memories.append(Memory(type=MemoryType.GOAL, content=g["content"], ...))
```

4. **Add a decay rate** in `friday/memory/decay.py → DECAY_RATES`:
```python
DECAY_RATES[MemoryType.GOAL] = 0.8  # decays fairly fast — goals change
```

### New Retrieval Path

`RetrievalEngine.retrieve()` merges multiple paths. To add a fourth (e.g., a remote knowledge base):

```python
# In retrieval/engine.py → retrieve()

# Path 4: Remote KB
if intent == QueryIntent.SEMANTIC:
    remote_results = self._remote_kb_search(query)
    for memory in remote_results:
        if memory.id not in merged:
            merged[memory.id] = RetrievalResult(memory=memory, score=0.6, source="remote_kb")
```

Register the new path source in `RetrievalResult.source` so it's visible in debug logs.

### Knowledge Graph Extensions

#### Adding a New Relationship Type

Extend the vocabulary in `graph.py`:
```python
class KnowledgeGraph:
    REL_MENTORS = "MENTORS"   # ← new type
```

Add a pattern in `entity_linker.py → _REL_PATTERNS`:
```python
(re.compile(r"\b(mentors?|coaches?|teaches?)\b", re.IGNORECASE), "MENTORS", False),
```

#### Querying the Graph from a Tool

```python
# From any tool or autopilot component:
from friday.core.brain import get_brain  # or inject via FridayBrain

brain = get_brain()
entity_card = brain.memory.get_entity_context("Priya")
# → formatted string ready for prompt injection

# Direct KG access:
kg = brain.memory.graph
paths = kg.multi_hop_paths("Boss", "Stark Industries", max_hops=3)
neighbors = kg.get_neighbors("Priya", depth=2)
central = kg.get_central_entities(top_n=5)
```

#### Adding New Graph Analytics

Add methods directly to `KnowledgeGraph` in `graph.py`:
```python
def get_clustering_coefficient(self, entity_name: str) -> float:
    """Measure how interconnected an entity's neighbors are."""
    import networkx as nx
    return nx.clustering(self._get_graph().to_undirected(), entity_name)
```

### Conflict Detection Tuning

**Change the similarity threshold** (lower → more conflicts detected, higher → fewer false positives):
```env
MEMORY_CONFLICT_SIMILARITY_THRESHOLD=0.85  # default: 0.82
```

**Change the LLM judge prompt** in `conflict.py → _llm_judge()` to fine-tune classification accuracy for your domain.

**Change the max LLM calls per batch**:
```env
MEMORY_CONFLICT_MAX_CHECKS=4  # default: 8 (lower to reduce cost)
```

### Decay Rate Tuning

Edit `DECAY_RATES` and `DEFAULT_STABILITY` in `friday/memory/decay.py`:

```python
DECAY_RATES[MemoryType.FACT] = 0.5   # slower decay — facts persist longer
DEFAULT_STABILITY[MemoryType.FACT] = 5.0  # 5-day natural stability
```

Change the archive threshold:
```python
ARCHIVE_THRESHOLD = 0.10  # archive at 10% confidence instead of 15%
```

Manually trigger a decay pass:
```python
bus = MemoryBus()
report = bus.run_decay_now()
print(report)  # {"total_checked": 131, "total_decayed": 48, ...}
```

Preview decay for a single memory without writing:
```python
preview = bus.decay_engine.get_decay_preview(memory)
print(preview)
# {
#   "content_preview": "Boss works at...",
#   "current_confidence": 0.72,
#   "projected_confidence": 0.61,
#   "would_archive": False,
#   "next_review": "2026-04-24T09:00:00"
# }
```

---

## Memory Introspection from Tools

Access all memory capabilities from any tool, route handler, or autopilot component via `FridayBrain.memory`:

```python
# All active tasks
tasks = brain.memory.get_active_tasks()

# Direct memory search
memories = brain.memory.search("Priya manager", limit=5)

# System health
stats = brain.memory.get_stats()

# KG entity card (prompt-ready)
entity_card = brain.memory.get_entity_context("Priya")

# Pending contradiction report
conflicts = brain.memory.get_conflict_report()

# Manual decay pass
decay_report = brain.memory.run_decay_now()

# Forget a specific memory
success = brain.memory.forget(memory_id)

# Full context for a query (what gets injected into the LLM prompt)
ctx = brain.memory.get_context_for("what should I focus on?")
print(ctx.to_prompt_string())
```

---

## Database Tables Reference

| Table | Module | Purpose |
|---|---|---|
| `memories` | `memory/schema.py` | Typed, scored memory units with decay metadata |
| `tasks` | `memory/schema.py` | Actionable items — priority, status, due date |
| `episodes` | `memory/schema.py` | Conversation sessions + LLM-generated summaries |
| `entities` | `memory/schema.py` | KG nodes — people, projects, tools, concepts |
| `relationships` | `memory/schema.py` | KG edges — typed, weighted, confidence-scored |
| `memory_conflicts` | `memory/schema.py` | Detected contradictions pending resolution |
| `llm_providers` | `llm/models/db_models.py` | Registered providers |
| `api_keys` | `llm/models/db_models.py` | Health-tracked key pool per provider |
| `model_entries` | `llm/models/db_models.py` | Model catalog per provider |
| `active_session` | `llm/models/db_models.py` | Currently active (provider, model) |

**Adding a new table:**
1. Define a `SQLModel` class in `friday/memory/schema.py`
2. Register it in `friday/core/database.py → create_db_and_tables()`
3. Auto-created on next startup — no migration needed during development
4. Add CRUD methods to `EpisodeStore` in `episodic.py`

---

## Testing

```bash
# Full import + init smoke test
python -c "from friday.memory import MemoryBus; print(MemoryBus().get_stats())"

# Phase B component smoke tests
python -c "
from friday.memory.graph import KnowledgeGraph
kg = KnowledgeGraph()
kg.load_from_db()
print('KG:', kg.stats())
e = kg.upsert_entity('TestEntity', entity_type='concept')
print('Entity:', e)
"

# Intent classifier (no API key needed)
python -c "
from friday.memory.retrieval.intent import LLMIntentClassifier
clf = LLMIntentClassifier()
clf.disable_llm()
for q in ['tasks pending?', 'who is Priya?', 'what do I prefer?']:
    print(clf.classify(q), '->', q)
"

# Unit tests
pytest tests/

# Full integration test (requires .env with valid API keys)
python scratch/test_brain.py
```

---

## Deployment

```bash
task backend      # Start FastAPI + Slack Socket Mode (uvicorn + slack-bolt)
task migrations   # Generate and run Alembic migrations
task seed         # Reset/populate DB with default providers and keys
```

**Data directory** (`data/`) is in `.gitignore` — SQLite and ChromaDB files are never committed.

**Environment**: copy `.env.example` to `.env` and fill in API keys. The memory system degrades gracefully — if ChromaDB or NetworkX are unavailable, FRIDAY falls back to SQL-only retrieval.
