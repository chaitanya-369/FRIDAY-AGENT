# Graph Report - D:\PROJECTS\FRIDAY-AGENT  (2026-04-23)

## Corpus Check
- 64 files · ~86,603 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 542 nodes · 1469 edges · 55 communities detected
- Extraction: 40% EXTRACTED · 60% INFERRED · 0% AMBIGUOUS · INFERRED: 888 edges (avg confidence: 0.56)
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

## God Nodes (most connected - your core abstractions)
1. `LLMProvider` - 111 edges
2. `APIKey` - 78 edges
3. `ModelCatalog` - 63 edges
4. `StreamChunk` - 57 edges
5. `LLMExhaustedError` - 46 edges
6. `ModelEntry` - 46 edges
7. `FridayBrain` - 45 edges
8. `ToolRouter` - 42 edges
9. `LLMRouter` - 38 edges
10. `ActiveSession` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Selects healthy API keys for a provider using a configurable strategy.      Rota` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\key_pool.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Load active, non-rate-limited keys from DB for this provider.` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\key_pool.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Persist field updates to an APIKey row.` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\key_pool.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Return the next healthy key according to the configured strategy.         Return` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\key_pool.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py
- `Increment request_count and update last_used_at.` --uses--> `APIKey`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\llm\key_pool.py → D:\PROJECTS\FRIDAY-AGENT\friday\llm\models\db_models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (70): BaseModel, ActiveSession, APIKey, ModelEntry, friday/llm/models/db_models.py  SQLModel table definitions for the Omni-LLM laye, Prepend a new entry to switch_history, keeping only the latest 10.         Mutat, An API key belonging to a provider. Multiple keys per provider are allowed., A known model for a given provider. (+62 more)

### Community 1 - "Community 1"
Cohesion: 0.09
Nodes (67): friday/core/brain.py  FRIDAY's core intelligence — now powered by the Omni-LLM l, Read the active (provider, model) from the session, bridge history         if ne, Persist the assistant's tool-use turn into history in the correct         format, Persist a tool result into history in the correct format for the         active, Execute a confirmed model switch and yield a confirmation message., Return a FRIDAY-persona status report of the current active model., Return a formatted list of available providers and models., Reset the session to settings defaults and confirm. (+59 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (48): ABC, AnthropicAdapter, friday/llm/adapters/anthropic_adapter.py  Adapter for Anthropic's Claude models., Streams responses from Anthropic Claude models.      Tool calling uses Anthropic, BaseAdapter, format_tool(), friday/llm/adapters/base.py  Core abstractions for the Omni-LLM adapter layer., Convert a list of unified tool schemas to provider-native format.          Args: (+40 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (32): FridayBrain, chat_endpoint(), ChatRequest, Stream the response from FRIDAY's brain., Stream the response from FRIDAY's brain via Server-Sent Events (SSE)., count_lines(), delete_key(), Return all active ModelEntry rows for a given provider name. (+24 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (19): BaseTool, Abstract base class for all FRIDAY tools., BaseTool, Core intelligence component of the FRIDAY Agent.      This class handles the L, Retrieves and formats the FRIDAY persona prompt with dynamic context., Appends a message to the conversation history, maintaining a sliding window of m, Processes user input and streams the LLM response token by token.          Thi, create_db_and_tables() (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (30): Exception, OfflineGuardian, OllamaNotAvailable, friday/llm/offline_guardian.py  OfflineGuardian — FRIDAY's always-on resilience, Call Ollama's OpenAI-compat chat endpoint and return the full response., Inspect the api_keys table to build a human-readable status summary.          Re, Build a rich, FRIDAY-persona diagnostic response when no LLM is available., Generate a response when all cloud providers are exhausted.          Tries Ollam (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (30): add_key(), key_health(), list_keys(), _mask(), friday/api/routes/keys.py  REST endpoints for managing API keys. Supports multip, Send a minimal test request to validate the key works right now., Return key with all but last 4 chars masked., List all API keys (values masked). (+22 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (12): KeyPool, Mark the key as rate-limited until retry_after_seconds from now., Permanently deactivate a key that returned an authentication error., Increment error_count for a generic (non-rate-limit, non-auth) failure., True if no healthy keys remain., Selects healthy API keys for a provider using a configurable strategy.      Rota, Load active, non-rate-limited keys from DB for this provider., Persist field updates to an APIKey row. (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (13): _block_attr(), _block_text(), _block_type(), _family(), _normalise_blocks(), friday/llm/history_bridge.py  SmartHistoryBridge — converts conversation history, Convert Anthropic-format history to OpenAI-compat format.          Anthropic his, Convert Anthropic user-role content blocks to OpenAI messages.         Tool resu (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (13): create_provider(), delete_provider(), list_providers(), friday/api/routes/providers.py  REST endpoints for managing LLM providers. Provi, List all registered LLM providers., Register a new LLM provider., Enable/disable a provider or change its priority., Remove a provider and all its keys/models. (+5 more)

### Community 10 - "Community 10"
Cohesion: 0.33
Nodes (5): downgrade(), add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0, Add the active_session singleton table., Drop the active_session table., upgrade()

### Community 11 - "Community 11"
Cohesion: 0.5
Nodes (3): BaseSettings, friday/config/settings.py  Pydantic Settings for FRIDAY-AGENT.  LLM provider/mod, Settings

### Community 12 - "Community 12"
Cohesion: 0.5
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 0.67
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
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
Nodes (1): Quick check: imports the bot module and calls start_in_background(), then waits

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Return 'anthropic' or 'openai' based on provider name.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Extract the 'type' from a block (dict or object).

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Extract text content from a text block.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Extract an arbitrary attribute from a block (dict or object).

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Ensure content is a list (wraps single blocks).

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (0): 

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Stream one LLM turn.          Args:             messages      : Conversation his

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Convert a unified tool definition to this provider's native schema.          Arg

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): A detailed description of what the tool does and when to use it.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): The JSON schema for the tool's parameters.         Example:         {

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Executes the tool with the given arguments.         Returns a string or JSON-ser

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (0): 

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
Nodes (1): Run migrations in 'offline' mode.      This configures the context with just a U

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Run migrations in 'online' mode.      In this scenario we need to create an Engi

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): A registered LLM provider.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): An API key belonging to a provider. Multiple keys per provider are allowed.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): A known model for a given provider.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): Core intelligence component of the FRIDAY Agent.          This class handles t

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.          Thi

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Processes user input and streams the LLM response token by token.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Processes the input and yields the response token by token.

