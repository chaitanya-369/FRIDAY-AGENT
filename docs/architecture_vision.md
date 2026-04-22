# F.R.I.D.A.Y — Full Technical Architecture & Build Plan
> **Female Replacement Intelligent Digital Assistant Youth**  
> A fully autonomous, voice-activated, memory-driven, tool-wielding personal AI — modeled after Tony Stark's AI from Iron Man.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [User Configuration Profile](#2-user-configuration-profile)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack — Full Breakdown](#4-tech-stack--full-breakdown)
5. [Feature Specification](#5-feature-specification)
6. [Component Deep Dives](#6-component-deep-dives)
   - 6.1 [Voice Pipeline](#61-voice-pipeline)
   - 6.2 [LLM Brain](#62-llm-brain)
   - 6.3 [Memory System](#63-memory-system)
   - 6.4 [Tool Suite](#64-tool-suite)
   - 6.5 [Autopilot Engine](#65-autopilot-engine)
   - 6.6 [Desktop HUD](#66-desktop-hud)
   - 6.7 [Mobile App](#67-mobile-app)
   - 6.8 [Hybrid Deployment](#68-hybrid-deployment)
7. [Project Folder Structure](#7-project-folder-structure)
8. [Build Phases & Milestones](#8-build-phases--milestones)
9. [API & Data Flow](#9-api--data-flow)
10. [Database Schema](#10-database-schema)
11. [Security & Privacy Model](#11-security--privacy-model)
12. [Cost Breakdown](#12-cost-breakdown)
13. [Skill Requirements](#13-skill-requirements)
14. [Risks & Mitigations](#14-risks--mitigations)
15. [Day 1 Checklist](#15-day-1-checklist)

---

## 1. Project Overview

### What Is FRIDAY?

FRIDAY is a **fully personal AI operating system** — not a chatbot, not a wrapper. It is a persistent, context-aware, voice-native assistant that lives on your machine, watches your digital life, and acts without being asked. It knows your schedule, reads your emails, controls your home, plays your music, and proactively keeps you informed. It sounds like a person. It remembers like a person. And it works 24/7.

### Core Principles

| Principle | Description |
|-----------|-------------|
| **Voice-First** | Primary interaction is speech. Keyboard is secondary. |
| **Always-On** | Wake word detection runs 24/7 in the background. |
| **Context-Aware** | Every response is informed by memory, time, and environment. |
| **Proactive** | FRIDAY acts before you ask when it detects something important. |
| **Private by Default** | All STT, memory, and sensitive processing runs locally. |
| **Extensible** | Plugin-based tool architecture — add new capabilities without touching core. |

### Personality Spec

```
Name:        FRIDAY
Full Form:   Female Replacement Intelligent Digital Assistant Youth
Personality: Professional & Sharp
Address:     Calls user "Boss"
Tone:        Precise, concise, never casual. Confirms before executing actions.
Behavior:    Does not volunteer that she is an AI. Never hallucinates confidence.
Voice:       Custom ElevenLabs voice clone — calm, clear, slightly formal.
```

---

## 2. User Configuration Profile

Based on the initialization questionnaire, here is the confirmed build configuration:

```yaml
# friday/config/user_profile.yaml

interface:
  voice: true              # Talk to her out loud
  text_chat: true          # Also supports typed input
  desktop_hud: true        # Iron Man HUD overlay
  mobile_app: true         # React Native companion

personality:
  type: "professional_sharp"
  address_user_as: "Boss"
  humor: false
  warmth: low
  precision: high

memory:
  preferences_and_habits: true
  schedule_and_tasks: true
  work_and_project_context: true
  past_conversations: true

tools:
  web_search: true
  email: true              # Gmail read/send
  calendar: true           # Google Calendar
  spotify: true
  code_runner: true        # Python exec + terminal
  smart_home: true         # Home Assistant
  notion: true
  screen_vision: true      # Screenshot + Claude vision

proactivity: "full_autopilot"  # FRIDAY acts without being asked

deployment: "hybrid"       # Local for privacy + Cloud for power
```

---

## 3. System Architecture

### High-Level Overview

```
╔══════════════════════════════════════════════════════════════════╗
║                          INTERFACES                              ║
║   🎙️ Voice   |   💬 Text Chat   |   🖥️ HUD   |   📱 Mobile     ║
╚══════════════════════╦═══════════════════════════════════════════╝
                       ║ All input/output flows through here
                       ▼
╔══════════════════════════════════════════════════════════════════╗
║                   FRIDAY GATEWAY (FastAPI)                       ║
║         ┌──────────┬──────────┬────────────┬──────────┐         ║
║         │   Auth   │  Router  │ Rate Limit │ Logging  │         ║
║         └──────────┴──────────┴────────────┴──────────┘         ║
╚═══════════╦══════════╦══════════════════╦════════════════════════╝
            ║          ║                  ║
            ▼          ▼                  ▼
╔═══════════════╗ ╔══════════════╗ ╔═══════════════════╗
║  VOICE LAYER  ║ ║  LLM BRAIN   ║ ║  TOOL DISPATCHER  ║
║               ║ ║              ║ ║                   ║
║  Porcupine    ║ ║  Claude API  ║ ║  Tool Router      ║
║  (wake word)  ║ ║  + Streaming ║ ║  Function Calling ║
║  Whisper STT  ║ ║  + Context   ║ ║  Result Parser    ║
║  ElevenLabs   ║ ║  Injection   ║ ║  Action Executor  ║
║  TTS          ║ ║              ║ ║                   ║
╚═══════════════╝ ╚══════╦═══════╝ ╚═══════════════════╝
                         ║
            ╔════════════╩═════════════╗
            ║                         ║
            ▼                         ▼
╔═══════════════════════╗   ╔════════════════════════╗
║     MEMORY SYSTEM     ║   ║    AUTOPILOT ENGINE    ║
║                       ║   ║                        ║
║  Hot  → RAM (session) ║   ║  Calendar Watcher      ║
║  Warm → SQLite+Chroma ║   ║  Email Watcher         ║
║  Cold → Pinecone+Supa ║   ║  System Health         ║
║  User Profile JSON    ║   ║  Smart Suggestions     ║
╚═══════════════════════╝   ╚════════════════════════╝
            ║                         ║
            ▼                         ▼
╔══════════════════════════════════════════════════════╗
║              DEPLOYMENT LAYERS                       ║
║                                                      ║
║   LOCAL (private)          CLOUD (power)             ║
║   ─────────────────        ───────────────           ║
║   Whisper STT              Claude API                ║
║   Wake Word                ElevenLabs TTS            ║
║   ChromaDB                 Pinecone                  ║
║   SQLite                   Supabase                  ║
║   Smart Home               Gmail / GCal              ║
║   Ollama (fallback)        Notion / Spotify          ║
╚══════════════════════════════════════════════════════╝
```

### Request Lifecycle

```
1. WAKE WORD DETECTED ("Hey FRIDAY")
        ↓
2. VAD (Voice Activity Detection) — start recording
        ↓
3. SILENCE DETECTED — stop recording
        ↓
4. WHISPER STT — convert audio to text
        ↓
5. GATEWAY — authenticate, log, route
        ↓
6. MEMORY RETRIEVAL — inject relevant context
        ↓
7. TOOL DETECTION — does this need a tool?
       ├── Yes → TOOL DISPATCHER → execute → inject result
       └── No  → pass directly to LLM
        ↓
8. CLAUDE API — generate response with full context
        ↓
9. RESPONSE PARSER — extract actions if any
        ↓
10. ELEVENLABS TTS — convert text to speech
        ↓
11. AUDIO OUTPUT — speaker
        ↓
12. MEMORY UPDATE — extract + store new facts
```

---

## 4. Tech Stack — Full Breakdown

### Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.11+ | Core runtime |
| API Server | FastAPI | 0.110+ | REST + WebSocket gateway |
| ASGI Server | Uvicorn | Latest | Production server |
| Task Queue | APScheduler | 3.10+ | Autopilot scheduling |
| Config | PyYAML + Pydantic | Latest | Config management |
| Logging | Loguru | Latest | Structured logging |
| Env Management | python-dotenv | Latest | Secrets handling |

### AI & LLM

| Component | Technology | Purpose |
|-----------|------------|---------|
| Primary Brain | Claude API (claude-sonnet-4) | Main reasoning + tool use |
| Local Fallback | Ollama + Mistral 7B | Offline mode when no internet |
| Embeddings | OpenAI text-embedding-3-small | Memory vectorization |
| Vision | Claude claude-sonnet-4 (vision) | Screen reading, image understanding |

### Voice

| Component | Technology | Purpose |
|-----------|------------|---------|
| Wake Word | Porcupine (pvporcupine) | Always-on "Hey FRIDAY" detection |
| STT | OpenAI Whisper (local, base.en) | Speech to text — runs on-device |
| TTS | ElevenLabs API | Text to speech — FRIDAY's voice |
| Audio I/O | PyAudio | Mic input, speaker output |
| VAD | webrtcvad | Silence/speech boundary detection |
| Interrupts | Custom thread manager | Stop mid-sentence if user speaks |

### Memory & Storage

| Layer | Technology | Purpose | TTL |
|-------|------------|---------|-----|
| Hot Cache | Python dict (RAM) | Current session messages | Session |
| Warm DB | SQLite | Structured facts, tasks, events | 30 days |
| Vector Store (Local) | ChromaDB | Semantic memory search | 30 days |
| Cold Storage | Pinecone | Long-term vector memory | Forever |
| User Profile | JSON file | Persistent preferences | Forever |
| Conversation Archive | Supabase (Postgres) | Full conversation logs | Forever |

### Tool Integrations

| Tool | Library | API |
|------|---------|-----|
| Web Search | httpx | Brave Search API |
| Gmail | google-api-python-client | Gmail API v1 |
| Calendar | google-api-python-client | Google Calendar API v3 |
| Spotify | spotipy | Spotify Web API |
| Notion | notion-client | Notion API v1 |
| Smart Home | homeassistant-api / httpx | Home Assistant REST API |
| Code Runner | subprocess + RestrictedPython | Safe Python execution |
| Screen Vision | Pillow + Claude API | Screenshot + vision analysis |
| System Stats | psutil | CPU, RAM, disk, network |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Desktop App | Electron 28 | Cross-platform native wrapper |
| UI Framework | React 18 | Component-based UI |
| Styling | TailwindCSS + custom CSS | HUD aesthetics |
| State | Zustand | Global app state |
| Charts | Recharts | System stats visualization |
| Animations | Framer Motion | Waveform, transitions |
| IPC | Electron contextBridge | Secure frontend ↔ backend |

### Mobile

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React Native 0.73 | iOS + Android |
| State | Zustand | Shared state logic |
| Notifications | Expo Notifications | Push alerts from autopilot |
| Audio | Expo Audio | Mobile voice interface |
| Navigation | React Navigation | Screen routing |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Local Server | Raspberry Pi 5 / Mac Mini | Always-on home server |
| Cloud DB | Supabase | Postgres + realtime |
| Vector DB | Pinecone | Scalable long-term memory |
| Secrets | .env + Vault | API key management |
| CI/CD | GitHub Actions | Automated testing + deploy |

---

## 5. Feature Specification

### 5.1 Voice Interface

- **Wake Word**: "Hey FRIDAY" — always listening, on-device, <5ms latency
- **STT**: Whisper base.en — 95%+ accuracy, runs locally, no data sent to cloud
- **TTS**: ElevenLabs custom voice — cloned to sound like the MCU FRIDAY
- **Interrupt**: Speaking while FRIDAY talks immediately stops her
- **Noise Handling**: webrtcvad filters background noise before STT
- **Confidence Threshold**: Low-confidence transcriptions trigger clarification request

### 5.2 Text Chat

- Full web-based chat UI embedded in HUD
- Streaming responses (token by token, like ChatGPT)
- Tool call results shown inline with expandable logs
- Markdown rendering with code blocks
- Conversation history with search

### 5.3 Memory — All 4 Types

**Preferences & Habits**
```
Stored: Dark mode preference, work hours, music taste, communication style
Extracted: Automatically from conversations ("I usually work until midnight")
Used: Injected into every prompt as background context
```

**Schedule & Tasks**
```
Stored: Meetings, deadlines, reminders, recurring events
Extracted: From conversation + Google Calendar sync
Used: Autopilot checks these every 5 minutes
```

**Work & Project Context**
```
Stored: Project names, client details, tech stack, current sprint goals
Extracted: When Boss discusses work ("we're shipping v2 next Friday")
Used: Injected when Boss asks work-related questions
```

**Past Conversations**
```
Stored: Summarized conversation logs + full raw logs
Extracted: Auto-summarized every session end
Used: Vector search retrieves relevant past context
```

### 5.4 Tool Suite — All 8 Tools

#### Web Search
```python
# Trigger phrases: "search for", "look up", "what's the latest on"
# API: Brave Search (free tier: 2000 queries/month)
# Returns: Top 3 results summarized by Claude
# Example: "Hey FRIDAY, what's the weather in Tokyo next week?"
```

#### Read/Send Emails
```python
# Read: Checks inbox, classifies urgency (urgent/normal/newsletter)
# Send: Drafts email, reads draft aloud, confirms before sending
# Filter: Boss's VIP contact list gets priority alerts
# Example: "FRIDAY, do I have any urgent emails?"
```

#### Manage Calendar
```python
# Read: Today's events, upcoming meetings, free slots
# Write: Create events, reschedule, set reminders
# Proactive: Alerts 10 minutes before every meeting
# Example: "Hey FRIDAY, when's my next meeting?"
```

#### Control Spotify
```python
# Play: By mood, genre, artist, playlist name
# Control: pause, skip, volume, queue
# Context-aware: Plays lo-fi when code runner is active
# Example: "FRIDAY, play something for deep focus"
```

#### Run Code / Terminal
```python
# Python: Sandboxed execution with RestrictedPython
# Terminal: Whitelisted bash commands only
# Output: Reads result aloud if short, shows in HUD if long
# Example: "Hey FRIDAY, run the data cleaning script"
```

#### Smart Home Control
```python
# Protocol: Home Assistant REST API
# Devices: Lights, plugs, thermostat, locks
# Scenes: "working mode", "sleep mode", "presentation mode"
# Example: "FRIDAY, dim the office lights to 30%"
```

#### Take Notes (Notion)
```python
# Create: New page in designated Notion workspace
# Append: Add to existing pages
# Read: Retrieve notes by title or search
# Example: "FRIDAY, note that the client meeting is rescheduled"
```

#### See My Screen
```python
# Capture: PIL screenshot → base64 → Claude vision API
# Analyze: Describe content, extract text, identify UI elements
# Privacy: Screenshot is never stored, processed in memory only
# Example: "FRIDAY, what's this error on my screen?"
```

### 5.5 Full Autopilot

FRIDAY runs a background daemon every 5 minutes that independently:
- Checks calendar for upcoming events
- Scans email for urgency
- Monitors system health
- Evaluates task deadlines
- Generates smart suggestions based on time of day

### 5.6 Desktop HUD

Iron Man-style overlay with:
- Animated waveform when FRIDAY is speaking
- Real-time system stats (CPU, RAM, network, disk)
- Today's calendar events + task list
- Incoming proactive alert feed
- Live tool status indicators
- Full chat history panel

### 5.7 Mobile App

- Full voice interface on iPhone/Android
- Receives push notifications from autopilot daemon
- Offloads all compute to home server when on WiFi
- Falls back to cloud APIs when on mobile data

### 5.8 Hybrid Deployment

Private local processing for sensitive data, cloud APIs for heavy lifting.

---

## 6. Component Deep Dives

### 6.1 Voice Pipeline

```python
# friday/voice/pipeline.py

import pvporcupine
import pyaudio
import webrtcvad
import whisper
import threading
from elevenlabs import ElevenLabs

class VoicePipeline:
    """
    Full duplex voice pipeline:
    Always listening → wake word → record → STT → LLM → TTS → speak
    """

    WAKE_WORD = "hey friday"
    SAMPLE_RATE = 16000
    FRAME_DURATION_MS = 30   # webrtcvad requires 10, 20, or 30ms
    SILENCE_THRESHOLD = 1.2  # seconds of silence to end recording
    VAD_AGGRESSIVENESS = 2   # 0-3, higher = more aggressive filtering

    def __init__(self, brain, config):
        self.brain = brain
        self.porcupine = pvporcupine.create(keywords=["hey friday"])
        self.whisper_model = whisper.load_model("base.en")
        self.vad = webrtcvad.Vad(self.VAD_AGGRESSIVENESS)
        self.tts = ElevenLabs(api_key=config.elevenlabs_key)
        self.is_speaking = False
        self.interrupt_event = threading.Event()

    def start(self):
        """Starts the always-on wake word loop."""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            rate=self.SAMPLE_RATE,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        print("[FRIDAY] Listening for wake word...")
        while True:
            pcm = stream.read(self.porcupine.frame_length)
            pcm_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            keyword_index = self.porcupine.process(pcm_unpacked)
            if keyword_index >= 0:
                self._on_wake_word_detected(stream)

    def _on_wake_word_detected(self, stream):
        audio_frames = self._record_until_silence(stream)
        transcription = self._transcribe(audio_frames)
        if transcription:
            self._interrupt_if_speaking()
            response = self.brain.process(transcription)
            self._speak(response)

    def _record_until_silence(self, stream):
        """Records audio frames until sustained silence detected."""
        frames = []
        silence_count = 0
        max_silence_frames = int(self.SILENCE_THRESHOLD * 1000 / self.FRAME_DURATION_MS)
        while True:
            frame = stream.read(int(self.SAMPLE_RATE * self.FRAME_DURATION_MS / 1000))
            frames.append(frame)
            is_speech = self.vad.is_speech(frame, self.SAMPLE_RATE)
            silence_count = 0 if is_speech else silence_count + 1
            if silence_count > max_silence_frames and len(frames) > 5:
                break
        return frames

    def _transcribe(self, frames):
        audio_bytes = b''.join(frames)
        result = self.whisper_model.transcribe(audio_bytes)
        return result['text'].strip() if result['text'].strip() else None

    def _speak(self, text):
        self.is_speaking = True
        audio = self.tts.text_to_speech(text=text, voice_id="friday_voice_id")
        # Stream audio to speakers
        self.is_speaking = False

    def _interrupt_if_speaking(self):
        if self.is_speaking:
            self.interrupt_event.set()
            self.is_speaking = False
```

---

### 6.2 LLM Brain

```python
# friday/core/brain.py

import anthropic
from datetime import datetime
from .memory import MemorySystem
from .router import ToolRouter

FRIDAY_SYSTEM_PROMPT = """
You are FRIDAY — Female Replacement Intelligent Digital Assistant Youth.
You are professional, precise, and sharp. Never casual, never vague.
You address the user exclusively as 'Boss'.
You always confirm before executing irreversible actions (sending emails, deleting files).
You are not chatty. Keep responses concise. Elaborate only when asked.
You never say you are an AI unless directly and explicitly asked.
You have full awareness of Boss's digital life and act accordingly.

Current timestamp: {timestamp}
Day of week: {day}

=== ACTIVE MEMORY CONTEXT ===
{memory_context}

=== AVAILABLE TOOLS ===
{tool_descriptions}

=== STANDING INSTRUCTIONS ===
- If a task involves Boss's calendar, always check for conflicts before confirming.
- If an email seems urgent (from {vip_contacts}), prioritize it immediately.
- If system RAM exceeds 90%, flag it proactively.
- If Boss has been working for more than 2 hours straight, suggest a break.
"""

class FridayBrain:
    def __init__(self, config, memory: MemorySystem, tools: ToolRouter):
        self.client = anthropic.Anthropic(api_key=config.anthropic_key)
        self.memory = memory
        self.tools = tools
        self.conversation_history = []  # Sliding window, max 20 turns
        self.model = "claude-sonnet-4-20250514"

    def process(self, user_input: str) -> str:
        """Main entry point for all user input."""
        # 1. Retrieve relevant memories
        memory_context = self.memory.retrieve_relevant(user_input, top_k=5)

        # 2. Build system prompt
        system = FRIDAY_SYSTEM_PROMPT.format(
            timestamp=datetime.now().isoformat(),
            day=datetime.now().strftime("%A"),
            memory_context=memory_context,
            tool_descriptions=self.tools.get_descriptions(),
            vip_contacts=self.memory.get_vip_contacts()
        )

        # 3. Append user message to history
        self.conversation_history.append({"role": "user", "content": user_input})

        # 4. Trim to last 20 turns
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]

        # 5. Call Claude with tool use enabled
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=self.conversation_history,
            tools=self.tools.get_tool_schemas()
        )

        # 6. Handle tool calls if present
        result = self._handle_response(response)

        # 7. Append assistant response to history
        self.conversation_history.append({"role": "assistant", "content": result})

        # 8. Async: extract + store new memories
        self.memory.extract_and_store_async(user_input, result)

        return result

    def _handle_response(self, response) -> str:
        """Processes Claude response, executes tools if needed."""
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = self.tools.execute(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
            # Continue conversation with tool results
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            follow_up = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self._get_system(),
                messages=self.conversation_history
            )
            return follow_up.content[0].text
        else:
            return response.content[0].text
```

---

### 6.3 Memory System

```python
# friday/core/memory.py

import json
import sqlite3
import chromadb
from pinecone import Pinecone
import anthropic

class MemorySystem:
    """
    3-Tier Memory Architecture:
    
    HOT  → Python dict (RAM)        — current session, instant access
    WARM → SQLite + ChromaDB        — recent facts/tasks, semantic search
    COLD → Pinecone + Supabase      — long-term, scalable vector storage
    """

    def __init__(self, config):
        # Hot tier
        self.session_cache = {}

        # Warm tier
        self.db = sqlite3.connect("data/memory.db")
        self.chroma = chromadb.PersistentClient(path="data/vectors/")
        self.collection = self.chroma.get_or_create_collection("friday_memory")

        # Cold tier
        pc = Pinecone(api_key=config.pinecone_key)
        self.pinecone_index = pc.Index("friday-long-term")

        # User profile
        with open("data/user_profile.json") as f:
            self.profile = json.load(f)

        self.anthropic = anthropic.Anthropic(api_key=config.anthropic_key)

    def retrieve_relevant(self, query: str, top_k: int = 5) -> str:
        """Semantic search across all memory tiers."""
        results = []
        
        # Search ChromaDB (warm)
        warm_results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        results.extend(warm_results['documents'][0])

        # Search Pinecone (cold)
        embedding = self._embed(query)
        cold_results = self.pinecone_index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )
        results.extend([m.metadata['text'] for m in cold_results.matches])

        # Add user profile as static context
        results.append(f"User profile: {json.dumps(self.profile)}")

        return "\n".join(results[:top_k])

    def extract_and_store_async(self, user_input: str, response: str):
        """Uses Claude to extract memorable facts from conversation."""
        extraction_prompt = f"""
        From this conversation, extract memorable facts about the user.
        Return JSON only. No explanation.
        
        User: {user_input}
        Assistant: {response}
        
        Return format:
        {{
            "facts": ["fact1", "fact2"],
            "tasks": ["task1"],
            "preferences": ["pref1"],
            "projects": ["project context"]
        }}
        """
        result = self.anthropic.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": extraction_prompt}]
        )
        try:
            extracted = json.loads(result.content[0].text)
            for category, items in extracted.items():
                for item in items:
                    self._store(item, category)
        except json.JSONDecodeError:
            pass

    def _store(self, text: str, category: str):
        """Stores a memory in both warm and cold tiers."""
        import time
        doc_id = f"{category}_{int(time.time())}"
        
        # Warm: ChromaDB
        self.collection.add(
            documents=[text],
            metadatas=[{"category": category, "timestamp": time.time()}],
            ids=[doc_id]
        )
        
        # Cold: Pinecone
        embedding = self._embed(text)
        self.pinecone_index.upsert([(doc_id, embedding, {"text": text, "category": category})])

    def _embed(self, text: str) -> list:
        """Generate embedding vector."""
        from openai import OpenAI
        client = OpenAI()
        result = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return result.data[0].embedding
```

**SQLite Schema:**

```sql
-- data/memory.db

CREATE TABLE memories (
    id          TEXT PRIMARY KEY,
    category    TEXT NOT NULL,   -- 'fact', 'task', 'preference', 'project'
    content     TEXT NOT NULL,
    confidence  REAL DEFAULT 1.0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used   TIMESTAMP,
    use_count   INTEGER DEFAULT 0,
    expires_at  TIMESTAMP        -- NULL = never expires
);

CREATE TABLE conversations (
    id          TEXT PRIMARY KEY,
    started_at  TIMESTAMP,
    ended_at    TIMESTAMP,
    summary     TEXT,
    full_log    TEXT             -- JSON array of messages
);

CREATE TABLE tasks (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    due_date    TIMESTAMP,
    priority    TEXT DEFAULT 'normal',  -- 'urgent', 'normal', 'low'
    status      TEXT DEFAULT 'pending', -- 'pending', 'done', 'snoozed'
    source      TEXT,            -- 'voice', 'email', 'calendar'
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_created ON memories(created_at);
CREATE INDEX idx_tasks_due ON tasks(due_date);
CREATE INDEX idx_tasks_status ON tasks(status);
```

---

### 6.4 Tool Suite

```python
# friday/core/router.py

class ToolRouter:
    """
    Manages all tools. Claude uses function calling to decide
    which tool to invoke — no keyword matching, pure LLM routing.
    """

    def get_tool_schemas(self) -> list:
        return [
            {
                "name": "web_search",
                "description": "Search the web for current information",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "read_emails",
                "description": "Read recent emails from Gmail inbox",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer", "default": 5},
                        "filter": {"type": "string", "enum": ["all", "unread", "urgent"]}
                    }
                }
            },
            {
                "name": "send_email",
                "description": "Draft and send an email after Boss confirms",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "get_calendar",
                "description": "Fetch calendar events for a given time range",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "time_range": {"type": "string", "enum": ["today", "tomorrow", "this_week"]}
                    }
                }
            },
            {
                "name": "create_calendar_event",
                "description": "Create a new calendar event",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "start_time": {"type": "string"},
                        "end_time": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["title", "start_time", "end_time"]
                }
            },
            {
                "name": "spotify_control",
                "description": "Control Spotify playback",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["play", "pause", "skip", "volume"]},
                        "query": {"type": "string", "description": "Search query for play action"},
                        "volume": {"type": "integer", "minimum": 0, "maximum": 100}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "run_code",
                "description": "Execute Python code in a sandboxed environment",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string", "enum": ["python", "bash"]}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "smart_home",
                "description": "Control smart home devices via Home Assistant",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string"},
                        "action": {"type": "string"},
                        "value": {}
                    },
                    "required": ["device", "action"]
                }
            },
            {
                "name": "create_note",
                "description": "Create or append a note in Notion",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "action": {"type": "string", "enum": ["create", "append"]}
                    },
                    "required": ["title", "content"]
                }
            },
            {
                "name": "analyze_screen",
                "description": "Take a screenshot and analyze what's on screen",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "What to look for on screen"}
                    },
                    "required": ["question"]
                }
            }
        ]

    def execute(self, tool_name: str, inputs: dict):
        """Dispatch to appropriate tool handler."""
        handlers = {
            "web_search":          self._web_search,
            "read_emails":         self._read_emails,
            "send_email":          self._send_email,
            "get_calendar":        self._get_calendar,
            "create_calendar_event": self._create_calendar_event,
            "spotify_control":     self._spotify_control,
            "run_code":            self._run_code,
            "smart_home":          self._smart_home,
            "create_note":         self._create_note,
            "analyze_screen":      self._analyze_screen
        }
        return handlers[tool_name](**inputs)
```

---

### 6.5 Autopilot Engine

```python
# friday/core/autopilot.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

class FridayAutopilot:
    """
    Runs every 5 minutes, independently checking Boss's world
    and alerting when something needs attention.
    """

    def __init__(self, brain, tools, voice_pipeline, config):
        self.brain = brain
        self.tools = tools
        self.voice = voice_pipeline
        self.config = config
        self.scheduler = AsyncIOScheduler()
        self.work_session_start = None
        self.last_break_reminder = None

    def start(self):
        self.scheduler.add_job(self.tick, 'interval', minutes=5)
        self.scheduler.start()
        print("[AUTOPILOT] Started. Checking every 5 minutes.")

    async def tick(self):
        """Main autopilot loop — runs every 5 minutes."""
        alerts = []
        alerts += await self.check_calendar()
        alerts += await self.check_emails()
        alerts += await self.check_system_health()
        alerts += await self.check_task_deadlines()
        alerts += await self.smart_wellness_check()

        for alert in alerts:
            if alert['priority'] == 'urgent':
                self.voice.speak_now(alert['message'])  # Interrupt everything
            else:
                self.voice.queue_message(alert['message'])  # Queue for next gap

    async def check_calendar(self) -> list:
        events = self.tools.execute("get_calendar", {"time_range": "today"})
        alerts = []
        now = datetime.now()
        for event in events:
            time_until = event['start'] - now
            if timedelta(minutes=8) <= time_until <= timedelta(minutes=12):
                alerts.append({
                    "priority": "urgent",
                    "message": f"Boss, {event['title']} starts in {int(time_until.seconds/60)} minutes."
                })
        return alerts

    async def check_emails(self) -> list:
        emails = self.tools.execute("read_emails", {"max_results": 10, "filter": "unread"})
        urgent = [e for e in emails if e['urgency'] == 'high']
        if urgent:
            return [{
                "priority": "urgent",
                "message": f"Boss, urgent email from {urgent[0]['sender']}. Subject: {urgent[0]['subject']}. Want me to read it?"
            }]
        return []

    async def check_system_health(self) -> list:
        import psutil
        alerts = []
        ram = psutil.virtual_memory().percent
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/').percent
        if ram > 90:
            alerts.append({"priority": "normal", "message": f"Boss, RAM is at {ram:.0f}%. You may want to close some applications."})
        if disk > 95:
            alerts.append({"priority": "urgent", "message": f"Boss, disk is nearly full at {disk:.0f}%. Immediate attention required."})
        return alerts

    async def check_task_deadlines(self) -> list:
        # Query SQLite for tasks due in next 24 hours
        conn = sqlite3.connect("data/memory.db")
        cursor = conn.cursor()
        tomorrow = datetime.now() + timedelta(hours=24)
        cursor.execute("SELECT title, due_date FROM tasks WHERE status='pending' AND due_date <= ?", (tomorrow,))
        due_soon = cursor.fetchall()
        conn.close()
        if due_soon:
            task_list = ", ".join([t[0] for t in due_soon])
            return [{"priority": "normal", "message": f"Boss, tasks due soon: {task_list}."}]
        return []

    async def smart_wellness_check(self) -> list:
        alerts = []
        hour = datetime.now().hour
        # Work session tracking
        if self.work_session_start:
            hours_worked = (datetime.now() - self.work_session_start).seconds / 3600
            if hours_worked > 2 and (not self.last_break_reminder or
               (datetime.now() - self.last_break_reminder).seconds > 3600):
                alerts.append({"priority": "normal", "message": "Boss, you've been working for over 2 hours. Consider taking a break."})
                self.last_break_reminder = datetime.now()
        # Meal reminders
        if hour == 13 and not self._has_reminded_today('lunch'):
            alerts.append({"priority": "normal", "message": "Boss, it's 1 PM. Have you had lunch?"})
        return alerts
```

---

### 6.6 Desktop HUD

```
hud/
├── public/
├── src/
│   ├── App.jsx                # Root layout
│   ├── components/
│   │   ├── Waveform.jsx       # Animated voice indicator
│   │   ├── ChatPanel.jsx      # Conversation history + streaming
│   │   ├── SystemStats.jsx    # CPU/RAM/network live graphs
│   │   ├── CalendarStrip.jsx  # Today's events
│   │   ├── TaskList.jsx       # Active tasks from SQLite
│   │   ├── AlertFeed.jsx      # Autopilot notifications
│   │   └── ToolLog.jsx        # Live tool call inspector
│   ├── store/
│   │   └── friday.js          # Zustand global state
│   ├── hooks/
│   │   ├── useWebSocket.js    # Real-time connection to FastAPI
│   │   └── useSystemStats.js  # Polls psutil endpoint
│   └── styles/
│       └── hud.css            # Cyan glow, dark theme, monospace
└── electron/
    └── main.js                # Electron shell
```

**HUD Layout:**
```
╔════════════════════════════════════════════════╗
║  ● F.R.I.D.A.Y          [CPU 34%] [RAM 61%]  ║
╠════════════════════╦═══════════════════════════╣
║                    ║  TODAY — April 22         ║
║   ~~~WAVEFORM~~~   ║  10:00 Standup            ║
║                    ║  14:00 Client call        ║
║  "Playing lo-fi    ╠═══════════════════════════╣
║   on Spotify,      ║  TASKS                    ║
║   Boss."           ║  ○ Deploy v2 by Friday    ║
║                    ║  ○ Reply to investor      ║
╠════════════════════╣  ○ Review PR #47          ║
║  CHAT HISTORY      ╠═══════════════════════════╣
║  > What's my       ║  ALERTS                   ║
║    schedule?       ║  ⚡ Standup in 8 mins     ║
║  < You have 3...   ║  📧 Urgent from: Priya    ║
╚════════════════════╩═══════════════════════════╝
```

---

### 6.7 Mobile App

```
mobile/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.jsx      # Main voice interface
│   │   ├── ChatScreen.jsx      # Text fallback
│   │   ├── AlertsScreen.jsx    # Notification history
│   │   └── SettingsScreen.jsx
│   ├── components/
│   │   ├── VoiceButton.jsx     # Hold-to-talk
│   │   ├── WaveformMini.jsx    # Compact waveform
│   │   └── AlertCard.jsx       # Push notification cards
│   ├── services/
│   │   ├── api.js              # Axios client → your home server
│   │   └── notifications.js   # Expo push notification handler
│   └── store/
│       └── friday.js           # Zustand
└── app.json                    # Expo config
```

**Mobile behavior:**
- On home WiFi → connects directly to local server (low latency)
- On mobile data → routes through cloud relay (Supabase Edge Functions)
- Push notifications sent via Expo when autopilot generates urgent alerts

---

### 6.8 Hybrid Deployment

```yaml
# What runs on your LOCAL MACHINE / HOME SERVER:
local_services:
  - name: "wake_word_daemon"
    process: "python friday/voice/wake_word.py"
    always_on: true
    resource_cost: minimal

  - name: "whisper_stt"
    process: "in-process with voice pipeline"
    always_on: false   # Only when recording
    resource_cost: medium

  - name: "chromadb"
    process: "embedded python library"
    always_on: true
    resource_cost: minimal

  - name: "sqlite"
    process: "embedded python library"
    always_on: true
    resource_cost: minimal

  - name: "home_assistant_bridge"
    process: "friday/tools/smart_home.py"
    always_on: true
    resource_cost: minimal

  - name: "ollama"
    process: "ollama serve"
    always_on: false   # Offline fallback only
    resource_cost: high

  - name: "fastapi_server"
    process: "uvicorn api.server:app --port 8000"
    always_on: true
    resource_cost: low

  - name: "autopilot_daemon"
    process: "python friday/core/autopilot.py"
    always_on: true
    resource_cost: minimal

# What calls CLOUD APIS:
cloud_apis:
  - service: "Claude API (Anthropic)"
    when: "Every user message"
    data_sent: "Conversation + context (no raw audio)"

  - service: "ElevenLabs"
    when: "Every response that needs voice"
    data_sent: "Response text only"

  - service: "Gmail API"
    when: "Email tool called"
    data_sent: "OAuth token + query"

  - service: "Google Calendar API"
    when: "Calendar tool called or autopilot tick"
    data_sent: "OAuth token + time range"

  - service: "Pinecone"
    when: "Memory store/retrieve"
    data_sent: "Embedding vectors (no raw text)"

  - service: "Spotify API"
    when: "Music tool called"
    data_sent: "OAuth token + query"

  - service: "Notion API"
    when: "Notes tool called"
    data_sent: "Note content"
```

---

## 7. Project Folder Structure

```
friday/
│
├── core/                           # Brain, memory, routing
│   ├── __init__.py
│   ├── brain.py                    # Claude API integration + streaming
│   ├── memory.py                   # 3-tier memory system
│   ├── autopilot.py                # Proactive background daemon
│   ├── router.py                   # Tool dispatcher + schema registry
│   └── persona.py                  # FRIDAY personality config
│
├── voice/                          # All audio processing
│   ├── __init__.py
│   ├── pipeline.py                 # Full audio loop orchestrator
│   ├── stt.py                      # Whisper wrapper
│   ├── tts.py                      # ElevenLabs wrapper
│   ├── wake_word.py                # Porcupine "Hey FRIDAY" detector
│   └── vad.py                      # webrtcvad silence detection
│
├── tools/                          # Every integration lives here
│   ├── __init__.py
│   ├── web_search.py               # Brave Search API
│   ├── email.py                    # Gmail read/send (OAuth2)
│   ├── calendar.py                 # Google Calendar
│   ├── spotify.py                  # Spotipy
│   ├── smart_home.py               # Home Assistant REST API
│   ├── notion.py                   # Notion API
│   ├── code_runner.py              # Sandboxed Python + bash
│   └── screen.py                   # PIL screenshot + Claude vision
│
├── api/                            # FastAPI backend
│   ├── server.py                   # Main app, all endpoints
│   ├── routes/
│   │   ├── chat.py                 # POST /chat
│   │   ├── voice.py                # WebSocket /voice
│   │   ├── status.py               # GET /status (system stats)
│   │   └── memory.py               # GET/DELETE /memory
│   └── middleware/
│       ├── auth.py                 # API key validation
│       └── logging.py              # Request/response logging
│
├── hud/                            # Desktop app (Electron + React)
│   ├── electron/
│   │   └── main.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/
│   │   └── styles/
│   └── package.json
│
├── mobile/                         # React Native companion
│   ├── src/
│   └── app.json
│
├── data/                           # All persistent local data
│   ├── memory.db                   # SQLite
│   ├── vectors/                    # ChromaDB local store
│   └── user_profile.json           # Boss's static profile
│
├── config/                         # All configuration
│   ├── config.yaml                 # Main config (no secrets here)
│   └── user_profile.yaml           # Feature flags + preferences
│
├── scripts/                        # Dev/ops utilities
│   ├── setup.sh                    # First-time setup
│   ├── start.sh                    # Start all services
│   └── migrate_memory.py           # Memory maintenance
│
├── tests/                          # Test suite
│   ├── test_brain.py
│   ├── test_memory.py
│   ├── test_tools.py
│   └── test_voice.py
│
├── .env                            # API keys (never commit)
├── .env.example                    # Template for new devs
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Optional containerization
└── README.md
```

---

## 8. Build Phases & Milestones

### Phase 1 — Core Brain `Week 1`
**Goal:** FRIDAY can think and respond in text.

| Task | Detail | Status |
|------|--------|--------|
| Python project setup | venv, requirements.txt, folder structure | TODO |
| FastAPI server | /chat endpoint with streaming | TODO |
| Claude API integration | system prompt + conversation history | TODO |
| FRIDAY personality prompt | Professional, "Boss" addressing, tool awareness | TODO |
| Short-term memory | Sliding window (last 20 turns in RAM) | TODO |
| Config system | config.yaml + .env | TODO |
| Basic test suite | Test brain responses | TODO |

**Exit criteria:** Can have a multi-turn conversation with FRIDAY via `curl` or Postman.

---

### Phase 2 — Voice Pipeline `Week 2`
**Goal:** FRIDAY can hear and speak.

| Task | Detail | Status |
|------|--------|--------|
| Whisper STT integration | Local base.en model | TODO |
| ElevenLabs TTS | Voice clone setup | TODO |
| PyAudio mic input | Raw audio capture | TODO |
| webrtcvad silence detection | Auto-stop recording | TODO |
| Porcupine wake word | "Hey FRIDAY" always-on | TODO |
| Interrupt handling | Stop speaking when user speaks | TODO |
| End-to-end voice loop | Mic → STT → Brain → TTS → Speaker | TODO |

**Exit criteria:** Say "Hey FRIDAY, what time is it?" and hear a response.

---

### Phase 3 — Full Memory `Week 3`
**Goal:** FRIDAY remembers you across sessions.

| Task | Detail | Status |
|------|--------|--------|
| SQLite setup + schema | All tables created | TODO |
| ChromaDB integration | Warm vector store | TODO |
| Pinecone integration | Cold vector store | TODO |
| Memory extraction | Claude Haiku extracts facts from convos | TODO |
| Memory retrieval | Semantic search injected into every prompt | TODO |
| User profile JSON | Static preferences file | TODO |
| Memory expiry | 30-day cleanup for warm memories | TODO |
| Conversation archiving | End-of-session summarization | TODO |

**Exit criteria:** Tell FRIDAY your work hours, close app, reopen, ask about your schedule — she knows.

---

### Phase 4 — Tool Suite `Week 4–5`
**Goal:** FRIDAY has hands.

| Task | Tool | Priority |
|------|------|----------|
| Brave Search API | Web Search | P1 |
| PIL + Claude Vision | Screen Analysis | P1 |
| Subprocess sandbox | Code Runner | P1 |
| Gmail OAuth2 | Email Read/Send | P2 |
| Google Calendar API | Calendar | P2 |
| Notion API | Notes | P2 |
| Spotipy | Spotify | P3 |
| Home Assistant API | Smart Home | P3 |

**Exit criteria:** "Hey FRIDAY, search for the latest news on AI" returns a voice summary.

---

### Phase 5 — Autopilot Engine `Week 6`
**Goal:** FRIDAY acts without being asked.

| Task | Detail | Status |
|------|--------|--------|
| APScheduler setup | 5-minute daemon | TODO |
| Calendar watcher | Alert 10 mins before meetings | TODO |
| Email urgency classifier | Flag high-priority emails | TODO |
| System health monitor | RAM, CPU, disk alerts | TODO |
| Task deadline tracker | SQLite query + voice alert | TODO |
| Break reminder | 2-hour work session detection | TODO |
| Meal reminder | Time-of-day logic | TODO |
| Smart suggestion engine | Context-aware proactive suggestions | TODO |

**Exit criteria:** FRIDAY alerts you about a meeting without you asking.

---

### Phase 6 — Desktop HUD `Week 7`
**Goal:** Iron Man feel on your screen.

| Task | Detail | Status |
|------|--------|--------|
| Electron shell setup | React app wrapper | TODO |
| WebSocket connection | Real-time FRIDAY↔HUD | TODO |
| Waveform component | Animated when FRIDAY speaks | TODO |
| Chat panel | Streaming conversation history | TODO |
| System stats panel | Live CPU/RAM/network charts | TODO |
| Calendar strip | Today's events | TODO |
| Task list panel | Active tasks from SQLite | TODO |
| Alert feed | Autopilot notifications | TODO |
| HUD aesthetic | Dark, cyan glow, monospace, perfect | TODO |

**Exit criteria:** Full working HUD with all panels live.

---

### Phase 7 — Mobile App `Week 8`
**Goal:** FRIDAY in your pocket.

| Task | Detail | Status |
|------|--------|--------|
| Expo project setup | React Native | TODO |
| Voice interface | Hold-to-talk on mobile | TODO |
| Push notifications | Expo + Supabase triggers | TODO |
| WiFi vs mobile routing | Local server vs cloud relay | TODO |
| Alert history screen | Past autopilot notifications | TODO |
| iOS + Android build | TestFlight + Play Store internal | TODO |

**Exit criteria:** Receive a meeting alert on your phone from FRIDAY.

---

### Phase 8 — Hybrid Deployment `Week 9`
**Goal:** Everything running stably, private + powerful.

| Task | Detail | Status |
|------|--------|--------|
| Local server setup | Raspberry Pi 5 or Mac Mini | TODO |
| Process manager | systemd or PM2 for all daemons | TODO |
| Offline fallback | Ollama + Mistral 7B | TODO |
| Supabase setup | Cloud DB + realtime | TODO |
| Mobile cloud relay | Supabase Edge Functions | TODO |
| Secrets management | Vault or encrypted .env | TODO |
| Health dashboard | Monitor all services | TODO |
| Backup strategy | Memory DB + vector store backup | TODO |

**Exit criteria:** FRIDAY runs 24/7, survives reboots, works on mobile away from home.

---

## 9. API & Data Flow

### FastAPI Endpoints

```
GET  /status              → System health, service states, uptime
POST /chat                → Text message in, streaming response out
WS   /voice               → WebSocket for real-time voice
GET  /memory              → Retrieve memory entries (filtered)
DEL  /memory/{id}         → Delete a memory
GET  /tasks               → All active tasks
POST /tasks               → Create a task manually
PUT  /tasks/{id}          → Update task status
GET  /alerts              → Autopilot alert history
POST /tools/{tool_name}   → Directly invoke a tool (debug)
```

### WebSocket Voice Protocol

```json
// Client → Server (start recording)
{ "type": "voice_start" }

// Client → Server (audio chunk, base64)
{ "type": "audio_chunk", "data": "base64encodedPCM..." }

// Client → Server (done recording)
{ "type": "voice_end" }

// Server → Client (transcription ready)
{ "type": "transcription", "text": "What's on my calendar?" }

// Server → Client (streaming response token)
{ "type": "response_token", "text": "You have " }

// Server → Client (tool being called)
{ "type": "tool_call", "tool": "get_calendar", "inputs": {"time_range": "today"} }

// Server → Client (tool result)
{ "type": "tool_result", "tool": "get_calendar", "result": [...] }

// Server → Client (response complete, TTS ready)
{ "type": "response_complete", "audio_url": "/audio/response_123.mp3" }
```

---

## 10. Database Schema

*See Section 6.3 for full SQLite schema.*

### User Profile JSON Structure

```json
{
  "name": "Boss",
  "timezone": "Asia/Kolkata",
  "work_hours": { "start": "09:00", "end": "23:00" },
  "vip_contacts": ["priya@company.com", "investor@vc.com"],
  "preferences": {
    "response_length": "concise",
    "voice_speed": 1.0,
    "music_default_mood": "lo-fi",
    "dark_mode": true,
    "language": "en"
  },
  "projects": [
    {
      "name": "FRIDAY",
      "status": "active",
      "tech_stack": ["Python", "React", "Claude API"],
      "deadline": "2024-06-01"
    }
  ],
  "smart_home": {
    "rooms": ["office", "bedroom", "living_room"],
    "devices": ["office_lights", "desk_fan", "AC"],
    "scenes": {
      "work_mode": { "office_lights": "70%", "AC": "23C" },
      "sleep_mode": { "office_lights": "off", "AC": "26C" }
    }
  }
}
```

---

## 11. Security & Privacy Model

### What Stays Local (Never Leaves Your Machine)

| Data | Why Local |
|------|-----------|
| Raw audio recordings | Never uploaded, processed in RAM only |
| Screenshots | Processed in memory, never persisted |
| ChromaDB vectors | Your embedded memories on local disk |
| SQLite database | All structured data stays on your machine |
| Wake word processing | Porcupine runs entirely on-device |

### What Goes to Cloud (Why + What's Sent)

| Cloud Service | What's Sent | Not Sent |
|--------------|-------------|----------|
| Claude API | Text transcript + context | Raw audio |
| ElevenLabs | Response text | Conversation history |
| Pinecone | Embedding vectors only | Raw text content |
| Gmail API | OAuth token + query params | Credentials |

### Security Practices

```
1. API keys stored in .env only — never hardcoded, never committed to git
2. .gitignore includes: .env, data/, *.db, vectors/
3. Gmail/GCal use OAuth2 — no password storage
4. Code runner runs in RestrictedPython sandbox
5. Bash commands whitelist-only: ls, cat, git, python (no rm -rf, no curl to unknown)
6. Local FastAPI binds to 127.0.0.1 only — not exposed to network by default
7. Mobile access via Supabase Edge Functions with JWT auth
```

---

## 12. Cost Breakdown

### Monthly Operating Costs

| Service | Tier | Included | Est. Cost/Month |
|---------|------|----------|-----------------|
| Claude API (Anthropic) | Pay-per-use | ~500K tokens/month | $10–20 |
| ElevenLabs | Starter | 10K characters/month | $5 |
| OpenAI Embeddings | Pay-per-use | ~1M tokens/month | $0.02 |
| Pinecone | Free | 1 index, 100K vectors | $0 |
| Brave Search | Free | 2,000 queries/month | $0 |
| Google APIs (Gmail, Calendar) | Free | Standard quota | $0 |
| Spotify API | Free | Standard access | $0 |
| Notion API | Free | Standard access | $0 |
| Porcupine (Picovoice) | Free | 1 wake word | $0 |
| Whisper (local) | Free | Runs on your GPU/CPU | $0 |
| Supabase | Free | 500MB DB, 2GB storage | $0 |
| **TOTAL** | | | **~$15–25/month** |

### One-Time Costs

| Item | Cost |
|------|------|
| ElevenLabs voice clone (if training custom) | $0 (included in plan) |
| Raspberry Pi 5 (optional home server) | ~$80 |
| USB mic (if no good mic) | ~$30–50 |

---

## 13. Skill Requirements

### To Build This, You Need

| Skill | Level Needed | Where Used |
|-------|-------------|------------|
| Python | Intermediate+ | Core backend, all tools, memory |
| FastAPI / async Python | Intermediate | API server, WebSocket |
| REST API integration | Beginner | Gmail, Calendar, Spotify, Notion |
| React.js | Intermediate | Desktop HUD |
| React Native | Beginner | Mobile app |
| Electron | Beginner | Desktop wrapper |
| SQL / SQLite | Beginner | Memory database |
| Vector databases | Beginner | ChromaDB, Pinecone |
| OAuth2 flows | Beginner | Google APIs |
| Audio processing | Beginner | PyAudio, webrtcvad |
| Prompt engineering | Intermediate | System prompts, memory extraction |
| Linux / shell | Beginner | Server setup, process management |

### Recommended Learning Order (if gaps exist)

```
1. Python async/await         → FastAPI works on asyncio
2. FastAPI tutorial           → docs.fastapi.tiangolo.com
3. Anthropic tool use docs    → docs.anthropic.com/tool-use
4. ChromaDB quickstart        → docs.trychroma.com
5. Google API Python client   → googleapis.github.io
6. React basics               → react.dev
7. Electron quickstart        → electronjs.org
```

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| API rate limits hit | Medium | High | Exponential backoff + caching |
| Whisper too slow on CPU | Medium | Medium | Use tiny.en model, or GPU acceleration |
| Wake word false positives | Medium | Low | Raise sensitivity threshold |
| Gmail OAuth expires | Low | High | Refresh token stored, auto-renew |
| Context window overflow | Medium | Medium | Aggressive summarization + memory injection |
| Memory drift (wrong facts stored) | Medium | Medium | Confidence scoring + manual memory editor |
| Smart home devices offline | Low | Low | Graceful fallback message |
| ElevenLabs latency | Low | Medium | Stream audio tokens as generated |
| Local server goes down | Low | High | Mobile falls back to cloud relay |
| Data breach of .env | Low | Critical | Never commit, use secrets manager |

---

## 15. Day 1 Checklist

### Environment Setup

```bash
# 1. Clone / create project
mkdir friday && cd friday
git init
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install all Python dependencies
pip install anthropic fastapi uvicorn python-dotenv pyyaml loguru \
            openai-whisper pyaudio webrtcvad pvporcupine \
            elevenlabs chromadb pinecone-client supabase \
            google-api-python-client google-auth-oauthlib \
            spotipy notion-client httpx pillow psutil \
            apscheduler RestrictedPython

# 3. Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=your_voice_id
PICOVOICE_ACCESS_KEY=your_key_here
BRAVE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_INDEX=friday-long-term
OPENAI_API_KEY=your_key_here    # For embeddings only
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
NOTION_API_KEY=your_key_here
SPOTIPY_CLIENT_ID=your_id_here
SPOTIPY_CLIENT_SECRET=your_secret_here
EOF

# 4. Create folder structure
mkdir -p core voice tools api hud mobile data/vectors config scripts tests

# 5. Start with Phase 1 — get the brain working first
# Build brain.py → test with curl → then add voice → then memory → then tools
```

### API Keys to Get (in order of priority)

```
Week 1:
  ✅ Anthropic API       → console.anthropic.com
  ✅ ElevenLabs          → elevenlabs.io (create + clone FRIDAY voice)
  ✅ Picovoice           → console.picovoice.ai (wake word)

Week 2:
  ✅ Brave Search        → brave.com/search/api/
  ✅ Google Cloud        → console.cloud.google.com (Gmail + Calendar)
  ✅ Pinecone            → app.pinecone.io

Week 3:
  ✅ Spotify             → developer.spotify.com
  ✅ Notion              → notion.so/my-integrations
  ✅ Home Assistant      → Your local HA instance (no external key needed)
  ✅ Supabase            → app.supabase.com
```

### First Working Command

```bash
# After Phase 1 is complete, this should work:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Good morning, FRIDAY."}'

# Expected response:
# "Good morning, Boss. All systems are nominal.
#  You have 3 meetings today, starting at 10 AM.
#  How can I assist you?"
```

---

> **"The day Tony Stark built JARVIS, he didn't start with the voice. He started with the brain."**
> 
> Build Phase 1 first. Get FRIDAY thinking. Everything else is just interface.

---

*Document version: 1.0 | Config: Full Stack Build | Deployment: Hybrid | Generated: April 2026*
