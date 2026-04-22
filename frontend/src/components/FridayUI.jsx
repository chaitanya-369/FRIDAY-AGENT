import { useState, useEffect, useRef } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: #000;
    font-family: 'Share Tech Mono', monospace;
    color: #00e5ff;
    overflow: hidden;
    height: 100vh;
  }

  .friday-root {
    width: 100vw;
    height: 100vh;
    background: radial-gradient(ellipse at 50% 50%, #001a2e 0%, #000 70%);
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }

  /* Animated grid background */
  .grid-bg {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,229,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,229,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
  }

  /* Scanline effect */
  .scanlines {
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.08) 2px,
      rgba(0,0,0,0.08) 4px
    );
    pointer-events: none;
    z-index: 10;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    border-bottom: 1px solid rgba(0,229,255,0.15);
    position: relative;
    z-index: 5;
  }

  .logo {
    font-family: 'Orbitron', monospace;
    font-weight: 900;
    font-size: 28px;
    letter-spacing: 8px;
    color: #00e5ff;
    text-shadow: 0 0 20px rgba(0,229,255,0.8), 0 0 40px rgba(0,229,255,0.4);
  }

  .logo span { color: #ff4081; }

  .status-bar {
    display: flex;
    gap: 24px;
    font-size: 11px;
    color: rgba(0,229,255,0.5);
    letter-spacing: 2px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00ff88;
    box-shadow: 0 0 8px #00ff88;
    animation: pulse 2s infinite;
  }

  .status-dot.warn { background: #ffaa00; box-shadow: 0 0 8px #ffaa00; }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* Main layout */
  .main-layout {
    flex: 1;
    display: grid;
    grid-template-columns: 260px 1fr 260px;
    gap: 0;
    padding: 0;
    overflow: hidden;
    position: relative;
    z-index: 5;
  }

  /* Side panels */
  .side-panel {
    padding: 20px 16px;
    border-right: 1px solid rgba(0,229,255,0.1);
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
  }

  .side-panel.right {
    border-right: none;
    border-left: 1px solid rgba(0,229,255,0.1);
  }

  .panel-title {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    color: rgba(0,229,255,0.4);
    text-transform: uppercase;
    margin-bottom: 4px;
  }

  .widget {
    border: 1px solid rgba(0,229,255,0.12);
    border-radius: 4px;
    padding: 12px;
    background: rgba(0,229,255,0.02);
    position: relative;
    overflow: hidden;
  }

  .widget::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,229,255,0.5), transparent);
  }

  .widget-label {
    font-size: 9px;
    letter-spacing: 2px;
    color: rgba(0,229,255,0.35);
    margin-bottom: 8px;
    text-transform: uppercase;
  }

  .widget-value {
    font-family: 'Orbitron', monospace;
    font-size: 20px;
    color: #00e5ff;
    text-shadow: 0 0 10px rgba(0,229,255,0.5);
  }

  .widget-sub { font-size: 10px; color: rgba(0,229,255,0.4); margin-top: 4px; }

  /* Bar chart */
  .bar-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }

  .bar-label { font-size: 9px; color: rgba(0,229,255,0.4); width: 28px; }

  .bar-track {
    flex: 1;
    height: 4px;
    background: rgba(0,229,255,0.08);
    border-radius: 2px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 1s ease;
  }

  .bar-pct { font-size: 9px; color: rgba(0,229,255,0.4); width: 28px; text-align: right; }

  /* Tool status */
  .tool-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid rgba(0,229,255,0.05);
    font-size: 10px;
  }

  .tool-name { color: rgba(0,229,255,0.6); }
  .tool-badge {
    font-size: 8px;
    letter-spacing: 1px;
    padding: 2px 6px;
    border-radius: 2px;
  }

  .badge-active { background: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
  .badge-idle { background: rgba(0,229,255,0.05); color: rgba(0,229,255,0.3); border: 1px solid rgba(0,229,255,0.1); }

  /* Center - Chat */
  .chat-center {
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }

  /* Orb visualizer */
  .orb-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px 0 12px;
    position: relative;
  }

  .orb-outer {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 1px solid rgba(0,229,255,0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    animation: orb-rotate 8s linear infinite;
  }

  @keyframes orb-rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .orb-inner {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #00e5ff, #0066cc, #000033);
    box-shadow:
      0 0 20px rgba(0,229,255,0.4),
      0 0 40px rgba(0,229,255,0.2),
      inset 0 0 20px rgba(0,0,0,0.5);
    position: relative;
    animation: orb-rotate 8s linear infinite reverse;
  }

  .orb-inner.listening {
    animation: orb-rotate 1s linear infinite reverse, orb-pulse 0.5s ease infinite;
  }

  .orb-inner.thinking {
    animation: orb-rotate 2s linear infinite reverse, orb-glow 0.8s ease infinite;
  }

  @keyframes orb-pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(0,229,255,0.4), 0 0 40px rgba(0,229,255,0.2); }
    50% { box-shadow: 0 0 40px rgba(0,229,255,0.9), 0 0 80px rgba(0,229,255,0.5); }
  }

  @keyframes orb-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(255,64,129,0.3), 0 0 40px rgba(255,64,129,0.15); }
    50% { box-shadow: 0 0 40px rgba(255,64,129,0.7), 0 0 80px rgba(255,64,129,0.3); }
  }

  .orb-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(0,229,255,0.15);
  }

  .orb-ring-1 { width: 120px; height: 120px; }
  .orb-ring-2 { width: 145px; height: 145px; border-color: rgba(0,229,255,0.07); }

  .friday-state {
    font-family: 'Orbitron', monospace;
    font-size: 9px;
    letter-spacing: 4px;
    color: rgba(0,229,255,0.5);
    text-align: center;
    margin-top: -8px;
    margin-bottom: 8px;
    text-transform: uppercase;
  }

  /* Chat messages */
  .chat-feed {
    flex: 1;
    overflow-y: auto;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .chat-feed::-webkit-scrollbar { width: 3px; }
  .chat-feed::-webkit-scrollbar-track { background: transparent; }
  .chat-feed::-webkit-scrollbar-thumb { background: rgba(0,229,255,0.2); border-radius: 2px; }

  .message {
    display: flex;
    gap: 10px;
    animation: msg-in 0.3s ease;
  }

  @keyframes msg-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .message.user { flex-direction: row-reverse; }

  .msg-avatar {
    width: 28px;
    height: 28px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    flex-shrink: 0;
    font-family: 'Orbitron', monospace;
    font-weight: 700;
  }

  .avatar-friday {
    background: linear-gradient(135deg, #001a2e, #003355);
    border: 1px solid rgba(0,229,255,0.3);
    color: #00e5ff;
    box-shadow: 0 0 10px rgba(0,229,255,0.2);
  }

  .avatar-user {
    background: linear-gradient(135deg, #1a0010, #330020);
    border: 1px solid rgba(255,64,129,0.3);
    color: #ff4081;
  }

  .msg-bubble {
    max-width: 75%;
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 12px;
    line-height: 1.6;
    position: relative;
  }

  .bubble-friday {
    background: rgba(0,229,255,0.05);
    border: 1px solid rgba(0,229,255,0.12);
    color: rgba(0,229,255,0.85);
    border-left: 2px solid rgba(0,229,255,0.5);
  }

  .bubble-user {
    background: rgba(255,64,129,0.05);
    border: 1px solid rgba(255,64,129,0.12);
    color: rgba(255,64,129,0.85);
    border-right: 2px solid rgba(255,64,129,0.5);
    text-align: right;
  }

  .msg-time {
    font-size: 8px;
    color: rgba(0,229,255,0.2);
    margin-top: 4px;
    letter-spacing: 1px;
  }

  .message.user .msg-time { text-align: right; color: rgba(255,64,129,0.2); }

  /* Tool use indicator */
  .tool-use-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(0,255,136,0.06);
    border: 1px solid rgba(0,255,136,0.2);
    border-radius: 2px;
    padding: 2px 8px;
    font-size: 9px;
    letter-spacing: 1px;
    color: #00ff88;
    margin-bottom: 6px;
  }

  /* Input area */
  .input-area {
    padding: 16px 24px 20px;
    border-top: 1px solid rgba(0,229,255,0.08);
  }

  .input-row {
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }

  .input-box {
    flex: 1;
    background: rgba(0,229,255,0.03);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 4px;
    padding: 10px 14px;
    color: #00e5ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    resize: none;
    outline: none;
    transition: border-color 0.2s;
    min-height: 42px;
    max-height: 100px;
  }

  .input-box::placeholder { color: rgba(0,229,255,0.2); }
  .input-box:focus { border-color: rgba(0,229,255,0.4); }

  .btn {
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    color: #00e5ff;
    width: 42px;
    height: 42px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .btn:hover { background: rgba(0,229,255,0.15); border-color: rgba(0,229,255,0.4); }
  .btn.active { background: rgba(255,64,129,0.15); border-color: rgba(255,64,129,0.4); color: #ff4081; animation: orb-pulse 0.5s infinite; }

  .input-hints {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
  }

  .hint-chip {
    font-size: 9px;
    letter-spacing: 1px;
    color: rgba(0,229,255,0.25);
    border: 1px solid rgba(0,229,255,0.08);
    padding: 3px 8px;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .hint-chip:hover { color: rgba(0,229,255,0.6); border-color: rgba(0,229,255,0.2); }

  /* Thinking dots */
  .thinking-dots span {
    display: inline-block;
    animation: dot-bounce 1.4s infinite;
    color: rgba(0,229,255,0.5);
  }
  .thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
  .thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

  @keyframes dot-bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.3; }
    40% { transform: translateY(-4px); opacity: 1; }
  }
`;

const DEMO_MESSAGES = [
  {
    id: 1, role: "friday",
    text: "FRIDAY online. All systems nominal. How can I assist you today, Boss?",
    time: "09:41:00", tools: []
  },
  {
    id: 2, role: "user",
    text: "Search the latest news about AI agents and open Chrome.",
    time: "09:41:22", tools: []
  },
  {
    id: 3, role: "friday",
    text: "Executing two tasks simultaneously. Found 3 relevant articles on AI agent frameworks — LangGraph and AutoGen are dominating, with OpenAI releasing a new agents SDK last week. Chrome is now open. Anything else?",
    time: "09:41:25",
    tools: ["web_search", "open_app"]
  }
];

const HINTS = [
  "Open Spotify", "What's the weather?", "Search AI news", "Take a screenshot", "System status"
];

const NOW = new Date();
const pad = n => String(n).padStart(2, "0");
const timeStr = `${pad(NOW.getHours())}:${pad(NOW.getMinutes())}:${pad(NOW.getSeconds())}`;
const dateStr = NOW.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

export default function FridayUI() {
  const [messages, setMessages] = useState(DEMO_MESSAGES);
  const [input, setInput] = useState("");
  const [state, setState] = useState("STANDBY"); // STANDBY | LISTENING | THINKING | SPEAKING
  const [isListening, setIsListening] = useState(false);
  const [cpuVal] = useState(42);
  const [memVal] = useState(67);
  const [netVal] = useState(28);
  const chatRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { id: Date.now(), role: "user", text: input, time: timeStr, tools: [] };
    setMessages(m => [...m, userMsg]);
    setInput("");
    setState("THINKING");

    // Simulate response delay
    setTimeout(() => {
      const responses = [
        { text: "On it, Boss. Task completed successfully.", tools: [] },
        { text: "Searching the web now... Found relevant results. Here's a summary of the latest data.", tools: ["web_search"] },
        { text: "Application launched. Is there anything else you'd like me to do?", tools: ["open_app"] },
        { text: "Analyzing system status. CPU at 42%, RAM at 67%, all processes nominal.", tools: ["system_info"] },
      ];
      const r = responses[Math.floor(Math.random() * responses.length)];
      setMessages(m => [...m, { id: Date.now(), role: "friday", ...r, time: timeStr }]);
      setState("STANDBY");
    }, 1500);
  };

  const toggleListen = () => {
    if (isListening) {
      setIsListening(false);
      setState("STANDBY");
    } else {
      setIsListening(true);
      setState("LISTENING");
      setTimeout(() => {
        setIsListening(false);
        setInput("What's the latest news in AI?");
        setState("STANDBY");
      }, 3000);
    }
  };

  const STATE_LABELS = {
    STANDBY: "STANDBY", LISTENING: "LISTENING", THINKING: "PROCESSING", SPEAKING: "RESPONDING"
  };

  return (
    <>
      <style>{styles}</style>
      <div className="friday-root">
        <div className="grid-bg" />
        <div className="scanlines" />

        {/* Header */}
        <div className="header">
          <div className="logo">FRI<span>D</span>AY</div>
          <div className="status-bar">
            <div className="status-item"><div className="status-dot" /> ONLINE</div>
            <div className="status-item"><div className="status-dot" /> CLAUDE API</div>
            <div className="status-item"><div className="status-dot warn" /> VOICE READY</div>
            <div className="status-item" style={{color: "rgba(0,229,255,0.35)"}}>{dateStr} · {timeStr}</div>
          </div>
        </div>

        {/* Main */}
        <div className="main-layout">

          {/* Left Panel */}
          <div className="side-panel">
            <div className="panel-title">System Monitor</div>

            <div className="widget">
              <div className="widget-label">CPU Usage</div>
              {[["CPU", cpuVal, "#00e5ff"], ["MEM", memVal, "#ff4081"], ["NET", netVal, "#00ff88"]].map(([l, v, c]) => (
                <div className="bar-row" key={l}>
                  <div className="bar-label">{l}</div>
                  <div className="bar-track"><div className="bar-fill" style={{width: `${v}%`, background: c}} /></div>
                  <div className="bar-pct">{v}%</div>
                </div>
              ))}
            </div>

            <div className="widget">
              <div className="widget-label">Session Time</div>
              <div className="widget-value">00:18:42</div>
              <div className="widget-sub">Active since 09:22 AM</div>
            </div>

            <div className="widget">
              <div className="widget-label">Commands Run</div>
              <div className="widget-value">{messages.filter(m => m.role === "user").length}</div>
              <div className="widget-sub">This session</div>
            </div>

            <div className="widget">
              <div className="widget-label">Memory Stored</div>
              <div className="widget-value">47</div>
              <div className="widget-sub">Interactions indexed</div>
            </div>
          </div>

          {/* Center - Chat */}
          <div className="chat-center">
            <div className="orb-container">
              <div className="orb-ring orb-ring-2" />
              <div className="orb-ring orb-ring-1" />
              <div className="orb-outer">
                <div className={`orb-inner ${state === "LISTENING" ? "listening" : state === "THINKING" ? "thinking" : ""}`} />
              </div>
            </div>
            <div className="friday-state">{STATE_LABELS[state]}</div>

            <div className="chat-feed" ref={chatRef}>
              {messages.map(msg => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className={`msg-avatar ${msg.role === "friday" ? "avatar-friday" : "avatar-user"}`}>
                    {msg.role === "friday" ? "F" : "B"}
                  </div>
                  <div>
                    {msg.tools && msg.tools.length > 0 && (
                      <div style={{marginBottom: 4}}>
                        {msg.tools.map(t => (
                          <span key={t} className="tool-use-chip">⚡ {t}</span>
                        ))}
                      </div>
                    )}
                    <div className={`msg-bubble ${msg.role === "friday" ? "bubble-friday" : "bubble-user"}`}>
                      {msg.text}
                    </div>
                    <div className="msg-time">{msg.time}</div>
                  </div>
                </div>
              ))}
              {state === "THINKING" && (
                <div className="message friday">
                  <div className="msg-avatar avatar-friday">F</div>
                  <div>
                    <div className="msg-bubble bubble-friday">
                      <span className="thinking-dots"><span>·</span><span>·</span><span>·</span></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="input-area">
              <div className="input-row">
                <textarea
                  ref={inputRef}
                  className="input-box"
                  rows={1}
                  placeholder="Command FRIDAY..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }}}
                />
                <button className={`btn ${isListening ? "active" : ""}`} onClick={toggleListen} title="Voice input">
                  {isListening ? "⏹" : "🎤"}
                </button>
                <button className="btn" onClick={sendMessage} title="Send">
                  ▶
                </button>
              </div>
              <div className="input-hints">
                {HINTS.map(h => (
                  <div key={h} className="hint-chip" onClick={() => setInput(h)}>{h}</div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="side-panel right">
            <div className="panel-title">Agent Tools</div>

            <div className="widget">
              <div className="widget-label">Active Tools</div>
              {[
                ["web_search", true], ["pc_control", true],
                ["file_ops", true], ["system_info", true],
                ["wake_word", false], ["memory", true],
              ].map(([name, active]) => (
                <div className="tool-row" key={name}>
                  <span className="tool-name">{name}</span>
                  <span className={`tool-badge ${active ? "badge-active" : "badge-idle"}`}>
                    {active ? "ACTIVE" : "IDLE"}
                  </span>
                </div>
              ))}
            </div>

            <div className="widget">
              <div className="widget-label">LLM</div>
              <div style={{fontSize: 10, color: "rgba(0,229,255,0.5)", lineHeight: 1.8}}>
                <div>MODEL claude-sonnet-4</div>
                <div>TEMP 0.7</div>
                <div>TOKENS 4.2K used</div>
              </div>
            </div>

            <div className="widget">
              <div className="widget-label">Recent Actions</div>
              {[
                ["09:41", "web_search", "AI agent news"],
                ["09:41", "open_app", "chrome"],
                ["09:38", "system_info", "status check"],
              ].map(([t, tool, arg], i) => (
                <div key={i} style={{fontSize: 9, color: "rgba(0,229,255,0.35)", padding: "4px 0", borderBottom: "1px solid rgba(0,229,255,0.05)"}}>
                  <span style={{color: "rgba(0,229,255,0.2)"}}>{t} </span>
                  <span style={{color: "#00ff88"}}>{tool}</span>
                  <span> "{arg}"</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
