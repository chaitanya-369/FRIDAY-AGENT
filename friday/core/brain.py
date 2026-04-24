"""
friday/core/brain.py

FRIDAY's core intelligence — now powered by the Omni-LLM layer with:
  - Dynamic model switching (reads ActiveModelSession on every turn)
  - SmartHistoryBridge (preserves conversation when provider changes)
  - SwitchCommandParser (intercepts model-switch commands before LLM call)
  - OfflineGuardian delegation (graceful rich response when all LLMs fail)

FridayBrain manages:
  - Conversation history (sliding window, provider-native format)
  - System prompt construction (includes active session context)
  - Tool execution loop (calls LLMRouter → executes tools → loops on tool_use)
  - Provider-aware history updates for all 5 adapters
"""

from datetime import datetime
from typing import Generator, List, Dict, Any

import sentry_sdk
from langfuse import Langfuse

from friday.config.settings import settings
from friday.core.database import create_db_and_tables
from friday.core.persona import FRIDAY_SYSTEM_PROMPT
from friday.llm.history_bridge import history_bridge
from friday.llm.router import LLMRouter, LLMExhaustedError
from friday.llm.session import active_session
from friday.llm.switch_parser import (
    switch_parser,
    SwitchIntent,
    StatusIntent,
    ListIntent,
    ResetIntent,
    AmbiguousIntent,
    DiagnosticsIntent,
)
from friday.llm.adapters.base import StreamChunk
from friday.memory import MemoryBus
from friday.tools.router import ToolRouter
from friday.tools.memory_tools import (
    MemorySearchTool,
    MemoryUpdateTool,
    MemoryDeleteTool,
)

# ── Observability setup ───────────────────────────────────────────────────────
if hasattr(settings, "sentry_dsn") and settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=1.0)

if hasattr(settings, "langfuse_public_key") and settings.langfuse_public_key:
    langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )


