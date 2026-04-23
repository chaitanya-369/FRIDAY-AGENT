import abc
from typing import Any, Dict


class BaseTool(abc.ABC):
    """
    Abstract base class for all FRIDAY tools.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ for Anthropic."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does and when to use it."""
        pass

    @property
    @abc.abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        The JSON schema for the tool's parameters.
        Example:
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
        """
        pass

    @abc.abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Executes the tool with the given arguments.
        Returns a string or JSON-serializable object representing the result.
        """
        pass
