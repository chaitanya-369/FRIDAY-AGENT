# Graph Report - D:\PROJECTS\FRIDAY-AGENT  (2026-04-22)

## Corpus Check
- 22 files · ~19,677 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 57 nodes · 52 edges · 24 communities detected
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.69)
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

## God Nodes (most connected - your core abstractions)
1. `FridayBrain` - 14 edges
2. `ChatRequest` - 3 edges
3. `test_sliding_window_memory()` - 3 edges
4. `test_system_prompt_formatting()` - 3 edges
5. `run_migrations_offline()` - 2 edges
6. `run_migrations_online()` - 2 edges
7. `chat_endpoint()` - 2 edges
8. `Stream the response from FRIDAY's brain via Server-Sent Events (SSE).` - 2 edges
9. `Settings` - 2 edges
10. `create_db_and_tables()` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Stream the response from FRIDAY's brain via Server-Sent Events (SSE).` --uses--> `FridayBrain`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\api\routes\chat.py → D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py
- `ChatRequest` --uses--> `FridayBrain`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\api\routes\chat.py → D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py
- `FridayBrain` --calls--> `test_sliding_window_memory()`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py → D:\PROJECTS\FRIDAY-AGENT\tests\test_brain.py
- `FridayBrain` --calls--> `test_system_prompt_formatting()`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py → D:\PROJECTS\FRIDAY-AGENT\tests\test_brain.py
- `Stream the response from FRIDAY's brain.` --uses--> `FridayBrain`  [INFERRED]
  D:\PROJECTS\FRIDAY-AGENT\friday\api\routes\chat.py → D:\PROJECTS\FRIDAY-AGENT\friday\core\brain.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.47
Nodes (2): Appends a message to the conversation history, maintaining a sliding window of m, Processes user input and streams the LLM response token by token.

### Community 1 - "Community 1"
Cohesion: 0.4
Nodes (4): Run migrations in 'offline' mode.      This configures the context with just a U, Run migrations in 'online' mode.      In this scenario we need to create an Engi, run_migrations_offline(), run_migrations_online()

### Community 2 - "Community 2"
Cohesion: 0.4
Nodes (4): BaseModel, chat_endpoint(), ChatRequest, Stream the response from FRIDAY's brain via Server-Sent Events (SSE).

### Community 3 - "Community 3"
Cohesion: 0.5
Nodes (3): FridayBrain, Core intelligence component of the FRIDAY Agent.          This class handles t, Stream the response from FRIDAY's brain.

### Community 4 - "Community 4"
Cohesion: 0.5
Nodes (1): create_db_and_tables()

### Community 5 - "Community 5"
Cohesion: 0.67
Nodes (2): BaseSettings, Settings

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (2): test_sliding_window_memory(), test_system_prompt_formatting()

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (1): Retrieves and formats the FRIDAY persona prompt with dynamic context.

### Community 8 - "Community 8"
Cohesion: 0.67
Nodes (0): 

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0): 

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 1.0
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
Nodes (0): 

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
Nodes (1): Processes the input and yields the response token by token.

## Knowledge Gaps
- **8 isolated node(s):** `Run migrations in 'offline' mode.      This configures the context with just a U`, `Run migrations in 'online' mode.      In this scenario we need to create an Engi`, `Core intelligence component of the FRIDAY Agent.          This class handles t`, `Retrieves and formats the FRIDAY persona prompt with dynamic context.`, `Appends a message to the conversation history, maintaining a sliding window of m` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (2 nodes): `server.py`, `status()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (2 nodes): `slack_routes.py`, `slack_events()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (2 nodes): `App.tsx`, `main.tsx`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `capture_screenshot()`, `capture_ui.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `ingest_docs.py`, `ingest_directory()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `notify.py`, `send_notification()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `persona.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `install_act.ps1`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Processes the input and yields the response token by token.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FridayBrain` connect `Community 3` to `Community 0`, `Community 2`, `Community 4`, `Community 6`, `Community 7`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Why does `ChatRequest` connect `Community 2` to `Community 3`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `FridayBrain` (e.g. with `ChatRequest` and `Stream the response from FRIDAY's brain via Server-Sent Events (SSE).`) actually correct?**
  _`FridayBrain` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `test_sliding_window_memory()` (e.g. with `FridayBrain` and `._update_history()`) actually correct?**
  _`test_sliding_window_memory()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `test_system_prompt_formatting()` (e.g. with `FridayBrain` and `._get_system_prompt()`) actually correct?**
  _`test_system_prompt_formatting()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Run migrations in 'offline' mode.      This configures the context with just a U`, `Run migrations in 'online' mode.      In this scenario we need to create an Engi`, `Core intelligence component of the FRIDAY Agent.          This class handles t` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._