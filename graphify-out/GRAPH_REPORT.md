# Graph Report - D:\PROJECTS\FRIDAY-AGENT  (2026-04-23)

## Corpus Check
- 80 files · ~113,889 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 936 nodes · 3090 edges · 96 communities detected
- Extraction: 28% EXTRACTED · 72% INFERRED · 0% AMBIGUOUS · INFERRED: 2237 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 193 edges
2. `APIKey` - 136 edges
3. `ModelCatalog` - 111 edges
4. `StreamChunk` - 94 edges
5. `ModelEntry` - 81 edges
6. `Memory` - 77 edges
7. `LLMExhaustedError` - 75 edges
8. `ToolRouter` - 64 edges
9. `MemoryType` - 62 edges
10. `LLMRouter` - 61 edges

## Surprising Connections (you probably didn't know these)
- `Stream the response from FRIDAY's brain via Server-Sent Events (SSE).` --uses--> `FridayBrain`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\api\routes\chat.py → D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py
- `StreamChunk` --uses--> `Streams responses from DeepSeek models (deepseek-chat, deepseek-reasoner).`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\adapters\base.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\adapters\deepseek_adapter.py
- `Emit SQL to stdout without a live DB connection.` --uses--> `LLMProvider`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\alembic\env.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Emit SQL to stdout without a live DB connection.` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\alembic\env.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Emit SQL to stdout without a live DB connection.` --uses--> `ModelEntry`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\alembic\env.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (120): classify_intent(), QueryIntent, friday/memory/retrieval/engine.py  RetrievalEngine — multi-modal memory retrieva, Run semantic similarity search. Returns empty list if unavailable., Structured SQL-based retrieval.          Fetches:           - High-importance fa, Lightweight keyword-based intent classification.         Phase B will replace th, Rough classification of what the user's query needs from memory., A single memory returned from the retrieval engine with its final score. (+112 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (176): A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment, StreamChunk, friday/core/brain.py  FRIDAY's core intelligence — now powered by the Omni-LLM l, Persist a tool result into history in the correct format for the         active, Bridge history from the current provider format to the new provider format,, Read the active (provider, model) from the session, bridge history         if ne, Process user input and stream the response token-by-token.          Handles the, Read the active (provider, model) from the session, bridge history         if ne (+168 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (104): FridayBrain, Stream the response from FRIDAY's brain., count_lines(), ActiveSession, Prepend a new entry to switch_history, keeping only the latest 10.         Mutat, Single-row table (always id=1) that persists FRIDAY's currently active     LLM s, Deserialize switch_history JSON into a list of dicts., _block_attr() (+96 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (67): BaseModel, chat_endpoint(), ChatRequest, Stream the response from FRIDAY's brain via Server-Sent Events (SSE)., add_key(), key_health(), list_keys(), _mask() (+59 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (41): ABC, AnthropicAdapter, friday/llm/adapters/anthropic_adapter.py  Adapter for Anthropic's Claude models., Streams responses from Anthropic Claude models.      Tool calling uses Anthropic, Streams responses from Anthropic Claude models.      Tool calling uses Anthropic, BaseAdapter, format_tool(), friday/llm/adapters/base.py  Core abstractions for the Omni-LLM adapter layer. (+33 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (19): BaseTool, Abstract base class for all FRIDAY tools., BaseTool, Manages the registration and execution of tools.     Also handles converting too, Registers the built-in FRIDAY tools., Registers the built-in FRIDAY tools., Returns tool schemas in Anthropic's format., Returns tool schemas in Anthropic's format. (+11 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (33): Exception, OfflineGuardian, OllamaNotAvailable, friday/llm/offline_guardian.py  OfflineGuardian — FRIDAY's always-on resilience, Call Ollama's OpenAI-compat chat endpoint and return the full response., Inspect the api_keys table to build a human-readable status summary.          Re, Build a rich, FRIDAY-persona diagnostic response when no LLM is available., Generate a response when all cloud providers are exhausted.          Tries Ollam (+25 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (19): Return all active ModelEntry rows across all providers., _is_false_positive(), _normalise(), _similarity(), _strip_stop_words(), SwitchCommandParser, parser(), tests/test_switch_parser.py  Parametrized tests for friday/llm/switch_parser.py (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.33
Nodes (5): downgrade(), add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0, Add the active_session singleton table., Drop the active_session table., upgrade()

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (3): create_db_and_tables(), friday/core/database.py  SQLite engine and table creation for FRIDAY-AGENT.  IMP, Create all tables and seed providers/keys/models from .env (idempotent).

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (4): ConversationTurn, _generate_session_id(), friday/memory/working.py  WorkingMemory — Tier 0 of the FRIDAY Memory Mesh.  Liv, A single turn in the current conversation.

### Community 11 - "Community 11"
Cohesion: 0.4
Nodes (4): Emit SQL to stdout without a live DB connection., Run migrations against the live DB engine., run_migrations_offline(), run_migrations_online()

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (2): lifespan(), Startup/shutdown lifecycle — launches the Slack bot alongside the API.

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (3): BaseSettings, friday/config/settings.py  Pydantic Settings for FRIDAY-AGENT.  LLM provider/mod, Settings

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (2): EntityRow, A named entity node in the knowledge graph.

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Quick check: imports the bot module and calls start_in_background(), then waits

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Return 'anthropic' or 'openai' based on provider name.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Extract the 'type' from a block (dict or object).

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Extract text content from a text block.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Extract an arbitrary attribute from a block (dict or object).

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Ensure content is a list (wraps single blocks).

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Stream one LLM turn.          Args:             messages      : Conversation his

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Convert a unified tool definition to this provider's native schema.          Arg

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (0): 

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): A detailed description of what the tool does and when to use it.

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): The JSON schema for the tool's parameters.         Example:         {

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Executes the tool with the given arguments.         Returns a string or JSON-ser

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (0): 

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (0): 

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (0): 

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (0): 

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Create all tables and seed providers/keys/models from .env (idempotent).

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Add the active_session singleton table.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Drop the active_session table.

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Reset the active session to settings defaults (default_provider / default_model)

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Create all tables and seed providers/keys/models from .env (idempotent).

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (0): 

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Converts conversation history between Anthropic and OpenAI-compatible formats.

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Convert a conversation history list from one provider's format to another.

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Return 'anthropic' or 'openai' based on provider name.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Convert Anthropic-format history to OpenAI-compat format.          Anthropic his

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Convert Anthropic user-role content blocks to OpenAI messages.         Tool resu

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Convert Anthropic assistant content blocks to a single OpenAI assistant message.

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Convert OpenAI-compat format history to Anthropic format.          OpenAI histor

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Extract the 'type' from a block (dict or object).

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Extract text content from a text block.

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Extract an arbitrary attribute from a block (dict or object).

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Ensure content is a list (wraps single blocks).

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): A tool invocation parsed from an LLM response.      Attributes:         id   : P

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Abstract base class for all LLM provider adapters.      Each concrete adapter ha

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Stream one LLM turn.          Args:             messages      : Conversation his

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Convert a unified tool definition to this provider's native schema.          Arg

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Convert a list of unified tool schemas to provider-native format.          Args:

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): A registered LLM provider.

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): An API key belonging to a provider. Multiple keys per provider are allowed.

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): A known model for a given provider.

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Single-row table (always id=1) that persists FRIDAY's currently active     LLM s

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Deserialize switch_history JSON into a list of dicts.

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Prepend a new entry to switch_history, keeping only the latest 10.         Mutat

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Abstract base class for all FRIDAY tools.

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): The JSON schema for the tool's parameters.         Example:         {

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Executes the tool with the given arguments.         Returns a string or JSON-ser

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Run migrations in 'offline' mode.      This configures the context with just a U

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): Run migrations in 'online' mode.      In this scenario we need to create an Engi

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): A registered LLM provider.

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): An API key belonging to a provider. Multiple keys per provider are allowed.

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): A known model for a given provider.

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): Core intelligence component of the FRIDAY Agent.          This class handles t

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.          Thi

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): Processes the input and yields the response token by token.

