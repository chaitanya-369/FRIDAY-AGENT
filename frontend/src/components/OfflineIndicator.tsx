import React, { useEffect, useState } from "react";

interface OfflineIndicatorProps {
  isOnline: boolean;
  ollamaAvailable: boolean;
  providers: Array<{
    provider_name: string;
    display_name: string;
    healthy_keys: number;
    rate_limited_keys: number;
    auth_failed_keys: number;
    total_keys: number;
  }>;
  onRetry: () => void;
}

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: "#cc785c",
  groq:      "#f55036",
  openai:    "#10a37f",
  gemini:    "#4285f4",
  deepseek:  "#5b6aff",
};

export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({
  isOnline,
  ollamaAvailable,
  providers,
  onRetry,
}) => {
  const [retrying, setRetrying] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [pulse, setPulse] = useState(false);

  // Pulse the offline indicator every 3 seconds when offline
  useEffect(() => {
    if (isOnline) return;
    const interval = setInterval(() => {
      setPulse((v) => !v);
    }, 1500);
    return () => clearInterval(interval);
  }, [isOnline]);

  const handleRetry = async () => {
    setRetrying(true);
    await new Promise((r) => setTimeout(r, 500));
    onRetry();
    setRetrying(false);
  };

  // Don't render when fully online
  if (isOnline) return null;

  const mode = ollamaAvailable ? "local" : "offline";
  const modeColor = ollamaAvailable ? "#4caf50" : "#f44336";
  const modeLabel = ollamaAvailable ? "LOCAL (Ollama)" : "OFFLINE";
  const modeIcon = ollamaAvailable ? "🖥" : "📡";

  const unhealthyProviders = providers.filter(
    (p) => p.healthy_keys === 0
  );

  return (
    <div id="offline-indicator" style={{ position: "relative" }}>
      {/* ── Compact badge ── */}
      <button
        onClick={() => setExpanded((v) => !v)}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          background: `${modeColor}18`,
          border: `1px solid ${modeColor}55`,
          borderRadius: "8px",
          color: modeColor,
          padding: "5px 10px",
          cursor: "pointer",
          fontSize: "12px",
          fontWeight: 600,
          transition: "all 0.3s",
          animation: pulse ? "none" : undefined,
          opacity: pulse ? 0.75 : 1,
        }}
      >
        <span>{modeIcon}</span>
        <span>{modeLabel}</span>
        <span style={{ color: "#666", fontSize: "10px" }}>▾</span>
      </button>

      {/* ── Expanded panel ── */}
      {expanded && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            right: 0,
            width: "340px",
            background: "#111318",
            border: `1px solid ${modeColor}44`,
            borderRadius: "12px",
            boxShadow: `0 20px 60px rgba(0,0,0,0.6), 0 0 20px ${modeColor}22`,
            zIndex: 1000,
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: "12px 16px",
              borderBottom: "1px solid #1e2028",
              background: `${modeColor}0d`,
            }}
          >
            <div style={{ color: modeColor, fontWeight: 700, fontSize: "13px" }}>
              {modeIcon} FRIDAY is in {modeLabel} mode
            </div>
            <div style={{ color: "#666", fontSize: "11px", marginTop: "3px" }}>
              {ollamaAvailable
                ? "Using local Ollama — responses may be slower."
                : "No LLM providers reachable. Diagnostic mode active."}
            </div>
          </div>

          {/* Provider health list */}
          <div style={{ padding: "8px 0" }}>
            {providers.map((p) => {
              const color = PROVIDER_COLORS[p.provider_name] || "#888";
              let statusText = "";
              let statusColor = "";
              if (p.healthy_keys > 0) {
                statusText = `${p.healthy_keys} key(s) healthy`;
                statusColor = "#4caf50";
              } else if (p.rate_limited_keys > 0) {
                statusText = `${p.rate_limited_keys} rate-limited`;
                statusColor = "#ff9800";
              } else if (p.total_keys === 0) {
                statusText = "no keys configured";
                statusColor = "#555";
              } else {
                statusText = "auth error";
                statusColor = "#f44336";
              }

              return (
                <div
                  key={p.provider_name}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "7px 16px",
                    borderBottom: "1px solid #1a1d25",
                  }}
                >
                  <div
                    style={{
                      width: "7px",
                      height: "7px",
                      borderRadius: "50%",
                      background: statusColor,
                      flexShrink: 0,
                    }}
                  />
                  <div style={{ flex: 1 }}>
                    <span style={{ color, fontSize: "12px", fontWeight: 600 }}>
                      {p.display_name}
                    </span>
                  </div>
                  <span style={{ color: statusColor, fontSize: "11px" }}>{statusText}</span>
                </div>
              );
            })}
          </div>

          {/* Actions */}
          <div style={{ padding: "12px 16px", borderTop: "1px solid #1e2028", display: "flex", gap: "8px" }}>
            <button
              id="offline-retry-btn"
              onClick={handleRetry}
              disabled={retrying}
              style={{
                flex: 1,
                background: modeColor,
                border: "none",
                borderRadius: "7px",
                color: "#fff",
                padding: "7px 12px",
                cursor: retrying ? "wait" : "pointer",
                fontWeight: 600,
                fontSize: "12px",
                opacity: retrying ? 0.7 : 1,
                transition: "opacity 0.2s",
              }}
            >
              {retrying ? "Checking…" : "Retry Now"}
            </button>
            <button
              onClick={() => setExpanded(false)}
              style={{
                background: "transparent",
                border: "1px solid #333",
                borderRadius: "7px",
                color: "#888",
                padding: "7px 12px",
                cursor: "pointer",
                fontSize: "12px",
              }}
            >
              Dismiss
            </button>
          </div>

          {/* Help text */}
          <div style={{ padding: "0 16px 12px", color: "#444", fontSize: "10px" }}>
            Add keys via <code style={{ color: "#666" }}>POST /api/keys</code> or the control panel.
            {!ollamaAvailable && (
              <> Install <a href="https://ollama.ai" target="_blank" rel="noreferrer" style={{ color: "#5b6aff" }}>Ollama</a> for local fallback.</>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OfflineIndicator;
