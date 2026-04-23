from typing import Dict, Any, List
import json

from friday.tools.base import BaseTool
from friday.tools.system_stats import SystemStatsTool
from friday.tools.web_search import WebSearchTool


class ToolRouter:
    """
    Manages the registration and execution of tools.
    Also handles converting tool definitions to provider-specific schemas.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register_default_tools()

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def register_default_tools(self):
        """Registers the built-in FRIDAY tools."""
        self.register_tool(SystemStatsTool())
        self.register_tool(WebSearchTool())

    def get_anthropic_schemas(self) -> List[Dict[str, Any]]:
        """Returns tool schemas in Anthropic's format."""
        schemas = []
        for tool in self._tools.values():
            schemas.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters,
                }
            )
        return schemas

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        """Returns tool schemas in OpenAI/Groq's format."""
        schemas = []
        for tool in self._tools.values():
            schemas.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )
        return schemas

    def get_gemini_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns tool schemas in Gemini's format.
        For now we use generic python dicts, but Google genai usually wraps functions directly.
        """
        schemas = []
        for tool in self._tools.values():
            schemas.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            )
        return schemas

    def get_unified_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns provider-agnostic tool schemas for LLMRouter.

        Each entry is {"name": str, "description": str, "parameters": dict}.
        LLMRouter passes these to the active adapter's format_tools() for
        provider-specific conversion (Anthropic input_schema vs OpenAI function).
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]

    def execute(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        """Executes a tool by name and returns the result as a string."""
        if tool_name not in self._tools:
            return f"Error: Tool '{tool_name}' not found."

        try:
            tool = self._tools[tool_name]
            result = tool.execute(**kwargs)

            if isinstance(result, str):
                return result
            return json.dumps(result, indent=2)

        except Exception as e:
            return f"Error executing '{tool_name}': {str(e)}"
