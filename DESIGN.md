---
# F.R.I.D.A.Y. Design System Tokens
# Version: 1.1.0
# Tone: Professional, Precise, Sharp, High-Fidelity

colors:
  brand:
    primary: "#00e5ff"      # Cyan / Electric Blue (System Focus / FRIDAY)
    secondary: "#ff4081"    # Magenta / Pink (User Focus / Boss)
    accent: "#7c6aff"       # Purple (Code/Technical highlights)
  
  providers:
    anthropic: "#cc785c"
    groq: "#f55036"
    openai: "#10a37f"
    gemini: "#4285f4"
    deepseek: "#5b6aff"
  
  functional:
    success: "#00ff88"      # Emerald (Online / Healthy)
    warning: "#ffaa00"      # Amber (Local / Rate-limited)
    error: "#f44336"        # Crimson (Offline / Auth Failed)
  
  neutrals:
    black: "#000000"
    deep-navy: "#001a2e"    # Background gradient core
    space-gray: "#0d0f14"   # Dashboard dark
    surface: "#111318"      # Panel/Card background
    surface-alt: "#1a1d25"  # List item hover/divider
    border: "#1e2028"       # Structure line
    border-light: "rgba(0, 229, 255, 0.15)"
    border-faint: "rgba(0, 229, 255, 0.05)"
  
  text:
    primary: "#ffffff"      # Data/Headings
    secondary: "rgba(0, 229, 255, 0.7)" # Cyan-tinted content
    muted: "#666666"        # Labels/Non-critical
    dimmed: "rgba(0, 229, 255, 0.35)"   # HUD Background labels
    boss: "#ff4081"         # User-specific text highlights

typography:
  families:
    heading: "'Orbitron', monospace"     # High-tech headers
    mono: "'Share Tech Mono', monospace" # Technical data/Primary body
    sans: "system-ui, -apple-system, sans-serif" # Fallback/Dashboard
  
  sizes:
    h1: "56px"              # Hero Display
    logo: "28px"            # Brand Header
    h2: "20px"              # Widget Value
    base: "13px"            # Dashboard Body
    ui: "12px"              # Chat/HUD Body
    tiny: "11px"            # HUD Labels
    micro: "9px"            # Technical Tickers
  
  weights:
    black: 900
    bold: 700
    regular: 400

spacing:
  gap:
    xl: "32px"
    l: "24px"
    m: "16px"
    s: "12px"
    xs: "8px"
    xxs: "4px"

effects:
  shadows:
    glow-cyan: "0 0 20px rgba(0, 229, 255, 0.4), 0 0 40px rgba(0, 229, 255, 0.2)"
    glow-cyan-heavy: "0 0 40px rgba(0, 229, 255, 0.9), 0 0 80px rgba(0, 229, 255, 0.5)"
    glow-magenta: "0 0 20px rgba(255, 64, 129, 0.3), 0 0 40px rgba(255, 64, 129, 0.15)"
    glow-magenta-heavy: "0 0 40px rgba(255, 64, 129, 0.7), 0 0 80px rgba(255, 64, 129, 0.3)"
    orb-inner: "inset 0 0 20px rgba(0, 0, 0, 0.5)"
  
  gradients:
    bg-radial: "radial-gradient(ellipse at 50% 50%, #001a2e 0%, #000 70%)"
    orb-cyan: "radial-gradient(circle at 35% 35%, #00e5ff, #0066cc, #000033)"
    msg-friday: "linear-gradient(135deg, #001a2e, #003355)"
    msg-user: "linear-gradient(135deg, #1a0010, #330020)"
    widget-top-line: "linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.5), transparent)"

  overlays:
    scanlines: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px)"
    grid: "linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px)"

animations:
  orb-rotate: "8s linear infinite"
  orb-pulse: "0.5s ease infinite"      # Listening state
  orb-glow: "0.8s ease infinite"       # Thinking state
  msg-in: "0.3s ease-out"
  status-pulse: "2s infinite"
---

# F.R.I.D.A.Y. Design System

## Core Aesthetic: Tactical HUD
F.R.I.D.A.Y. is designed as a high-fidelity, data-dense interface that bridges the gap between a traditional dashboard and an immersive "Iron Man" style HUD. The interface prioritizes **status transparency** and **proactive feedback**.

### 1. Color Strategy
- **Cyan Primary (#00e5ff):** Represents the system's "conscious" state. All FRIDAY-originated data, response bubbles, and system metrics use this glow.
- **Magenta Secondary (#ff4081):** Represents the "Boss" (User). It is used for user message avatars, user input focus states, and critical warnings that require human attention.
- **Provider Color Identity:** Complex systems like the Model Switcher use specific brand colors (e.g., Anthropic Orange, OpenAI Green) to provide instant semantic recognition of the active "Brain."

### 2. Layering & Depth
The UI uses three layers of depth to simulate a hardware-native display:
1.  **The Void:** A deep radial gradient (`bg-radial`) that provides the base.
2.  **The Scaffolding:** A fixed 40px grid and 2px scanlines that sit over the background but under the UI elements.
3.  **The Glow:** Active UI elements that emit light (`glow-cyan`, `glow-magenta`), making them appear to float above the "glass."

## Component Architecture

### The Central Orb (The Brain)
The Orb is the primary visualizer for FRIDAY's state. It is not just an icon but an animated state machine:
- **Standby:** Slow rotation (`orb-rotate`) with a steady cyan glow.
- **Listening:** Fast rotation with heavy cyan pulsing (`orb-pulse`).
- **Thinking:** Rapid magenta-shifted glow (`orb-glow`) indicating cognitive load.

### Information Widgets
Widgets follow a "Micro-Label" pattern:
- **Header:** Tiny, all-caps, letter-spaced labels (`tiny` size, 3px spacing).
- **Primary Value:** Large, high-contrast values in `Orbitron` (`h2` size).
- **Sub-Text:** Dimmest level of cyan (`dimmed`) for historical or secondary context.
- **Detail:** Every widget has a 1px top border gradient (`widget-top-line`) to define its boundary without "boxing" it in.

### Chat Interface
Messages are differentiated by **side** and **chroma**:
- **FRIDAY:** Left-aligned, Cyan theme, `msg-friday` background, blue border-left.
- **Boss:** Right-aligned, Magenta theme, `msg-user` background, pink border-right.
- **Tool Triggers:** High-visibility green badges (`success`) indicate when an autonomous tool (e.g., `web_search`) is being invoked.

## Interaction Design

### State-Based Feedback
- **Buttons:** Use `backdrop-filter: blur(8px)` and color-matched borders. Hovering shifts background opacity from `0.06` to `0.22`.
- **Input:** The command box uses a faint cyan background (`rgba(0,229,255,0.03)`) and brightens its border on focus.
- **Transitions:** Use `msg-in` (fade + 10px slide) for all incoming messages and alerts to ensure the UI feels fluid and alive.

### Status Indicators
System health is communicated via "Status Dots":
- **Healthy:** Green with glow.
- **Degraded/Local:** Amber (Ollama fallback).
- **Critical/Offline:** Red (API unreachable).
- **Animation:** All status dots pulse slowly (`status-pulse`) to show they are actively monitoring.
