"""
friday/llm/adapters/base.py

Core abstractions for the Omni-LLM adapter layer.

Every provider adapter inherits BaseAdapter and implements:
  - stream()       : yields StreamChunk objects for one LLM turn
  - format_tool()  : converts a unified tool dict → provider-native schema
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generator, Optional


@dataclass
class ToolCall:
    """
    A tool invocation parsed from an LLM response.

    Attributes:
        id   : Provider-assigned call ID (used to correlate results).
               Gemini does not issue IDs — the tool name is used instead.
        name : Name of the tool to execute (must match a registered BaseTool).
        arguments : Parsed keyword arguments to pass to the tool.
    """

    id: str
    name: str
    arguments: dict


@dataclass
class StreamChunk:
    """
    A single unit yielded by BaseAdapter.stream().

    Text chunks arrive incrementally (text != None).
    The final chunk has is_final=True. If the model requested tool use,
    stop_reason == "tool_use" and tool_calls is populated.

    Attributes:
        text                  : Incremental text token(s), or None.
        tool_calls            : List of ToolCall when stop_reason == "tool_use".
        is_final              : True on the last chunk of a turn.
        stop_reason           : "end_turn" | "tool_use" | "max_tokens" | None.
        raw_assistant_content : Provider-native content to persist in history.
                                For Anthropic: list of content blocks.
                                For Groq/OpenAI: {"content": str, "tool_calls": [...]}
                                For Gemini: str
    """

    text: Optional[str] = None
    tool_calls: list = field(default_factory=list)  # list[ToolCall]
    is_final: bool = False
    stop_reason: Optional[str] = None
    raw_assistant_content: Any = None


class BaseAdapter(ABC):
    """
    Abstract base class for all LLM provider adapters.

    Each concrete adapter handles:
      1. Client instantiation with the given api_key.
      2. Message format conversion (unified dicts → provider format).
      3. Tool schema conversion.
      4. Streaming and parsing tool calls from the response.
      5. Yielding StreamChunk objects back to LLMRouter.
    """

    #: Provider identifier string. Must match LLMProvider.name in DB.
    provider_name: str = ""

    @abstractmethod
    def stream(
        self,
        messages: list,
        system_prompt: str,
        model: str,
        api_key: str,
        tools: list,
        max_tokens: int = 1024,
        base_url: Optional[str] = None,
    ) -> Generator[StreamChunk, None, None]:
        """
        Stream one LLM turn.

        Args:
            messages      : Conversation history in this provider's native format.
            system_prompt : Formatted FRIDAY persona prompt.
            model         : Model ID string (e.g. "claude-sonnet-4-5-20250514").
            api_key       : Raw API key string from the KeyPool.
            tools         : Pre-formatted tool schemas (output of format_tools()).
            max_tokens    : Maximum tokens to generate.
            base_url      : Optional override for OpenAI-compatible providers.

        Yields:
            StreamChunk — text chunks first, then a final chunk with
            is_final=True and optional tool_calls.
        """
        ...

    @abstractmethod
    def format_tool(self, name: str, description: str, parameters: dict) -> dict:
        """
        Convert a unified tool definition to this provider's native schema.

        Args:
            name        : Tool name (e.g. "system_stats").
            description : Tool description string.
            parameters  : JSON Schema dict (from BaseTool.parameters).

        Returns:
            Provider-specific tool schema dict.
        """
        ...

    def format_tools(self, tool_schemas: list) -> list:
        """
        Convert a list of unified tool schemas to provider-native format.

        Args:
            tool_schemas : List of {"name": str, "description": str, "parameters": dict}

        Returns:
            List of provider-native tool schema objects.
        """
        if not tool_schemas:
            return []
        return [
            self.format_tool(t["name"], t["description"], t["parameters"])
            for t in tool_schemas
        ]
