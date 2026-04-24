from typing import Dict, Any
from duckduckgo_search import DDGS

from friday.tools.base import BaseTool


class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Searches the web for information using DuckDuckGo. Use this to find real-time info, news, or factual answers."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 3, max 10).",
                },
            },
            "required": ["query"],
        }

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        if not query:
            return "Error: 'query' parameter is required."

        max_results = min(kwargs.get("max_results", 3), 10)

        try:
            results = DDGS().text(query, max_results=max_results)
            formatted_results = []
            for r in results:
                formatted_results.append(
                    f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}"
                )
            if not formatted_results:
                return "No results found."
            return "\n\n".join(formatted_results)
        except Exception as e:
            return f"Search failed: {str(e)}"
