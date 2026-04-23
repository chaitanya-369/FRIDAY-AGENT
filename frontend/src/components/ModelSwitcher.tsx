import React, { useCallback, useEffect, useRef, useState } from "react";

const API = "http://localhost:8000";

// ── Types ──────────────────────────────────────────────────────────────────────

interface Provider {
  id: number;
  name: string;
  display_name: string;
  is_enabled: boolean;
  priority: number;
}

interface ModelEntry {
  id: number;
  provider_id: number;
  model_id: string;
  display_name: string;
  supports_tools: boolean;
  supports_vision: boolean;
  cost_input_per_1m: number | null;
  cost_output_per_1m: number | null;
}

interface SessionState {
  provider_name: string;
  model_id: string;
  set_by: string;
  reason: string;
  switched_at: string | null;
  switch_history: Array<{
    provider_name: string;
    model_id: string;
    set_by: string;
    reason: string;
    switched_at: string;
  }>;
}

interface StatusState {
  is_online: boolean;
  ollama_available: boolean;
  ollama_models: string[];
  providers: Array<{
    provider_name: string;
    display_name: string;
    healthy_keys: number;
    rate_limited_keys: number;
    auth_failed_keys: number;
    total_keys: number;
  }>;
}

// ── Provider colour map ────────────────────────────────────────────────────────

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: "#cc785c",
  groq:      "#f55036",
  openai:    "#10a37f",
  gemini:    "#4285f4",
  deepseek:  "#5b6aff",
};

const PROVIDER_ICONS: Record<string, string> = {
  anthropic: "🔸",
  groq:      "⚡",
  openai:    "✨",
  gemini:    "💎",
  deepseek:  "🌊",
};

function providerColor(name: string) {
  return PROVIDER_COLORS[name] || "#888";
}
function providerIcon(name: string) {
  return PROVIDER_ICONS[name] || "🤖";
}

// ── ModelSwitcher Component ────────────────────────────────────────────────────

interface ModelSwitcherProps {
  session: SessionState | null;
  status: StatusState | null;
  onSwitch: () => void;
}

