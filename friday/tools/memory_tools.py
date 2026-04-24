from typing import Any, Dict

from friday.memory import MemoryBus
from friday.tools.base import BaseTool


class MemorySearchTool(BaseTool):
    """Tool to search FRIDAY's memory mesh."""

    def __init__(self, memory_bus: MemoryBus):
        self.memory = memory_bus

    @property
    def name(self) -> str:
        return "memory_search"

    @property
    def description(self) -> str:
        return "Search FRIDAY's episodic and semantic memory for facts, preferences, or past events."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look for in memory.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        }

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        limit = kwargs.get("limit", 5)

        results = self.memory.search(query, limit=limit)
        if not results:
            return "No matching memories found."

        formatted_results = []
        for r in results:
            formatted_results.append(
                f"- [ID: {r.id[:8]}] ({r.type.value}): {r.content}"
            )
        return "\n".join(formatted_results)


class MemoryUpdateTool(BaseTool):
    """Tool to update an existing memory."""

    def __init__(self, memory_bus: MemoryBus):
        self.memory = memory_bus

    @property
    def name(self) -> str:
        return "memory_update"

    @property
    def description(self) -> str:
        return "Update the content of an existing memory using its ID. Use this when you find outdated facts or preferences."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The 8-character or full UUID of the memory to update.",
                },
                "new_content": {
                    "type": "string",
                    "description": "The complete new content that should replace the old memory.",
                },
            },
            "required": ["memory_id", "new_content"],
        }

    def execute(self, **kwargs) -> Any:
        memory_id = kwargs.get("memory_id")
        new_content = kwargs.get("new_content")

        # Simple prefix matching for short IDs
        if len(memory_id) == 8:
            all_memories = self.memory.episode_store.get_all_memories()
            matches = [m for m in all_memories if m.id.startswith(memory_id)]
            if not matches:
                return f"Error: No memory found starting with ID '{memory_id}'"
            memory_id = matches[0].id

        success = self.memory.update_memory(memory_id, new_content)
        if success:
            return f"Successfully updated memory {memory_id[:8]}."
        return f"Failed to update memory {memory_id[:8]}. Ensure ID is correct."


class MemoryDeleteTool(BaseTool):
    """Tool to forget/delete a memory."""

    def __init__(self, memory_bus: MemoryBus):
        self.memory = memory_bus

    @property
    def name(self) -> str:
        return "memory_forget"

    @property
    def description(self) -> str:
        return "Forget or delete a specific memory by its ID. Use this when a memory is no longer true or the user explicitly asks to forget it."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "memory_id": {
                    "type": "string",
                    "description": "The 8-character or full UUID of the memory to forget.",
                },
            },
            "required": ["memory_id"],
        }

    def execute(self, **kwargs) -> Any:
        memory_id = kwargs.get("memory_id")

        # Simple prefix matching for short IDs
        if len(memory_id) == 8:
            all_memories = self.memory.episode_store.get_all_memories()
            matches = [m for m in all_memories if m.id.startswith(memory_id)]
            if not matches:
                return f"Error: No memory found starting with ID '{memory_id}'"
            memory_id = matches[0].id

        success = self.memory.forget(memory_id)
        if success:
            return f"Successfully forgot memory {memory_id[:8]}."
        return f"Failed to forget memory {memory_id[:8]}. Ensure ID is correct."
