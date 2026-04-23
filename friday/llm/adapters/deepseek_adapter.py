"""
friday/llm/adapters/deepseek_adapter.py

Adapter for DeepSeek's API.
DeepSeek is fully OpenAI-compatible — this adapter simply hard-codes
the base_url so LLMRouter doesn't need to know about it.
"""

from typing import Generator, Optional

from friday.llm.adapters.openai_adapter import OpenAIAdapter
from friday.llm.adapters.base import StreamChunk

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class DeepSeekAdapter(OpenAIAdapter):
    """
    Streams responses from DeepSeek models (deepseek-chat, deepseek-reasoner).

    Inherits all logic from OpenAIAdapter, overriding provider_name and
    injecting the DeepSeek base URL automatically.
    """

    provider_name = "deepseek"

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
        # Always route through DeepSeek's endpoint
        yield from super().stream(
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            api_key=api_key,
            tools=tools,
            max_tokens=max_tokens,
            base_url=base_url or DEEPSEEK_BASE_URL,
        )
