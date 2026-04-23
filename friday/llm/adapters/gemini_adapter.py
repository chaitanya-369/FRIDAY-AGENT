"""
friday/llm/adapters/gemini_adapter.py

Adapter for Google Gemini models using the new google-genai SDK.
Supports full tool calling via FunctionDeclaration.
"""

from typing import Generator, Optional

from google import genai
from google.genai import types

from friday.llm.adapters.base import BaseAdapter, StreamChunk, ToolCall


def _to_gemini_type(json_type: str) -> str:
    return {
        "string": "STRING",
        "number": "NUMBER",
        "integer": "INTEGER",
        "boolean": "BOOLEAN",
        "array": "ARRAY",
        "object": "OBJECT",
    }.get(json_type, "STRING")


def _build_declaration(
    name: str, description: str, parameters: dict
) -> types.FunctionDeclaration:
    """Convert a JSON Schema dict to a Gemini FunctionDeclaration."""
    props = {}
    for prop_name, prop_schema in parameters.get("properties", {}).items():
        props[prop_name] = types.Schema(
            type=_to_gemini_type(prop_schema.get("type", "string")),
            description=prop_schema.get("description", ""),
        )

    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters=types.Schema(
            type="OBJECT",
            properties=props,
            required=parameters.get("required", []),
        ),
    )


class GeminiAdapter(BaseAdapter):
    """
    Streams responses from Google Gemini models using the google-genai SDK.
    Supports native tool calling via FunctionDeclaration.
    """

    provider_name = "gemini"

    def format_tool(self, name: str, description: str, parameters: dict) -> dict:
        return {"name": name, "description": description, "parameters": parameters}

    def format_tools(self, tool_schemas: list) -> list:
        """Return a single Gemini Tool wrapping all FunctionDeclarations."""
        if not tool_schemas:
            return []
        declarations = [
            _build_declaration(t["name"], t["description"], t["parameters"])
            for t in tool_schemas
        ]
        return [types.Tool(function_declarations=declarations)]

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
        client = genai.Client(api_key=api_key)

        # Build Gemini Contents from history
        contents = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            content = msg.get("content", "")
            if not isinstance(content, str):
                content = str(content)
            contents.append(types.Content(role=role, parts=[types.Part(text=content)]))

        config_kwargs: dict = {
            "system_instruction": system_prompt,
            "max_output_tokens": max_tokens,
        }
        if tools:
            config_kwargs["tools"] = tools

        config = types.GenerateContentConfig(**config_kwargs)

        response = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )

        full_text = ""
        function_calls: list[ToolCall] = []

        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                yield StreamChunk(text=chunk.text)

            if chunk.function_calls:
                for fc in chunk.function_calls:
                    function_calls.append(
                        ToolCall(
                            id=fc.id or fc.name,
                            name=fc.name,
                            arguments=dict(fc.args) if fc.args else {},
                        )
                    )

        if function_calls:
            yield StreamChunk(
                is_final=True,
                stop_reason="tool_use",
                tool_calls=function_calls,
                raw_assistant_content=full_text,
            )
        else:
            yield StreamChunk(
                is_final=True, stop_reason="end_turn", raw_assistant_content=full_text
            )
