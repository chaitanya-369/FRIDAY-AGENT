# Graph Report - D:\PROJECTS\FRIDAY-AGENT  (2026-04-23)

## Corpus Check
- 80 files · ~154,987 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 982 nodes · 3319 edges · 109 communities detected
- Extraction: 26% EXTRACTED · 74% INFERRED · 0% AMBIGUOUS · INFERRED: 2466 edges (avg confidence: 0.54)
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
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 108|Community 108]]

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 193 edges
2. `APIKey` - 136 edges
3. `ModelCatalog` - 111 edges
4. `Memory` - 108 edges
5. `StreamChunk` - 94 edges
6. `MemoryType` - 93 edges
7. `Task` - 86 edges
8. `ModelEntry` - 81 edges
9. `LLMExhaustedError` - 75 edges
10. `MemorySource` - 69 edges

## Surprising Connections (you probably didn't know these)
- `Stream the response from FRIDAY's brain via Server-Sent Events (SSE).` --uses--> `FridayBrain`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\api\routes\chat.py → D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py
- `StreamChunk` --uses--> `Streams responses from DeepSeek models (deepseek-chat, deepseek-reasoner).`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\adapters\base.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\adapters\deepseek_adapter.py
- `MemoryType` --uses--> `Remove a memory from the vector index.`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\memory\types.py → D:\PROJECTS\FRIDAY-AGENT\friday\memory\vector_store.py
- `MemoryType` --uses--> `Semantic similarity search over all stored memories.          Returns results so`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\memory\types.py → D:\PROJECTS\FRIDAY-AGENT\friday\memory\vector_store.py
- `MemoryType` --uses--> `Return the total number of memories in the vector index.`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\memory\types.py → D:\PROJECTS\FRIDAY-AGENT\friday\memory\vector_store.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (182): A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment, StreamChunk, friday/core/brain.py  FRIDAY's core intelligence — now powered by the Omni-LLM l, Persist a tool result into history in the correct format for the         active, Bridge history from the current provider format to the new provider format,, Read the active (provider, model) from the session, bridge history         if ne, Process user input and stream the response token-by-token.          Handles the, Read the active (provider, model) from the session, bridge history         if ne (+174 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (123): FridayBrain, Stream the response from FRIDAY's brain., count_lines(), ActiveSession, Prepend a new entry to switch_history, keeping only the latest 10.         Mutat, Single-row table (always id=1) that persists FRIDAY's currently active     LLM s, Deserialize switch_history JSON into a list of dicts., _block_attr() (+115 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (75): classify_intent(), QueryIntent, friday/memory/retrieval/engine.py  RetrievalEngine — multi-modal memory retrieva, Run semantic similarity search. Returns empty list if unavailable., Run semantic similarity search. Returns empty list if unavailable., Structured SQL-based retrieval.          Fetches:           - High-importance fa, Structured SQL-based retrieval.          Fetches:           - High-importance, Lightweight keyword-based intent classification.         Phase B will replace th (+67 more)

