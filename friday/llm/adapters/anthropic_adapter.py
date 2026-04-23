"""
friday/llm/adapters/anthropic_adapter.py

Adapter for Anthropic's Claude models.
Supports native tool use via Anthropic's content blocks.
"""

from typing import Generator, Optional

import anthropic

from friday.llm.adapters.base import BaseAdapter, StreamChunk, ToolCall


class AnthropicAdapter(BaseAdapter):
    """
    Streams responses from Anthropic Claude models.

    Tool calling uses Anthropic's native content-block format.
    raw_assistant_content in the final chunk is the list of Anthropic
    content blocks (TextBlock + ToolUseBlock) needed to reconstruct history.
    """

    provider_name = "anthropic"

    def format_tool(self, name: str, description: str, parameters: dict) -> dict:
        return {
            "name": name,
            "description": description,
            "input_schema": parameters,
        }

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
        client = anthropic.Anthropic(api_key=api_key)

        kwargs: dict = dict(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        if tools:
            kwargs["tools"] = tools

        with client.messages.stream(**kwargs) as stream:
            full_text = ""
            for text in stream.text_stream:
                full_text += text
                yield StreamChunk(text=text)

            message = stream.get_final_message()

            if message.stop_reason == "tool_use":
                tool_calls = [
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=dict(block.input),
                    )
                    for block in message.content
                    if block.type == "tool_use"
                ]
                yield StreamChunk(
                    is_final=True,
                    stop_reason="tool_use",
                    tool_calls=tool_calls,
                    raw_assistant_content=message.content,  # list of blocks for history
                )
            else:
                yield StreamChunk(
                    is_final=True,
                    stop_reason="end_turn",
                    raw_assistant_content=full_text,
                )
