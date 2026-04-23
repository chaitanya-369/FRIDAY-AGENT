"""
friday/llm/adapters/openai_adapter.py

Adapter for OpenAI's API (GPT-4o, o1, o3, etc.).
Also serves as the base for OpenAI-compatible providers (DeepSeek, Azure, etc.)
via the optional base_url parameter.
"""

import json
from typing import Generator, Optional

from openai import OpenAI

from friday.llm.adapters.base import BaseAdapter, StreamChunk, ToolCall


class OpenAIAdapter(BaseAdapter):
    """
    Streams responses from OpenAI models.

    Accepts an optional base_url to support OpenAI-compatible providers.
    Tool calling uses OpenAI's function-call format (identical to Groq).
    """

    provider_name = "openai"

    def format_tool(self, name: str, description: str, parameters: dict) -> dict:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
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
        client_kwargs: dict = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        kwargs: dict = dict(
            model=model,
            messages=all_messages,
            max_tokens=max_tokens,
            stream=True,
        )
        if tools:
            kwargs["tools"] = tools

        stream = client.chat.completions.create(**kwargs)

        full_text = ""
        tc_acc: dict = {}  # index → {"id", "name", "arguments"}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                full_text += delta.content
                yield StreamChunk(text=delta.content)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tc_acc:
                        tc_acc[idx] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tc_acc[idx]["id"] = tc_acc[idx]["id"] or tc.id
                    if tc.function:
                        if tc.function.name:
                            tc_acc[idx]["name"] = (
                                tc_acc[idx]["name"] or tc.function.name
                            )
                        if tc.function.arguments:
                            tc_acc[idx]["arguments"] += tc.function.arguments

        if tc_acc:
            tool_calls = []
            history_tcs = []
            for tc in tc_acc.values():
                try:
                    args = json.loads(tc["arguments"])
                except Exception:
                    args = {}
                tool_calls.append(
                    ToolCall(id=tc["id"], name=tc["name"], arguments=args)
                )
                history_tcs.append(
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    }
                )

            yield StreamChunk(
                is_final=True,
                stop_reason="tool_use",
                tool_calls=tool_calls,
                raw_assistant_content={
                    "content": full_text or None,
                    "tool_calls": history_tcs,
                },
            )
        else:
            yield StreamChunk(
                is_final=True, stop_reason="end_turn", raw_assistant_content=full_text
            )