class FridayBrain:
    """
    Core intelligence component of the FRIDAY Agent.

    On every turn:
      1. SwitchCommandParser intercepts model-switch commands first.
      2. MemoryBus retrieves ranked context for system prompt injection.
      3. ActiveModelSession provides the current (provider, model).
      4. SmartHistoryBridge converts history if provider changed.
      5. LLMRouter streams the response.
      6. MemoryBus buffers the completed turn for async consolidation.
      7. OfflineGuardian handles LLMExhaustedError gracefully.
    """

    def __init__(self):
        create_db_and_tables()
        self.llm = LLMRouter()
        self.tool_router = ToolRouter()
        self.memory = MemoryBus()  # ← Memory Mesh

        # Register Memory Mesh self-surgery tools
        self.tool_router.register_tool(MemorySearchTool(self.memory))
        self.tool_router.register_tool(MemoryUpdateTool(self.memory))
        self.tool_router.register_tool(MemoryDeleteTool(self.memory))

        self.conversation_history: List[Dict[str, Any]] = []
        self._current_provider: str = settings.default_provider
        self._last_user_input: str = ""  # buffered for memory observation

    # ── System prompt ─────────────────────────────────────────────────────────

    def _get_system_prompt(self, memory_context: str = "") -> str:
        """Build the FRIDAY persona prompt with live timestamp, session, and memory context."""
        state = active_session.get_state()
        return FRIDAY_SYSTEM_PROMPT.format(
            timestamp=datetime.now().isoformat(),
            day=datetime.now().strftime("%A"),
            active_provider=state.get("provider_name", "unknown"),
            active_model=state.get("model_id", "unknown"),
            set_by=state.get("set_by", "system"),
            switched_at=state.get("switched_at", "unknown"),
            memory_context=memory_context,
        )

    # ── History management ────────────────────────────────────────────────────

    def _update_history(self, role: str, content: Any, **extra) -> None:
        """Append a message to history, keeping the sliding window at 40."""
        msg: Dict[str, Any] = {"role": role, "content": content}
        msg.update(extra)
        self.conversation_history.append(msg)
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]

    def _switch_provider_with_bridge(self, new_provider: str) -> None:
        """
        Bridge history from the current provider format to the new provider format,
        then update the tracked current provider.
        """
        if new_provider == self._current_provider:
            return

        self.conversation_history = history_bridge.convert(
            history=self.conversation_history,
            from_provider=self._current_provider,
            to_provider=new_provider,
        )
        self._current_provider = new_provider

    def _sync_provider_from_session(self) -> tuple[str, str]:
        """
        Read the active (provider, model) from the session, bridge history
        if needed, and return both for use in this turn.
        """
        provider, model = active_session.get()
        self._switch_provider_with_bridge(provider)
        return provider, model

    # ── Provider-aware history update after tool_use ──────────────────────────

    def _record_tool_use_assistant(self, chunk: StreamChunk, provider: str) -> None:
        """
        Persist the assistant's tool-use turn into history in the correct
        format for the active provider.
        """
        if provider == "anthropic":
            self._update_history("assistant", chunk.raw_assistant_content)
        else:
            raw = chunk.raw_assistant_content or {}
            self._update_history(
                "assistant",
                raw.get("content"),
                tool_calls=raw.get("tool_calls", []),
            )

    def _record_tool_result(
        self, tc_id: str, name: str, result: str, provider: str
    ) -> None:
        """
        Persist a tool result into history in the correct format for the
        active provider.
        """
        if provider == "anthropic":
            self._update_history(
                "user",
                [{"type": "tool_result", "tool_use_id": tc_id, "content": result}],
            )
        else:
            self._update_history("tool", result, tool_call_id=tc_id, name=name)

    # ── Switch command handling ───────────────────────────────────────────────

    def _handle_switch_intent(self, intent: SwitchIntent) -> Generator[str, None, None]:
        """Execute a confirmed model switch and yield a confirmation message."""
        previous = active_session.get()
        active_session.set(
            provider_name=intent.provider,
            model_id=intent.model,
            set_by="user",
            reason="user command",
        )
        confirmation = switch_parser.format_switch_confirmation(intent, previous)
        self._update_history("assistant", confirmation)
        yield confirmation

    def _handle_status_intent(self) -> Generator[str, None, None]:
        """Return a FRIDAY-persona status report of the current active model."""
        state = active_session.get_state()
        history = active_session.get_history()

        lines = [
            f"Currently running on **{state['provider_name'].capitalize()}** / "
            f"**{state['model_id']}**, Boss.",
            f"Set by: {state['set_by']} — {state.get('reason', '')}",
        ]
        if history:
            last = history[0]
            lines.append(
                f"Previous: {last.get('provider_name', '?')} / {last.get('model_id', '?')}"
            )
        msg = "\n".join(lines)
        self._update_history("assistant", msg)
        yield msg

    def _handle_list_intent(self, intent: ListIntent) -> Generator[str, None, None]:
        """Return a formatted list of available providers and models."""
        from friday.llm.model_catalog import ModelCatalog
        from friday.llm.models.db_models import LLMProvider
        from sqlmodel import Session, select
        from friday.core.database import engine

        catalog = ModelCatalog()
        with Session(engine) as db:
            providers = db.exec(
                select(LLMProvider)
                .where(LLMProvider.is_enabled)
                .order_by(LLMProvider.priority)
            ).all()

        lines = ["Available models, Boss:"]
        for prov in providers:
            if intent.filter_provider and prov.name != intent.filter_provider:
                continue
            models = catalog.list_models(prov.name)
            if models:
                lines.append(f"\n**{prov.display_name}** ({prov.name})")
                for m in models:
                    lines.append(f"  • {m.display_name}  [{m.model_id}]")

        msg = "\n".join(lines)
        self._update_history("assistant", msg)
        yield msg

    def _handle_reset_intent(self) -> Generator[str, None, None]:
        """Reset the session to settings defaults and confirm."""
        previous = active_session.get()
        active_session.reset_to_default()
        new_provider, new_model = active_session.get()
        msg = (
            f"Reset to default, Boss. "
            f"Now using **{new_provider.capitalize()}** / **{new_model}**. "
            f"(Was: {previous[0]} / {previous[1]})"
        )
        self._update_history("assistant", msg)
        yield msg

    def _handle_ambiguous_intent(
        self, intent: AmbiguousIntent
    ) -> Generator[str, None, None]:
        """Ask the user to clarify which model they want."""
        msg = switch_parser.format_ambiguous_response(intent)
        self._update_history("assistant", msg)
        yield msg

    def _handle_diagnostics_intent(self) -> Generator[str, None, None]:
        """
        Generate a full-system diagnostic report covering:
          - Active session (provider, model, set by, when)
          - All providers (enabled/disabled, priority order)
          - All models per provider with capability badges
          - Per-provider API key health (healthy / rate-limited / auth-failed)
          - Ollama availability + available local models
          - Switch history (last 5 events)
          - Connectivity verdict and next steps if anything is wrong
        """
        from datetime import timezone
        from friday.llm.models.db_models import APIKey, LLMProvider, ModelEntry
        from friday.llm.model_catalog import ModelCatalog
        from sqlmodel import Session, select
        from friday.core.database import engine

        now = datetime.now(timezone.utc)
        catalog = ModelCatalog()
        lines: list[str] = []

        # ── Section 1: Active session ──────────────────────────────────────
        state = active_session.get_state()
        lines.append("**FRIDAY FULL SYSTEM DIAGNOSTIC**")
        lines.append("")
        lines.append("**Active Session**")
        lines.append(f"  Provider : {state['provider_name'].capitalize()}")
        lines.append(f"  Model    : {state['model_id']}")
        lines.append(f"  Set by   : {state['set_by']}  ({state.get('reason', '')})")
        if state.get("switched_at"):
            lines.append(f"  Since    : {state['switched_at']}")

        # ── Section 2: Providers + models + keys ──────────────────────────
        lines.append("")
        lines.append("**Providers & API Keys**")

        issues: list[str] = []

        with Session(engine) as db:
            providers = db.exec(
                select(LLMProvider).order_by(LLMProvider.priority)
            ).all()

            for prov in providers:
                status_flag = "✓" if prov.is_enabled else "✗ (disabled)"
                lines.append("")
                lines.append(
                    f"  [{status_flag}] {prov.display_name} ({prov.name})  priority={prov.priority}"
                )

                # Keys for this provider
                keys = db.exec(
                    select(APIKey)
                    .where(APIKey.provider_id == prov.id)
                    .order_by(APIKey.priority)
                ).all()

                if not keys:
                    lines.append("    Keys    : none configured")
                    issues.append(f"{prov.display_name}: no API keys")
                else:
                    healthy, rate_limited, auth_failed = [], [], []
                    for k in keys:
                        if not k.is_active:
                            auth_failed.append(k)
                        elif k.rate_limited_until:
                            rl = k.rate_limited_until
                            if rl.tzinfo is None:
                                rl = rl.replace(tzinfo=timezone.utc)
                            if rl > now:
                                rate_limited.append(k)
                            else:
                                healthy.append(k)
                        else:
                            healthy.append(k)

                    # Summary line
                    parts = []
                    if healthy:
                        parts.append(f"{len(healthy)} healthy")
                    if rate_limited:
                        parts.append(f"{len(rate_limited)} rate-limited")
                    if auth_failed:
                        parts.append(f"{len(auth_failed)} auth-error")
                    lines.append(
                        f"    Keys    : {', '.join(parts) or 'none usable'}  (total: {len(keys)})"
                    )

                    # Per-key detail (label only — never expose key_value)
                    for k in healthy:
                        lines.append(
                            f"    ✓ {k.label}  reqs={k.request_count}  errs={k.error_count}"
                        )
                    for k in rate_limited:
                        wait = max(
                            0,
                            int(
                                (
                                    k.rate_limited_until.replace(tzinfo=timezone.utc)
                                    - now
                                ).total_seconds()
                                / 60
                            ),
                        )
                        lines.append(
                            f"    ⏳ {k.label}  rate-limited (~{wait}m)  errs={k.error_count}"
                        )
                        issues.append(
                            f"{prov.display_name} / {k.label}: rate-limited (~{wait}m)"
                        )
                    for k in auth_failed:
                        lines.append(
                            f"    ✗ {k.label}  AUTH FAILED  errs={k.error_count}"
                        )
                        issues.append(
                            f"{prov.display_name} / {k.label}: auth failed — replace key"
                        )

                # Models for this provider
                models = catalog.list_models(prov.name)
                if models:
                    badges_map = {
                        m.model_id: (m.supports_tools, m.supports_vision)
                        for m in db.exec(
                            select(ModelEntry).where(ModelEntry.provider_id == prov.id)
                        ).all()
                    }
                    model_strs = []
                    for m in models:
                        tools, vision = badges_map.get(m.model_id, (False, False))
                        badges = "".join(
                            filter(
                                None,
                                [
                                    "[tools]" if tools else "",
                                    "[vision]" if vision else "",
                                ],
                            )
                        )
                        model_strs.append(
                            f"{m.display_name}{' ' + badges if badges else ''}"
                        )
                    lines.append(f"    Models  : {', '.join(model_strs)}")

        # ── Section 3: Ollama / local LLM ─────────────────────────────────
        lines.append("")
        lines.append("**Local LLM (Ollama)**")
        try:
            import httpx

            resp = httpx.get("http://localhost:11434/api/tags", timeout=2)
            resp.raise_for_status()
            data = resp.json()
            ollama_models = [
                m.get("name", "").split(":")[0] for m in data.get("models", [])
            ]
            ollama_models = [m for m in ollama_models if m]
            if ollama_models:
                lines.append(f"  Status : ✓ Running  ({len(ollama_models)} model(s))")
                lines.append(f"  Models : {', '.join(ollama_models)}")
            else:
                lines.append("  Status : ⚠ Running but no models installed")
                lines.append("  Tip    : Run `ollama pull llama3.3` to install a model")
        except Exception as e:
            lines.append(f"  Status : ✗ Not detected ({type(e).__name__})")
            lines.append(
                "  Tip    : Install from ollama.ai for zero-cost local fallback"
            )

        # ── Section 4: Switch history ──────────────────────────────────────
        history = active_session.get_history()
        if history:
            lines.append("")
            lines.append("**Recent Model Switches** (last 5)")
            for h in history[:5]:
                lines.append(
                    f"  {h.get('provider_name', '?')}/{h.get('model_id', '?')} "
                    f"← {h.get('set_by', '?')} · {h.get('reason', '')}"
                )

        # ── Section 5: Issues & next steps ────────────────────────────────
        lines.append("")
        if issues:
            lines.append("**Issues Detected**")
            for issue in issues:
                lines.append(f"  ⚠ {issue}")
            lines.append("")
            lines.append("**Next Steps**")
            lines.append("  • Add/replace keys: POST /api/keys")
            lines.append("  • Wait for rate-limits to expire and retry")
            lines.append("  • Install Ollama for local fallback: ollama.ai")
        else:
            lines.append("**Status: All systems nominal, Boss.** ✓")

        msg = "\n".join(lines)
        self._update_history("assistant", msg)
        yield msg

    # ── Offline guardian delegation ───────────────────────────────────────────

    def _handle_llm_exhausted(
        self, user_input: str, error: LLMExhaustedError
    ) -> Generator[str, None, None]:
        """Delegate to OfflineGuardian when all LLM providers are exhausted."""
        try:
            from friday.llm.offline_guardian import offline_guardian

            response = offline_guardian.respond(user_input=user_input, error=error)
        except Exception as guardian_err:
            response = (
                f"Boss, all LLM providers are currently unavailable and the "
                f"offline recovery system also encountered an error: {guardian_err}. "
                f"Please check your API keys and connectivity."
            )
        self._update_history("assistant", response)
        yield response

    # ── Core streaming entry point ────────────────────────────────────────────

    def stream_process(self, user_input: str) -> Generator[str, None, None]:
        """
        Process user input and stream the response token-by-token.

        Pipeline:
          1. SwitchCommandParser — intercept model-switch commands first.
          2. MemoryBus.get_context_for() — retrieve ranked memory context.
          3. Sync (provider, model) from ActiveModelSession + bridge history.
          4. LLMRouter.stream() — memory context injected into system prompt.
          5. Tool execution loop.
          6. MemoryBus.observe_turn() — buffer turn for async extraction.
          7. MemoryBus.consolidate_session_async() — every 5 user turns.
          8. OfflineGuardian on LLMExhaustedError.

        Args:
            user_input: Raw text from the user (or empty string on tool-loop re-entry).

        Yields:
            str: Incremental text chunks of FRIDAY's response.
        """
        # ── 1. Switch command interception ──────────────────────────────────
        if user_input:
            intent = switch_parser.parse(user_input)

            if isinstance(intent, SwitchIntent):
                self._update_history("user", user_input)
                yield from self._handle_switch_intent(intent)
                return

            if isinstance(intent, StatusIntent):
                self._update_history("user", user_input)
                yield from self._handle_status_intent()
                return

            if isinstance(intent, ListIntent):
                self._update_history("user", user_input)
                yield from self._handle_list_intent(intent)
                return

            if isinstance(intent, ResetIntent):
                self._update_history("user", user_input)
                yield from self._handle_reset_intent()
                return

            if isinstance(intent, AmbiguousIntent):
                self._update_history("user", user_input)
                yield from self._handle_ambiguous_intent(intent)
                return

            if isinstance(intent, DiagnosticsIntent):
                self._update_history("user", user_input)
                yield from self._handle_diagnostics_intent()
                return

            # Not a switch command — buffer and fall through to LLM
            self._last_user_input = user_input
            self._update_history("user", user_input)

        # ── 2. Memory context retrieval (fast — pre-ranked, < 200ms) ────────
        memory_context_str = ""
        if user_input and settings.memory_enabled:
            try:
                mem_ctx = self.memory.get_context_for(user_input)
                memory_context_str = mem_ctx.to_prompt_string()

                # Phase C: Inject preloaded context if present
                if self.memory.working.preloaded_context:
                    preloaded_str = (
                        self.memory.working.preloaded_context.to_prompt_string()
                    )
                    if preloaded_str:
                        memory_context_str = f"[PROACTIVE PRELOADED CONTEXT]\n{preloaded_str}\n\n{memory_context_str}"
                    # Clear it after use so we don't keep injecting it forever
                    self.memory.working.preloaded_context = None

            except Exception:
                pass  # Memory failure must never block the response

        # ── 3. Resolve active session + bridge history ──────────────────────
        active_provider, active_model = self._sync_provider_from_session()

        # ── 4. LLM streaming with memory-enriched system prompt ─────────────
        tool_schemas = self.tool_router.get_unified_schemas()

        try:
            final_chunk: StreamChunk | None = None
            response_parts: list[str] = []  # accumulate for memory observation

            for chunk in self.llm.stream(
                messages=self.conversation_history,
                system_prompt=self._get_system_prompt(memory_context_str),
                provider_name=active_provider,
                model=active_model,
                tool_schemas=tool_schemas,
            ):
                if chunk.text:
                    response_parts.append(chunk.text)
                    yield chunk.text
                if chunk.is_final:
                    final_chunk = chunk

            if final_chunk is None:
                return

            if final_chunk.stop_reason == "tool_use" and final_chunk.tool_calls:
                # Record assistant's tool-use turn in history
                self._record_tool_use_assistant(final_chunk, active_provider)

                # Execute every requested tool
                for tc in final_chunk.tool_calls:
                    yield f"\n\n*[FRIDAY is using tool: {tc.name}...]*\n"
                    result = self.tool_router.execute(tc.name, tc.arguments)
                    self._record_tool_result(tc.id, tc.name, result, active_provider)

                # Re-stream with tool results injected into history
                yield from self.stream_process("")

            else:
                # Normal end — persist full response to LLM history
                content = (
                    final_chunk.raw_assistant_content
                    if final_chunk.raw_assistant_content is not None
                    else ""
                )
                self._update_history("assistant", content)

                # ── 5. Memory observation (non-blocking) ─────────────────────
                if self._last_user_input and settings.memory_enabled:
                    assistant_text = "".join(response_parts)
                    self.memory.observe_turn(self._last_user_input, assistant_text)
                    self._last_user_input = ""

                    # ── 6. Async consolidation every 5 user turns ─────────────
                    if self.memory.working.should_consolidate():
                        self.memory.consolidate_session_async(self.conversation_history)

        except LLMExhaustedError as e:
            # ── 7. Auto-switch notification + OfflineGuardian ─────────────
            fallback_provider = settings.default_provider
            fallback_model = settings.default_model
            active_session.notify_hard_failure(
                failed_provider=active_provider,
                failed_model=active_model,
                fallback_provider=fallback_provider,
                fallback_model=fallback_model,
                error_summary=str(e),
            )
            yield from self._handle_llm_exhausted(user_input, e)

        except Exception as e:
            yield f"\n[FRIDAY Error: {e}]"

    # ── Voice Pipeline Memory Commit ──────────────────────────────────────────

    def commit_memory_explicit(self, user_input: str, assistant_response: str) -> None:
        """
        Explicitly commit memory and observe turn. Used by the Voice Pipeline
        to only commit what was actually spoken (handling interrupts).
        """
        if not user_input or not assistant_response or not settings.memory_enabled:
            return

        # Update history with the explicitly spoken text (replaces the generated one if needed)
        # Note: Depending on timing, the full generated text might already be in self.conversation_history
        # due to stream_process finishing. We can trim/replace the last assistant message.
        if (
            self.conversation_history
            and self.conversation_history[-1]["role"] == "assistant"
        ):
            self.conversation_history[-1]["content"] = assistant_response

        self.memory.observe_turn(user_input, assistant_response)

        if self.memory.working.should_consolidate():
            self.memory.consolidate_session_async(self.conversation_history)