export const ModelSwitcher: React.FC<ModelSwitcherProps> = ({ session, status, onSwitch }) => {
  const [open, setOpen] = useState(false);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [switching, setSwitching] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  // Load providers and models catalog on open
  useEffect(() => {
    if (!open) return;
    Promise.all([
      fetch(`${API}/api/providers`).then((r) => r.json()),
      fetch(`${API}/api/models`).then((r) => r.json()),
    ]).then(([provList, modelList]) => {
      setProviders(provList);
      setModels(modelList);
      if (provList.length && !activeTab) setActiveTab(provList[0].name);
    }).catch(() => {});
  }, [open]);

  // Close on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Keyboard shortcut: Ctrl+Shift+M
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === "M") {
        setOpen((v) => !v);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const handleSwitch = useCallback(async (providerName: string, modelId: string) => {
    setSwitching(true);
    try {
      await fetch(`${API}/api/session/switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider_name: providerName, model_id: modelId }),
      });
      onSwitch();
      setOpen(false);
    } catch {}
    setSwitching(false);
  }, [onSwitch]);

  const handleReset = useCallback(async () => {
    await fetch(`${API}/api/session/reset`, { method: "POST" });
    onSwitch();
    setOpen(false);
  }, [onSwitch]);

  if (!session) return null;

  const color = providerColor(session.provider_name);
  const icon = providerIcon(session.provider_name);
  const isOnline = status?.is_online ?? true;
  const healthDot = isOnline ? "🟢" : (status?.ollama_available ? "🟡" : "🔴");

  const tabModels = models.filter((m) => {
    const prov = providers.find((p) => p.name === activeTab);
    return prov ? m.provider_id === prov.id : false;
  });

  return (
    <div ref={ref} style={{ position: "relative", display: "inline-block" }}>
      {/* ── Trigger badge ── */}
      <button
        id="model-switcher-trigger"
        onClick={() => setOpen((v) => !v)}
        title="Switch Model (Ctrl+Shift+M)"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          background: "rgba(255,255,255,0.06)",
          border: `1px solid ${color}55`,
          borderRadius: "8px",
          color: "#fff",
          padding: "5px 12px",
          cursor: "pointer",
          fontSize: "13px",
          transition: "all 0.2s",
          backdropFilter: "blur(8px)",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLButtonElement).style.background = `${color}22`;
          (e.currentTarget as HTMLButtonElement).style.borderColor = color;
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.06)";
          (e.currentTarget as HTMLButtonElement).style.borderColor = `${color}55`;
        }}
      >
        <span>{healthDot}</span>
        <span style={{ color }}>{icon}</span>
        <span style={{ fontWeight: 600 }}>
          {session.provider_name.charAt(0).toUpperCase() + session.provider_name.slice(1)}
        </span>
        <span style={{ color: "#aaa", fontSize: "11px" }}>/ {session.model_id.split("-").slice(0, 2).join("-")}</span>
        <span style={{ color: "#888", fontSize: "10px" }}>▾</span>
      </button>

      {/* ── Dropdown panel ── */}
      {open && (
        <div
          id="model-switcher-panel"
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            width: "480px",
            background: "#111318",
            border: "1px solid #2a2d35",
            borderRadius: "12px",
            boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
            zIndex: 999,
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <div style={{ padding: "14px 16px", borderBottom: "1px solid #1e2028", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ color: "#fff", fontWeight: 700, fontSize: "14px" }}>Model Switcher</div>
              <div style={{ color: "#666", fontSize: "11px", marginTop: "2px" }}>Ctrl+Shift+M</div>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => setShowHistory((v) => !v)}
                style={{ background: "transparent", border: "1px solid #333", borderRadius: "6px", color: "#aaa", padding: "4px 8px", cursor: "pointer", fontSize: "11px" }}
              >
                {showHistory ? "Models" : "History"}
              </button>
              <button
                onClick={handleReset}
                title="Reset to default"
                style={{ background: "transparent", border: "1px solid #333", borderRadius: "6px", color: "#888", padding: "4px 8px", cursor: "pointer", fontSize: "11px" }}
              >
                Reset
              </button>
            </div>
          </div>

          {showHistory ? (
            /* Switch history tab */
            <div style={{ padding: "8px 0", maxHeight: "320px", overflowY: "auto" }}>
              {(!session.switch_history || session.switch_history.length === 0) ? (
                <div style={{ padding: "20px 16px", color: "#555", fontSize: "12px", textAlign: "center" }}>
                  No switch history yet.
                </div>
              ) : (
                session.switch_history.slice(0, 10).map((h, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "10px",
                      padding: "8px 16px",
                      borderBottom: "1px solid #1a1d25",
                    }}
                  >
                    <span style={{ color: providerColor(h.provider_name), fontSize: "14px" }}>
                      {providerIcon(h.provider_name)}
                    </span>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: "#ddd", fontSize: "12px" }}>
                        {h.provider_name} / {h.model_id.split("-").slice(0, 3).join("-")}
                      </div>
                      <div style={{ color: "#555", fontSize: "10px" }}>
                        {h.set_by} · {h.switched_at ? new Date(h.switched_at).toLocaleTimeString() : ""}
                      </div>
                    </div>
                    <button
                      onClick={() => handleSwitch(h.provider_name, h.model_id)}
                      disabled={switching}
                      style={{
                        background: "transparent",
                        border: `1px solid ${providerColor(h.provider_name)}44`,
                        borderRadius: "5px",
                        color: providerColor(h.provider_name),
                        padding: "3px 7px",
                        cursor: "pointer",
                        fontSize: "10px",
                      }}
                    >
                      Use
                    </button>
                  </div>
                ))
              )}
            </div>
          ) : (
            /* Models browser tab */
            <div style={{ display: "flex", height: "320px" }}>
              {/* Provider sidebar */}
              <div style={{ width: "120px", borderRight: "1px solid #1e2028", overflowY: "auto" }}>
                {providers.map((p) => {
                  const provHealth = status?.providers.find((ph) => ph.provider_name === p.name);
                  const hasHealthy = (provHealth?.healthy_keys ?? 0) > 0;
                  const dot = hasHealthy ? "🟢" : ((provHealth?.rate_limited_keys ?? 0) > 0 ? "🟡" : "🔴");
                  return (
                    <div
                      key={p.name}
                      onClick={() => setActiveTab(p.name)}
                      style={{
                        padding: "10px 12px",
                        cursor: "pointer",
                        background: activeTab === p.name ? `${providerColor(p.name)}18` : "transparent",
                        borderLeft: activeTab === p.name ? `3px solid ${providerColor(p.name)}` : "3px solid transparent",
                        transition: "all 0.15s",
                      }}
                    >
                      <div style={{ fontSize: "14px" }}>{providerIcon(p.name)}</div>
                      <div style={{ color: activeTab === p.name ? providerColor(p.name) : "#999", fontSize: "11px", marginTop: "3px", fontWeight: activeTab === p.name ? 600 : 400 }}>
                        {p.display_name.split(" ")[0]}
                      </div>
                      <div style={{ fontSize: "9px", marginTop: "2px" }}>{dot}</div>
                    </div>
                  );
                })}
              </div>

              {/* Model list */}
              <div style={{ flex: 1, overflowY: "auto", padding: "4px 0" }}>
                {tabModels.length === 0 ? (
                  <div style={{ padding: "20px 16px", color: "#444", fontSize: "12px" }}>No models available.</div>
                ) : (
                  tabModels.map((m) => {
                    const isActive = session.provider_name === activeTab && session.model_id === m.model_id;
                    const color = providerColor(activeTab || "");
                    return (
                      <div
                        key={m.model_id}
                        onClick={() => !isActive && !switching && handleSwitch(activeTab!, m.model_id)}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          padding: "10px 14px",
                          cursor: isActive ? "default" : "pointer",
                          background: isActive ? `${color}18` : "transparent",
                          borderLeft: isActive ? `3px solid ${color}` : "3px solid transparent",
                          transition: "all 0.15s",
                          opacity: switching ? 0.6 : 1,
                        }}
                        onMouseEnter={(e) => {
                          if (!isActive) (e.currentTarget as HTMLDivElement).style.background = `${color}10`;
                        }}
                        onMouseLeave={(e) => {
                          if (!isActive) (e.currentTarget as HTMLDivElement).style.background = "transparent";
                        }}
                      >
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <span style={{ color: isActive ? color : "#ccc", fontWeight: isActive ? 600 : 400, fontSize: "13px" }}>
                              {m.display_name}
                            </span>
                            {isActive && (
                              <span style={{ background: color, color: "#fff", fontSize: "9px", borderRadius: "4px", padding: "1px 5px" }}>
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <div style={{ display: "flex", gap: "6px", marginTop: "3px" }}>
                            {m.supports_tools && (
                              <span style={{ color: "#555", fontSize: "9px", border: "1px solid #2a2d35", borderRadius: "3px", padding: "1px 4px" }}>
                                tools
                              </span>
                            )}
                            {m.supports_vision && (
                              <span style={{ color: "#555", fontSize: "9px", border: "1px solid #2a2d35", borderRadius: "3px", padding: "1px 4px" }}>
                                vision
                              </span>
                            )}
                          </div>
                        </div>
                        {m.cost_input_per_1m != null && (
                          <div style={{ color: "#444", fontSize: "10px", textAlign: "right" }}>
                            <div>${m.cost_input_per_1m}/M in</div>
                            <div>${m.cost_output_per_1m}/M out</div>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}

          {/* Footer */}
          <div style={{ padding: "10px 16px", borderTop: "1px solid #1e2028", display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {status?.ollama_available && (
              <span style={{ fontSize: "10px", color: "#4caf50", background: "#4caf5018", borderRadius: "4px", padding: "2px 6px" }}>
                🖥 Ollama ready ({status.ollama_models.length} model{status.ollama_models.length !== 1 ? "s" : ""})
              </span>
            )}
            <span style={{ fontSize: "10px", color: "#555" }}>
              Set by: <span style={{ color: "#888" }}>{session.set_by}</span>
            </span>
            {session.switched_at && (
              <span style={{ fontSize: "10px", color: "#555" }}>
                at {new Date(session.switched_at).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSwitcher;
