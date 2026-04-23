"""
friday/llm/history_bridge.py

SmartHistoryBridge — converts conversation history between provider formats
so that FRIDAY can switch providers mid-conversation without losing context.

Provider message formats:
  Anthropic:
    user    → {"role": "user",      "content": "..."}               (simple)
    user    → {"role": "user",      "content": [...blocks...]}       (tool result)
    asst    → {"role": "assistant", "content": [...blocks...]}       (content blocks)

  OpenAI / Groq / DeepSeek (OpenAI-compat):
    user    → {"role": "user",      "content": "..."}
    asst    → {"role": "assistant", "content": "...", "tool_calls": [...]}
    tool    → {"role": "tool",      "content": "...", "tool_call_id": "...", "name": "..."}

  Gemini (also OpenAI-compat via the Gemini adapter — same format as above)

Bridge rules:
  - Text-only messages: trivially portable (same structure).
  - Tool-use turns:     converted to the target provider's native format.
  - Tool results:       converted between Anthropic's user-role blocks and
                        OpenAI's "tool" role messages.
  - Unknown blocks:     dropped with a warning rather than crashing.

Usage:
    bridge = SmartHistoryBridge()
    new_history = bridge.convert(
        history=old_history,
        from_provider="anthropic",
        to_provider="openai",
    )
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Providers that use the OpenAI message format
_OPENAI_COMPAT = {"openai", "groq", "deepseek", "gemini"}


class SmartHistoryBridge:
    """
    Converts conversation history between Anthropic and OpenAI-compatible formats.

    This is intentionally lossless for text content and best-effort for tool
    calls (tool call IDs are preserved; unknown block types are skipped).
    """

    # ── Public entry point ────────────────────────────────────────────────────

    def convert(
        self,
        history: list[dict[str, Any]],
        from_provider: str,
        to_provider: str,
    ) -> list[dict[str, Any]]:
        """
        Convert a conversation history list from one provider's format to another.

        Args:
            history       : The current conversation history list.
            from_provider : The provider that generated this history.
            to_provider   : The provider we're switching to.

        Returns:
            A new history list in the target provider's format.
            If from_provider == to_provider, returns history unchanged.
        """
        if from_provider == to_provider:
            return history

        from_family = self._family(from_provider)
        to_family = self._family(to_provider)

        if from_family == to_family:
            # Same wire format (e.g., groq → openai or openai → deepseek)
            return history

        if from_family == "anthropic" and to_family == "openai":
            return self._anthropic_to_openai(history)

        if from_family == "openai" and to_family == "anthropic":
            return self._openai_to_anthropic(history)

        # Unknown provider combination — return as-is with warning
        logger.warning(
            "SmartHistoryBridge: unknown conversion %s → %s, returning history unchanged",
            from_provider,
            to_provider,
        )
        return history

    # ── Family classification ─────────────────────────────────────────────────

    @staticmethod
    def _family(provider: str) -> str:
        """Return 'anthropic' or 'openai' based on provider name."""
        if provider == "anthropic":
            return "anthropic"
        if provider in _OPENAI_COMPAT:
            return "openai"
        return "unknown"

    # ── Anthropic → OpenAI ────────────────────────────────────────────────────

    def _anthropic_to_openai(
        self, history: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Convert Anthropic-format history to OpenAI-compat format.

        Anthropic history can contain:
          - user messages with string content
          - user messages with list content (tool_result blocks)
          - assistant messages with list content (TextBlock + ToolUseBlock)
        """
        result: list[dict[str, Any]] = []

        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")

            # ── User message ─────────────────────────────────────────────────
            if role == "user":
                if isinstance(content, str):
                    result.append({"role": "user", "content": content})
                elif isinstance(content, list):
                    # Could be tool_result blocks or mixed
                    converted = self._anthropic_user_blocks_to_openai(content)
                    result.extend(converted)
                else:
                    logger.warning(
                        "Skipping unknown user content type: %s", type(content)
                    )

            # ── Assistant message ─────────────────────────────────────────────
            elif role == "assistant":
                if isinstance(content, str):
                    result.append({"role": "assistant", "content": content})
                elif isinstance(content, list):
                    # Anthropic content block list
                    converted = self._anthropic_assistant_blocks_to_openai(content)
                    result.extend(converted)
                else:
                    # Raw object (e.g., Anthropic SDK content block objects)
                    converted = self._anthropic_assistant_blocks_to_openai(
                        self._normalise_blocks(content)
                    )
                    result.extend(converted)

            else:
                # Unknown role — pass through
                result.append(msg)

        return result

    def _anthropic_user_blocks_to_openai(
        self, blocks: list[Any]
    ) -> list[dict[str, Any]]:
        """
        Convert Anthropic user-role content blocks to OpenAI messages.
        Tool results become role="tool" messages.
        Text becomes role="user".
        """
        messages: list[dict[str, Any]] = []
        text_parts: list[str] = []

        for block in blocks:
            btype = self._block_type(block)

            if btype == "text":
                text_parts.append(self._block_text(block))

            elif btype == "tool_result":
                # Flush accumulated text first
                if text_parts:
                    messages.append({"role": "user", "content": " ".join(text_parts)})
                    text_parts = []

                tool_use_id = self._block_attr(block, "tool_use_id") or ""
                result_content = self._block_attr(block, "content") or ""
                if isinstance(result_content, list):
                    result_content = " ".join(
                        self._block_text(b)
                        for b in result_content
                        if self._block_type(b) == "text"
                    )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_use_id,
                        "name": "",  # Anthropic tool_result doesn't carry name; best-effort
                        "content": str(result_content),
                    }
                )

            else:
                logger.warning("Skipping unknown user block type '%s'", btype)

        if text_parts:
            messages.append({"role": "user", "content": " ".join(text_parts)})

        return messages

    def _anthropic_assistant_blocks_to_openai(
        self, blocks: list[Any]
    ) -> list[dict[str, Any]]:
        """
        Convert Anthropic assistant content blocks to a single OpenAI assistant message.
        TextBlocks → content string.
        ToolUseBlocks → tool_calls list.
        """
        text_parts: list[str] = []
        tool_calls: list[dict] = []

        for block in blocks:
            btype = self._block_type(block)

            if btype == "text":
                text_parts.append(self._block_text(block))

            elif btype == "tool_use":
                tool_calls.append(
                    {
                        "id": self._block_attr(block, "id") or "",
                        "type": "function",
                        "function": {
                            "name": self._block_attr(block, "name") or "",
                            "arguments": json.dumps(
                                self._block_attr(block, "input") or {}
                            ),
                        },
                    }
                )

            else:
                logger.warning("Skipping unknown assistant block type '%s'", btype)

        msg: dict[str, Any] = {
            "role": "assistant",
            "content": " ".join(text_parts) if text_parts else None,
        }
        if tool_calls:
            msg["tool_calls"] = tool_calls

        return [msg]

    # ── OpenAI → Anthropic ────────────────────────────────────────────────────

    def _openai_to_anthropic(
        self, history: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Convert OpenAI-compat format history to Anthropic format.

        OpenAI history can contain:
          - user    {"role": "user",      "content": str}
          - asst    {"role": "assistant", "content": str|None, "tool_calls": [...]}
          - tool    {"role": "tool",      "content": str, "tool_call_id": str, "name": str}
        """
        result: list[dict[str, Any]] = []
        i = 0

        while i < len(history):
            msg = history[i]
            role = msg.get("role", "")

            if role == "user":
                result.append({"role": "user", "content": msg.get("content", "")})
                i += 1

            elif role == "assistant":
                content_str = msg.get("content") or ""
                tool_calls = msg.get("tool_calls") or []

                blocks: list[dict] = []
                if content_str:
                    blocks.append({"type": "text", "text": content_str})

                for tc in tool_calls:
                    fn = tc.get("function", {})
                    try:
                        args = json.loads(fn.get("arguments", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.get("id", ""),
                            "name": fn.get("name", ""),
                            "input": args,
                        }
                    )

                result.append({"role": "assistant", "content": blocks})
                i += 1

            elif role == "tool":
                # Collect consecutive tool messages into a single user turn
                tool_results: list[dict] = []
                while i < len(history) and history[i].get("role") == "tool":
                    tm = history[i]
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tm.get("tool_call_id", ""),
                            "content": str(tm.get("content", "")),
                        }
                    )
                    i += 1
                result.append({"role": "user", "content": tool_results})

            else:
                # Unknown role — pass through
                result.append(msg)
                i += 1

        return result

    # ── Block introspection helpers ───────────────────────────────────────────
    # These handle both dict-style blocks and SDK object-style blocks
    # (e.g., anthropic.types.TextBlock, ToolUseBlock).

    @staticmethod
    def _block_type(block: Any) -> str:
        """Extract the 'type' from a block (dict or object)."""
        if isinstance(block, dict):
            return block.get("type", "unknown")
        return getattr(block, "type", "unknown")

    @staticmethod
    def _block_text(block: Any) -> str:
        """Extract text content from a text block."""
        if isinstance(block, dict):
            return block.get("text", "")
        return getattr(block, "text", "")

    @staticmethod
    def _block_attr(block: Any, attr: str) -> Any:
        """Extract an arbitrary attribute from a block (dict or object)."""
        if isinstance(block, dict):
            return block.get(attr)
        return getattr(block, attr, None)

    @staticmethod
    def _normalise_blocks(content: Any) -> list[Any]:
        """Ensure content is a list (wraps single blocks)."""
        if isinstance(content, list):
            return content
        return [content]


# ── Module-level singleton ─────────────────────────────────────────────────────

history_bridge = SmartHistoryBridge()
