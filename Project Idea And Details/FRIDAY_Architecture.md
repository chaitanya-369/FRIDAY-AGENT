# 🤖 FRIDAY AI Assistant — Full Architecture Guide

> **F**emale **R**eplacement **I**ntelligent **D**igital **A**ssistant **Y**ield  
> Inspired by Tony Stark's AI from Iron Man

---

## 🧠 Tech Stack (Best-in-Class)

| Layer | Technology | Why |
|---|---|---|
| **LLM Brain** | Claude API (claude-sonnet-4-20250514) | Best reasoning + tool use |
| **Agent Framework** | LangGraph | Stateful multi-agent workflows |
| **STT (Ears)** | faster-whisper (local) | Fast, free, offline-capable |
| **TTS (Voice)** | ElevenLabs API | Most human-like female voice |
| **Wake Word** | openWakeWord | Open-source, runs locally |
| **Web Search** | Tavily API | Built for AI agents |
| **Memory** | ChromaDB + LangChain | Persistent vector memory |
| **PC Control** | PyAutoGUI + subprocess | Cross-platform automation |
| **Backend** | FastAPI (Python) | Async, fast, WebSocket support |
| **Frontend** | React + Vite + Electron | Desktop app with web UI |

---

## 📁 Project Structure

```
friday/
├── main.py                    # Entry point
├── config.py                  # API keys, settings
│
├── core/
│   ├── agent.py               # LangGraph agent orchestrator
│   ├── memory.py              # ChromaDB vector memory
│   ├── personality.py         # FRIDAY's system prompt & persona
│   └── context.py             # Session context manager
│
├── voice/
│   ├── stt.py                 # faster-whisper speech-to-text
│   ├── tts.py                 # ElevenLabs text-to-speech
│   ├── wake_word.py           # openWakeWord detection
│   └── audio_stream.py        # PyAudio real-time streaming
│
├── tools/                     # Agent tools (LangChain @tool)
│   ├── web_search.py          # Tavily web search
│   ├── pc_control.py          # Open apps, type, click
│   ├── file_ops.py            # Read/write/search files
│   ├── system_info.py         # CPU, battery, time, weather
│   └── browser_control.py     # Open URLs, search browser
│
├── api/
│   └── server.py              # FastAPI + WebSocket server
│
└── ui/
    ├── package.json
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── VoiceVisualizer.jsx
        │   ├── ChatFeed.jsx
        │   └── StatusHUD.jsx
        └── styles/
```

---

## 🔧 Installation

```bash
# 1. Create environment
python -m venv friday-env
source friday-env/bin/activate  # Windows: friday-env\Scripts\activate

# 2. Install Python deps
pip install langchain langgraph langchain-anthropic
pip install faster-whisper pyaudio sounddevice
pip install elevenlabs
pip install openwakeword
pip install chromadb
pip install tavily-python
pip install pyautogui psutil
pip install fastapi uvicorn websockets python-dotenv

# 3. Frontend
cd ui && npm install && npm run dev
```

---

## ⚙️ config.py

```python
import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

FRIDAY_VOICE_ID = "your-elevenlabs-voice-id"  # Pick a female voice
WAKE_WORD = "hey friday"
WHISPER_MODEL = "base.en"  # tiny / base / small / medium
```

---

## 🧬 core/personality.py

```python
FRIDAY_SYSTEM_PROMPT = """
You are FRIDAY — an advanced AI assistant with a warm, witty, and confident personality.
You speak in a friendly Irish-accented manner (like in Iron Man).
You are direct, capable, and slightly playful.

Your capabilities:
- Search the web for real-time information
- Control the user's PC (open apps, type, click)
- Manage files and folders
- Monitor system status
- Answer any question with reasoning

Rules:
- Keep responses concise unless detail is requested
- Confirm before executing system actions
- Address the user as "Boss" occasionally for personality
- Never say you can't do something without trying first
"""
```

---

## 🤖 core/agent.py

```python
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools.web_search import web_search
from tools.pc_control import open_app, type_text
from tools.system_info import get_system_info
from core.personality import FRIDAY_SYSTEM_PROMPT
from core.memory import FridayMemory
from config import ANTHROPIC_API_KEY

# Initialize LLM
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=ANTHROPIC_API_KEY,
    temperature=0.7
)

# Register all tools
tools = [web_search, open_app, type_text, get_system_info]

# Create ReAct agent with LangGraph
agent = create_react_agent(llm, tools, state_modifier=FRIDAY_SYSTEM_PROMPT)

memory = FridayMemory()

async def process_command(user_input: str, session_id: str = "default") -> str:
    # Fetch relevant memories
    past_context = memory.recall(user_input)
    
    messages = []
    if past_context:
        messages.append(HumanMessage(content=f"[Context from memory]: {past_context}"))
    messages.append(HumanMessage(content=user_input))
    
    result = await agent.ainvoke({"messages": messages})
    response = result["messages"][-1].content
    
    # Store to memory
    memory.store(user_input, response, session_id)
    
    return response
```

---

## 🔊 voice/stt.py