### Community 3 - "Community 3"
Cohesion: 0.1
Nodes (80): Enum, friday/memory/episodic.py  EpisodeStore — Tier 1 of the FRIDAY Memory Mesh.  SQL, Retrieve a memory by ID, bumping access stats., Fetch top memories of a given type, ordered by effective score., Fetch memories created or accessed in the last N hours., Mark a memory as superseded (versioning — never hard-delete).         The supers, Boss explicitly asked to forget this memory.         We set confidence=0 and mar, Return all active (non-superseded, non-expired) memories. (+72 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (43): ABC, AnthropicAdapter, friday/llm/adapters/anthropic_adapter.py  Adapter for Anthropic's Claude models., Streams responses from Anthropic Claude models.      Tool calling uses Anthropic, Streams responses from Anthropic Claude models.      Tool calling uses Anthropic, BaseAdapter, format_tool(), friday/llm/adapters/base.py  Core abstractions for the Omni-LLM adapter layer. (+35 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (46): BaseModel, chat_endpoint(), ChatRequest, Stream the response from FRIDAY's brain via Server-Sent Events (SSE)., add_key(), key_health(), list_keys(), _mask() (+38 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (19): BaseTool, Abstract base class for all FRIDAY tools., BaseTool, Manages the registration and execution of tools.     Also handles converting too, Registers the built-in FRIDAY tools., Registers the built-in FRIDAY tools., Returns tool schemas in Anthropic's format., Returns tool schemas in Anthropic's format. (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (34): Exception, OfflineGuardian, OllamaNotAvailable, friday/llm/offline_guardian.py  OfflineGuardian — FRIDAY's always-on resilience, Call Ollama's OpenAI-compat chat endpoint and return the full response., Inspect the api_keys table to build a human-readable status summary.          Re, Build a rich, FRIDAY-persona diagnostic response when no LLM is available., Generate a response when all cloud providers are exhausted.          Tries Ollam (+26 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (18): _is_false_positive(), _normalise(), _similarity(), _strip_stop_words(), SwitchCommandParser, parser(), tests/test_switch_parser.py  Parametrized tests for friday/llm/switch_parser.py, test_confidence_is_between_zero_and_one() (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.33
Nodes (5): downgrade(), add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0, Add the active_session singleton table., Drop the active_session table., upgrade()

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (3): create_db_and_tables(), friday/core/database.py  SQLite engine and table creation for FRIDAY-AGENT.  IMP, Create all tables and seed providers/keys/models from .env (idempotent).

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (2): lifespan(), Startup/shutdown lifecycle — launches the Slack bot alongside the API.

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (3): BaseSettings, friday/config/settings.py  Pydantic Settings for FRIDAY-AGENT.  LLM provider/mod, Settings

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (0): 

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): Quick check: imports the bot module and calls start_in_background(), then waits

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Return 'anthropic' or 'openai' based on provider name.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Extract the 'type' from a block (dict or object).

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Extract text content from a text block.

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Extract an arbitrary attribute from a block (dict or object).

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Ensure content is a list (wraps single blocks).

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Stream one LLM turn.          Args:             messages      : Conversation his

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Convert a unified tool definition to this provider's native schema.          Arg

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): A detailed description of what the tool does and when to use it.

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): The JSON schema for the tool's parameters.         Example:         {

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Executes the tool with the given arguments.         Returns a string or JSON-ser

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (0): 

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Persistent store for a single typed memory unit.      confidence, stability, and

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Structured actionable task extracted from conversation.

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): A complete conversation session.      raw_turns_json is the full conversation lo

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): A named entity node in the knowledge graph.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): A typed, weighted, temporal edge between two entity nodes.      Relation type ex

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): A detected contradiction between two memories, pending resolution.      conflict

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): The type of a memory unit.      Each type has different:       - decay rate

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Where did this memory originate?

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): A single typed unit of FRIDAY's long-term memory.      Scoring dimensions:

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Composite score used for retrieval ranking.          Weights:           40% conf

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): A structured, actionable task extracted from conversation.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): A complete conversation session.      Raw turns are stored for archive/audit. Th

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): A named entity in the knowledge graph (person, project, tool, concept).

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): The assembled, ranked, deduplicated memory context ready for     injection into

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Format the context for injection into the FRIDAY system prompt.         Returns

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Create all tables and seed providers/keys/models from .env (idempotent).

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Add the active_session singleton table.

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Drop the active_session table.

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Reset the active session to settings defaults (default_provider / default_model)

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Create all tables and seed providers/keys/models from .env (idempotent).

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (0): 

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Converts conversation history between Anthropic and OpenAI-compatible formats.

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Convert a conversation history list from one provider's format to another.

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Return 'anthropic' or 'openai' based on provider name.

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Convert Anthropic-format history to OpenAI-compat format.          Anthropic his

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Convert Anthropic user-role content blocks to OpenAI messages.         Tool resu

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Convert Anthropic assistant content blocks to a single OpenAI assistant message.

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Convert OpenAI-compat format history to Anthropic format.          OpenAI histor

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Extract the 'type' from a block (dict or object).

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Extract text content from a text block.

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): Extract an arbitrary attribute from a block (dict or object).

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Ensure content is a list (wraps single blocks).

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): A tool invocation parsed from an LLM response.      Attributes:         id   : P

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Abstract base class for all LLM provider adapters.      Each concrete adapter ha

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Stream one LLM turn.          Args:             messages      : Conversation his

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): Convert a unified tool definition to this provider's native schema.          Arg

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): Convert a list of unified tool schemas to provider-native format.          Args:

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): A registered LLM provider.

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): An API key belonging to a provider. Multiple keys per provider are allowed.

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): A known model for a given provider.

