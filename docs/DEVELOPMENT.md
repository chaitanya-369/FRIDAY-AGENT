# 🛠️ FRIDAY Development Guide

This document outlines the patterns and practices for extending FRIDAY's capabilities.

---

## 🧱 Codebase Structure

```
friday/
├── core/         ← Brain orchestrator, DB engine, persona prompt
├── llm/          ← Adapters, Key Pool, Model Catalog, Router
├── memory/       ← Memory Mesh (Tier 0–2, Extraction, Retrieval)
├── tools/        ← Tool definitions and Tool Router
├── api/          ← FastAPI routes and server lifecycle
└── interfaces/   ← Entry points (Slack, CLI, HUD)
```

---

## 🔌 Adding a New LLM Provider

1. **Define the Adapter** — create a new class in `friday/llm/adapters/` inheriting from `BaseAdapter`.
2. **Register in Catalog** — add the provider and its models to `ModelCatalog` or seed them via `seeder.py`.
3. **Update DB** — run the seeder to populate `LLMProvider` and `ModelEntry` tables.

---

## 🧰 Creating a New Tool

1. **Inherit `BaseTool`** — create a new file in `friday/tools/`:

```python
class MyNewTool(BaseTool):
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
        # Implementation
        return f"Result for: {query}"
```

2. **Register** — add an instance to `ToolRouter.register_default_tools()`.

---

## 🧠 Extending the Memory System

The Memory Mesh is designed for extensibility. Each tier is independently replaceable.

### Adding a New Memory Extractor

The extraction pipeline calls a single LLM and parses JSON. To add a new extraction dimension:

1. Add the new field to the JSON schema in `_EXTRACTION_PROMPT_TEMPLATE` in `extraction/pipeline.py`.
2. Add a corresponding `MemoryType` value in `types.py` if needed.
3. Parse the new field in `ExtractionPipeline._parse_result()`.

### Adding a Custom Retrieval Path

`RetrievalEngine.retrieve()` runs multiple search paths in parallel. To add a third path (e.g., Knowledge Graph):

```python
# In retrieval/engine.py → retrieve()
graph_results = self._graph_search(query, intent)  # your new path
merged = self._merge(vector_by_id, sql_results, graph_results)
```

### Memory Introspection from Tools

From any tool or autopilot component, access memory directly via `FridayBrain.memory`:

```python
# Get all active tasks
tasks = brain.memory.get_active_tasks()

# Search memories for a query
memories = brain.memory.search("Priya manager", limit=5)

# Get system health
stats = brain.memory.get_stats()
```

### Adding New SQLite Tables

1. Define a new `SQLModel` class in `friday/memory/schema.py`.
2. It will be auto-created by `create_db_and_tables()` on next startup (no migration needed during dev).
3. Add CRUD methods to `EpisodeStore` in `episodic.py`.

---

## 🗃️ Database Tables

| Table | Module | Purpose |
|---|---|---|
| `llm_providers` | `llm/models/db_models.py` | Registered providers |
| `api_keys` | `llm/models/db_models.py` | Key pool with health tracking |
| `model_entries` | `llm/models/db_models.py` | Model catalog per provider |
| `active_session` | `llm/models/db_models.py` | Current active (provider, model) |
| `memories` | `memory/schema.py` | Typed, scored memory units |
| `tasks` | `memory/schema.py` | Actionable tasks |
| `episodes` | `memory/schema.py` | Conversation sessions |
| `entities` | `memory/schema.py` | Knowledge graph nodes |
| `relationships` | `memory/schema.py` | Knowledge graph edges |
| `memory_conflicts` | `memory/schema.py` | Detected contradictions |

---

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Memory system smoke tests
python -c "from friday.memory import MemoryBus; print(MemoryBus().get_stats())"

# Full integration test (requires .env with valid API keys)
python scratch/test_brain.py
```

---

## 🚀 Deployment

The project uses `Taskfile.yml` for common operations:

```bash
task backend      # Start FastAPI + Slack bot
task migrations   # Generate and run Alembic migrations
task seed         # Reset/populate DB with default models and keys
```