```python
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel("base.en", device="cpu", compute_type="int8")

def listen_once(duration=5, sample_rate=16000) -> str:
    """Record audio and transcribe"""
    print("🎤 Listening...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate,
                   channels=1, dtype='float32')
    sd.wait()
    audio_flat = audio.flatten()
    
    segments, _ = model.transcribe(audio_flat, beam_size=5)
    text = " ".join([seg.text for seg in segments]).strip()
    print(f"📝 Heard: {text}")
    return text
```

---

## 🗣️ voice/tts.py

```python
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from config import ELEVENLABS_API_KEY, FRIDAY_VOICE_ID

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def speak(text: str):
    """Convert text to FRIDAY's voice and play"""
    print(f"🔊 FRIDAY: {text}")
    audio = client.generate(
        text=text,
        voice=FRIDAY_VOICE_ID,
        model="eleven_turbo_v2"  # Fastest model
    )
    play(audio)
```

---

## 👂 voice/wake_word.py

```python
import pyaudio
import numpy as np
from openwakeword.model import Model

model = Model(wakeword_models=["hey_friday"], inference_framework="onnx")

def start_listening(callback):
    """Continuously listen for wake word, call callback when detected"""
    pa = pyaudio.PyAudio()
    stream = pa.open(rate=16000, channels=1, format=pyaudio.paInt16,
                     input=True, frames_per_buffer=1280)
    
    print("👂 Waiting for wake word: 'Hey FRIDAY'...")
    
    while True:
        audio_chunk = np.frombuffer(stream.read(1280), dtype=np.int16)
        predictions = model.predict(audio_chunk)
        
        if predictions.get("hey_friday", 0) > 0.7:
            print("⚡ Wake word detected!")
            callback()
```

---

## 🛠️ tools/web_search.py

```python
from langchain.tools import tool
from tavily import TavilyClient
from config import TAVILY_API_KEY

tavily = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:
    """Search the web for real-time information"""
    results = tavily.search(query=query, max_results=3)
    return "\n".join([r["content"] for r in results["results"]])
```

---

## 🖥️ tools/pc_control.py

```python
from langchain.tools import tool
import subprocess
import pyautogui
import platform

@tool
def open_app(app_name: str) -> str:
    """Open an application by name (e.g., 'chrome', 'vscode', 'spotify')"""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(["start", app_name], shell=True)
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", app_name])
        else:  # Linux
            subprocess.Popen([app_name])
        return f"Opened {app_name} successfully"
    except Exception as e:
        return f"Could not open {app_name}: {e}"

@tool
def type_text(text: str) -> str:
    """Type text at the current cursor position"""
    pyautogui.typewrite(text, interval=0.05)
    return f"Typed: {text}"

@tool
def take_screenshot() -> str:
    """Take a screenshot and save it"""
    screenshot = pyautogui.screenshot()
    path = "friday_screenshot.png"
    screenshot.save(path)
    return f"Screenshot saved to {path}"
```

---

## 🌐 api/server.py

```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from core.agent import process_command
import json

app = FastAPI(title="FRIDAY API")
app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)
        response = await process_command(message["text"])
        await websocket.send_text(json.dumps({"response": response}))

@app.post("/chat")
async def chat(payload: dict):
    response = await process_command(payload["text"])
    return {"response": response}
```

---

## 🚀 main.py

```python
import asyncio
import threading
from voice.wake_word import start_listening
from voice.stt import listen_once
from voice.tts import speak
from core.agent import process_command

def on_wake_word():
    """Triggered when 'Hey FRIDAY' is detected"""
    speak("Yes, Boss?")
    user_input = listen_once(duration=8)
    
    if user_input:
        response = asyncio.run(process_command(user_input))
        speak(response)

if __name__ == "__main__":
    speak("FRIDAY online. How can I help you, Boss?")
    
    # Start wake word listener in background
    wake_thread = threading.Thread(target=start_listening, args=(on_wake_word,))
    wake_thread.daemon = True
    wake_thread.start()
    
    # Also start the API server
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=False)
```

---

## 🔑 .env file

```
ANTHROPIC_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

---

## 🗺️ Roadmap

### Phase 1 — Core (Week 1-2)
- [ ] Basic chat with Claude API
- [ ] Text-to-speech with ElevenLabs
- [ ] Speech-to-text with Whisper
- [ ] Web search tool

### Phase 2 — Intelligence (Week 3-4)
- [ ] Wake word detection
- [ ] PC control tools
- [ ] Persistent memory with ChromaDB
- [ ] Multi-tool agent with LangGraph

### Phase 3 — Interface (Week 5-6)
- [ ] React UI with voice visualizer
- [ ] Electron desktop app
- [ ] HUD-style overlay

### Phase 4 — Advanced (Month 2+)
- [ ] Calendar & email integration
- [ ] Custom wake word training
- [ ] Vision (screenshot analysis)
- [ ] Smart home control

---

## 🧪 Key APIs to Get

| Service | URL | Free Tier |
|---|---|---|
| Anthropic (Claude) | console.anthropic.com | $5 free credits |
| ElevenLabs | elevenlabs.io | 10k chars/month free |
| Tavily | tavily.com | 1000 searches/month free |
| OpenWeatherMap | openweathermap.org | Free |

---

*Built with ❤️ — Inspired by Tony Stark's FRIDAY*