### Community 91 - "Community 91"
Cohesion: 1.0
Nodes (1): Single-row table (always id=1) that persists FRIDAY's currently active     LLM s

### Community 92 - "Community 92"
Cohesion: 1.0
Nodes (1): Deserialize switch_history JSON into a list of dicts.

### Community 93 - "Community 93"
Cohesion: 1.0
Nodes (1): Prepend a new entry to switch_history, keeping only the latest 10.         Mutat

### Community 94 - "Community 94"
Cohesion: 1.0
Nodes (1): Abstract base class for all FRIDAY tools.

### Community 95 - "Community 95"
Cohesion: 1.0
Nodes (1): The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo

### Community 96 - "Community 96"
Cohesion: 1.0
Nodes (1): The JSON schema for the tool's parameters.         Example:         {

### Community 97 - "Community 97"
Cohesion: 1.0
Nodes (1): Executes the tool with the given arguments.         Returns a string or JSON-ser

### Community 98 - "Community 98"
Cohesion: 1.0
Nodes (1): Run migrations in 'offline' mode.      This configures the context with just a U

### Community 99 - "Community 99"
Cohesion: 1.0
Nodes (1): Run migrations in 'online' mode.      In this scenario we need to create an Engi

### Community 100 - "Community 100"
Cohesion: 1.0
Nodes (1): A registered LLM provider.

### Community 101 - "Community 101"
Cohesion: 1.0
Nodes (1): An API key belonging to a provider. Multiple keys per provider are allowed.

### Community 102 - "Community 102"
Cohesion: 1.0
Nodes (1): A known model for a given provider.

### Community 103 - "Community 103"
Cohesion: 1.0
Nodes (1): Core intelligence component of the FRIDAY Agent.          This class handles t

### Community 104 - "Community 104"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 105 - "Community 105"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.          Thi

### Community 106 - "Community 106"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 107 - "Community 107"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.

### Community 108 - "Community 108"
Cohesion: 1.0
Nodes (1): Processes the input and yields the response token by token.