## Knowledge Gaps
- **148 isolated node(s):** `add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0`, `Add the active_session singleton table.`, `Drop the active_session table.`, `Startup/shutdown lifecycle — launches the Slack bot alongside the API.`, `Reset the active session to settings defaults (default_provider / default_model)` (+143 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 17`** (2 nodes): `App.tsx`, `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `OfflineIndicator.tsx`, `handleRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `capture_screenshot()`, `capture_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `ingest_docs.py`, `ingest_directory()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `test_bg_slack.py`, `Quick check: imports the bot module and calls start_in_background(), then waits`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `test_socket_full.py`, `handle_mention()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `persona.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Return 'anthropic' or 'openai' based on provider name.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Extract the 'type' from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Extract text content from a text block.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Extract an arbitrary attribute from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Ensure content is a list (wraps single blocks).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Stream one LLM turn.          Args:             messages      : Conversation his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Convert a unified tool definition to this provider's native schema.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `A detailed description of what the tool does and when to use it.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `The JSON schema for the tool's parameters.         Example:         {`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Executes the tool with the given arguments.         Returns a string or JSON-ser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `slack_diag.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `verify_gemini.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `verify_groq.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `verify_slack.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `verify_socket.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `install_act.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Create all tables and seed providers/keys/models from .env (idempotent).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Add the active_session singleton table.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Drop the active_session table.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Reset the active session to settings defaults (default_provider / default_model)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Create all tables and seed providers/keys/models from .env (idempotent).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Start the Slack Socket Mode bot in a daemon thread.      Uses handler.connect()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Converts conversation history between Anthropic and OpenAI-compatible formats.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Convert a conversation history list from one provider's format to another.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Return 'anthropic' or 'openai' based on provider name.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Convert Anthropic-format history to OpenAI-compat format.          Anthropic his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Convert Anthropic user-role content blocks to OpenAI messages.         Tool resu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Convert Anthropic assistant content blocks to a single OpenAI assistant message.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Convert OpenAI-compat format history to Anthropic format.          OpenAI histor`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Extract the 'type' from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Extract text content from a text block.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Extract an arbitrary attribute from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Ensure content is a list (wraps single blocks).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `A tool invocation parsed from an LLM response.      Attributes:         id   : P`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Abstract base class for all LLM provider adapters.      Each concrete adapter ha`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Stream one LLM turn.          Args:             messages      : Conversation his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Convert a unified tool definition to this provider's native schema.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Convert a list of unified tool schemas to provider-native format.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `A registered LLM provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `An API key belonging to a provider. Multiple keys per provider are allowed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `A known model for a given provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Single-row table (always id=1) that persists FRIDAY's currently active     LLM s`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Deserialize switch_history JSON into a list of dicts.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Prepend a new entry to switch_history, keeping only the latest 10.         Mutat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Abstract base class for all FRIDAY tools.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `The JSON schema for the tool's parameters.         Example:         {`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `Executes the tool with the given arguments.         Returns a string or JSON-ser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `Run migrations in 'offline' mode.      This configures the context with just a U`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `Run migrations in 'online' mode.      In this scenario we need to create an Engi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `A registered LLM provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `An API key belonging to a provider. Multiple keys per provider are allowed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `A known model for a given provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `Core intelligence component of the FRIDAY Agent.          This class handles t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `Processes user input and streams the LLM response token by token.          Thi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `Processes user input and streams the LLM response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `Processes the input and yields the response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 11`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `APIKey` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 5`, `Community 6`, `Community 11`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `StreamChunk` connect `Community 1` to `Community 2`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 190 inferred relationships involving `LLMProvider` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`LLMProvider` has 190 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `APIKey` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`APIKey` has 133 INFERRED edges - model-reasoned connections that need verification._
- **Are the 106 inferred relationships involving `ModelCatalog` (e.g. with `friday/api/routes/models_catalog.py  REST endpoints for browsing the model catal` and `List all active models across every registered provider.`) actually correct?**
  _`ModelCatalog` has 106 INFERRED edges - model-reasoned connections that need verification._
- **Are the 92 inferred relationships involving `StreamChunk` (e.g. with `FridayBrain` and `friday/core/brain.py  FRIDAY's core intelligence — now powered by the Omni-LLM l`) actually correct?**
  _`StreamChunk` has 92 INFERRED edges - model-reasoned connections that need verification._