## Knowledge Gaps
- **62 isolated node(s):** `add_active_session_table  Revision ID: 7b923705ea41 Revises: Create Date: 2026-0`, `Add the active_session singleton table.`, `Drop the active_session table.`, `Startup/shutdown lifecycle — launches the Slack bot alongside the API.`, `Reset the active session to settings defaults (default_provider / default_model)` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (2 nodes): `App.tsx`, `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `OfflineIndicator.tsx`, `handleRetry()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `capture_screenshot()`, `capture_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `ingest_docs.py`, `ingest_directory()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `test_bg_slack.py`, `Quick check: imports the bot module and calls start_in_background(), then waits`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `persona.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Return 'anthropic' or 'openai' based on provider name.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Extract the 'type' from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Extract text content from a text block.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Extract an arbitrary attribute from a block (dict or object).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Ensure content is a list (wraps single blocks).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Stream one LLM turn.          Args:             messages      : Conversation his`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Convert a unified tool definition to this provider's native schema.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `The name of the tool (e.g., 'system_stats'). Must match ^[a-zA-Z0-9_-]{1,64}$ fo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `A detailed description of what the tool does and when to use it.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `The JSON schema for the tool's parameters.         Example:         {`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Executes the tool with the given arguments.         Returns a string or JSON-ser`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `slack_diag.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `install_act.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Run migrations in 'offline' mode.      This configures the context with just a U`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Run migrations in 'online' mode.      In this scenario we need to create an Engi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `A registered LLM provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `An API key belonging to a provider. Multiple keys per provider are allowed.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `A known model for a given provider.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `Core intelligence component of the FRIDAY Agent.          This class handles t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Processes user input and streams the LLM response token by token.          Thi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Retrieves and formats the FRIDAY persona prompt with dynamic context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Processes user input and streams the LLM response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Processes the input and yields the response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMProvider` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 9`?**
  _High betweenness centrality (0.192) - this node is a cross-community bridge._
- **Why does `StreamChunk` connect `Community 2` to `Community 1`, `Community 3`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `APIKey` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `LLMProvider` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`LLMProvider` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 75 inferred relationships involving `APIKey` (e.g. with `Emit SQL to stdout without a live DB connection.` and `Run migrations against the live DB engine.`) actually correct?**
  _`APIKey` has 75 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `ModelCatalog` (e.g. with `friday/api/routes/models_catalog.py  REST endpoints for browsing the model catal` and `List all active models across every registered provider.`) actually correct?**
  _`ModelCatalog` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `StreamChunk` (e.g. with `FridayBrain` and `friday/core/brain.py  FRIDAY's core intelligence — now powered by the Omni-LLM l`) actually correct?**
  _`StreamChunk` has 55 INFERRED edges - model-reasoned connections that need verification._