## Knowledge Gaps
- **163 isolated node(s):** `add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0`, `Add the active_session singleton table.`, `Drop the active_session table.`, `Startup/shutdown lifecycle — launches the Slack bot alongside the API.`, `Reset the active session to settings defaults (default_provider / default_model)` (+158 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (2 nodes): `App.tsx`, `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `OfflineIndicator.tsx`, `handleRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `capture_screenshot()`, `capture_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `ingest_docs.py`, `ingest_directory()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `test_bg_slack.py`, `Quick check: imports the bot module and calls start_in_background(), then waits`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `test_socket_full.py`, `handle_mention()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `persona.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Return 'anthropic' or 'openai' based on provider name.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Extract the 'type' from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Extract text content from a text block.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Extract an arbitrary attribute from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Ensure content is a list (wraps single blocks).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Stream one LLM turn.          Args:             messages      : Conversation his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Convert a unified tool definition to this provider's native schema.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `A detailed description of what the tool does and when to use it.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `The JSON schema for the tool's parameters.         Example:         {`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Executes the tool with the given arguments.         Returns a string or JSON-ser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `slack_diag.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `verify_gemini.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `verify_groq.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `verify_slack.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `verify_socket.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `install_act.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Persistent store for a single typed memory unit.      confidence, stability, and`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Structured actionable task extracted from conversation.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `A complete conversation session.      raw_turns_json is the full conversation lo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `A named entity node in the knowledge graph.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `A typed, weighted, temporal edge between two entity nodes.      Relation type ex`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `A detected contradiction between two memories, pending resolution.      conflict`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `The type of a memory unit.      Each type has different:       - decay rate`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Where did this memory originate?`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `A single typed unit of FRIDAY's long-term memory.      Scoring dimensions:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Composite score used for retrieval ranking.          Weights:           40% conf`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `A structured, actionable task extracted from conversation.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `A complete conversation session.      Raw turns are stored for archive/audit. Th`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `A named entity in the knowledge graph (person, project, tool, concept).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `The assembled, ranked, deduplicated memory context ready for     injection into`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Format the context for injection into the FRIDAY system prompt.         Returns`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Create all tables and seed providers/keys/models from .env (idempotent).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Add the active_session singleton table.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Drop the active_session table.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Reset the active session to settings defaults (default_provider / default_model)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Create all tables and seed providers/keys/models from .env (idempotent).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Start the Slack Socket Mode bot in a daemon thread.      Uses handler.connect()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Converts conversation history between Anthropic and OpenAI-compatible formats.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Convert a conversation history list from one provider's format to another.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Return 'anthropic' or 'openai' based on provider name.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Convert Anthropic-format history to OpenAI-compat format.          Anthropic his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Convert Anthropic user-role content blocks to OpenAI messages.         Tool resu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Convert Anthropic assistant content blocks to a single OpenAI assistant message.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Convert OpenAI-compat format history to Anthropic format.          OpenAI histor`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Extract the 'type' from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Extract text content from a text block.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `Extract an arbitrary attribute from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Ensure content is a list (wraps single blocks).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `A tool invocation parsed from an LLM response.      Attributes:         id   : P`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `A single unit yielded by BaseAdapter.stream().      Text chunks arrive increment`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `Abstract base class for all LLM provider adapters.      Each concrete adapter ha`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `Stream one LLM turn.          Args:             messages      : Conversation his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `Convert a unified tool definition to this provider's native schema.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `Convert a list of unified tool schemas to provider-native format.          Args:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `A registered LLM provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `An API key belonging to a provider. Multiple keys per provider are allowed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `A known model for a given provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 91`** (1 nodes): `Single-row table (always id=1) that persists FRIDAY's currently active     LLM s`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 92`** (1 nodes): `Deserialize switch_history JSON into a list of dicts.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 93`** (1 nodes): `Prepend a new entry to switch_history, keeping only the latest 10.         Mutat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 94`** (1 nodes): `Abstract base class for all FRIDAY tools.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 95`** (1 nodes): `The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 96`** (1 nodes): `The JSON schema for the tool's parameters.         Example:         {`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 97`** (1 nodes): `Executes the tool with the given arguments.         Returns a string or JSON-ser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 98`** (1 nodes): `Run migrations in 'offline' mode.      This configures the context with just a U`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 99`** (1 nodes): `Run migrations in 'online' mode.      In this scenario we need to create an Engi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 100`** (1 nodes): `A registered LLM provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 101`** (1 nodes): `An API key belonging to a provider. Multiple keys per provider are allowed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 102`** (1 nodes): `A known model for a given provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 103`** (1 nodes): `Core intelligence component of the FRIDAY Agent.          This class handles t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 104`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 105`** (1 nodes): `Processes user input and streams the LLM response token by token.          Thi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 106`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 107`** (1 nodes): `Processes user input and streams the LLM response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 108`** (1 nodes): `Processes the input and yields the response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `APIKey` connect `Community 0` to `Community 1`, `Community 3`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `StreamChunk` connect `Community 0` to `Community 1`, `Community 4`, `Community 6`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 190 inferred relationships involving `LLMProvider` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`LLMProvider` has 190 INFERRED edges - model-reasoned connections that need verification._
- **Are the 133 inferred relationships involving `APIKey` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`APIKey` has 133 INFERRED edges - model-reasoned connections that need verification._
- **Are the 106 inferred relationships involving `ModelCatalog` (e.g. with `friday/api/routes/models_catalog.py  REST endpoints for browsing the model catal` and `List all active models across every registered provider.`) actually correct?**
  _`ModelCatalog` has 106 INFERRED edges - model-reasoned connections that need verification._
- **Are the 104 inferred relationships involving `Memory` (e.g. with `EpisodeStore` and `friday/memory/episodic.py  EpisodeStore — Tier 1 of the FRIDAY Memory Mesh.  SQL`) actually correct?**
  _`Memory` has 104 INFERRED edges - model-reasoned connections that need verification._