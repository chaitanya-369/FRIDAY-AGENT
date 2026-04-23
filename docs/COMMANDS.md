# 🎙️ FRIDAY Command Guide

FRIDAY understands natural language for controlling her own parameters. You don't need rigid slash commands; just talk to her like an assistant.

## 🧠 Model Switching
You can switch the underlying brain at any time. FRIDAY will acknowledge the change and preserve your conversation context.

**Examples:**
- *"Switch to Claude Sonnet"*
- *"Use the fastest model"*
- *"Go back to default"*
- *"Run on Llama 70B via Groq"*
- *"Switch to Gemini Flash"*

## 📊 System Diagnostics
Ask FRIDAY about her health and she will provide a comprehensive report.

**Commands:**
- *"Diagnostic"* or *"Full status"*
- *"Are you online?"*
- *"Show my API keys"*
- *"Show provider health"*
- *"Which model are you using?"*

## 🛠️ Tool Usage
FRIDAY invokes tools autonomously when needed, but you can explicitly request actions.

**Capabilities:**
- **Web Search:** *"Search for the latest news on SpaceX"*
- **System Stats:** *"How is my computer doing?"* (Checks RAM, CPU, Disk)
- **Time/Date:** *"What time is it in Tokyo?"*

---

## ⚡ Interaction Patterns

### The "Boss" Protocol
FRIDAY addresses you exclusively as **Boss**. This is hardcoded into her persona. If she fails to do so, it indicates a persona corruption or a base model override.

### Conciseness
By default, FRIDAY is designed to be sharp and brief. If you need more detail, say: *"Elaborate on that, FRIDAY."*

### Confirmation
For actions involving external APIs or local file changes, FRIDAY will often say: *"Boss, I am about to [action]. Shall I proceed?"*
