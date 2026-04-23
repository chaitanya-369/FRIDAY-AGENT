# 🛠️ FRIDAY Development Guide

This document outlines the patterns and practices for extending FRIDAY's capabilities.

## 🧱 Codebase Structure

- `friday/core/`: The "Brain" and primary orchestrator.
- `friday/llm/`: Adapters, Key Pool, and Model Catalog.
- `friday/tools/`: Tool definitions and the Tool Router.
- `friday/api/`: FastAPI routes and server lifecycle.
- `friday/interfaces/`: Entry points for Slack, CLI, or HUD.

## 🔌 Adding a New LLM Provider

1.  **Define the Adapter:** Create a new class in `friday/llm/adapters/` inheriting from `BaseAdapter`.
2.  **Register in Catalog:** Add the provider and its models to `ModelCatalog` (or seed them via `seeder.py`).
3.  **Update DB:** Run the seeder to populate the `LLMProvider` and `LLMModel` tables.

## 🧰 Creating a New Tool

1.  **Inherit BaseTool:** Create a new file in `friday/tools/`.
    ```python
    class MyNewTool(BaseTool):
        name = "my_tool"
        description = "Does something cool"
        parameters = { ... } # JSON Schema
        
        def execute(self, **kwargs):
            # Implementation
            return "Success"
    ```
2.  **Register:** Add an instance of your tool to `ToolRouter.register_default_tools()`.

## 🧪 Testing

We use `pytest` for logic testing and scratch scripts for integration testing.

- **Unit Tests:** `pytest tests/`
- **Integration Test:** `python scratch/test_brain.py`

## 🚀 Deployment

The project uses a `Taskfile.yml` for common operations:
- `task backend`: Start the API and Slack bot.
- `task migrations`: Generate and run Alembic migrations.
- `task seed`: Reset/Populate the database with default models and keys.
