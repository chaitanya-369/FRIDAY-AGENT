import { useCallback, useEffect, useState } from 'react'
import { Excalidraw } from '@excalidraw/excalidraw'
import FridayUI from './components/FridayUI'
import { ModelSwitcher } from './components/ModelSwitcher'
import { OfflineIndicator } from './components/OfflineIndicator'
import './App.css'

const API = 'http://localhost:8000'

// ── Types ──────────────────────────────────────────────────────────────────────

interface SessionState {
  provider_name: string
  model_id: string
  set_by: string
  reason: string
  switched_at: string | null
  switch_history: Array<{
    provider_name: string
    model_id: string
    set_by: string
    reason: string
    switched_at: string
  }>
}

interface StatusState {
  is_online: boolean
  ollama_available: boolean
  ollama_models: string[]
  providers: Array<{
    provider_name: string
    display_name: string
    healthy_keys: number
    rate_limited_keys: number
    auth_failed_keys: number
    total_keys: number
  }>
}

// ── App ────────────────────────────────────────────────────────────────────────

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'hud' | 'whiteboard'>('dashboard')
  const [session, setSession] = useState<SessionState | null>(null)
  const [status, setStatus] = useState<StatusState | null>(null)

  const refreshSession = useCallback(async () => {
    try {
      const [sessionRes, statusRes] = await Promise.all([
        fetch(`${API}/api/session`),
        fetch(`${API}/api/session/status`),
      ])
      if (sessionRes.ok) setSession(await sessionRes.json())
      if (statusRes.ok) setStatus(await statusRes.json())
    } catch {
      // Backend not running — silent fail
    }
  }, [])

  // Load on mount and poll every 30s
  useEffect(() => {
    refreshSession()
    const interval = setInterval(refreshSession, 30_000)
    return () => clearInterval(interval)
  }, [refreshSession])

  return (
    <div style={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column', background: '#0d0f14' }}>
      {/* ── Header ── */}
      <header style={{
        padding: '0.6rem 1.2rem',
        backgroundColor: '#111318',
        borderBottom: '1px solid #1e2028',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '0.08em', color: '#fff' }}>
            FRIDAY
          </span>
          <span style={{ fontSize: '11px', color: '#3a3f50', fontWeight: 500 }}>
            Agent v1
          </span>
        </div>

        {/* Tab navigation */}
        <div style={{ display: 'flex', gap: '4px' }}>
          {(['dashboard', 'hud', 'whiteboard'] as const).map((tab) => (
            <button
              key={tab}
              id={`tab-${tab}`}
              onClick={() => setActiveTab(tab)}
              style={{
                background: activeTab === tab ? 'rgba(255,255,255,0.08)' : 'transparent',
                border: '1px solid',
                borderColor: activeTab === tab ? '#2a2d35' : 'transparent',
                color: activeTab === tab ? '#fff' : '#666',
                padding: '5px 14px',
                cursor: 'pointer',
                borderRadius: '7px',
                fontSize: '12px',
                fontWeight: activeTab === tab ? 600 : 400,
                transition: 'all 0.2s',
                textTransform: 'capitalize',
              }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Spacer */}
        <div style={{ flex: 1 }} />

        {/* ── HUD Widgets ── */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Offline indicator — only shows when offline */}
          {status && (
            <OfflineIndicator
              isOnline={status.is_online}
              ollamaAvailable={status.ollama_available}
              providers={status.providers}
              onRetry={refreshSession}
            />
          )}

          {/* Model switcher badge + panel */}
          <ModelSwitcher
            session={session}
            status={status}
            onSwitch={refreshSession}
          />
        </div>
      </header>

      {/* ── Main content ── */}
      <main style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {activeTab === 'dashboard' ? (
          <div style={{ padding: '2.5rem', maxWidth: '900px', margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }}>
              <h1 style={{ color: '#fff', margin: 0, fontSize: '28px', fontWeight: 800 }}>
                FRIDAY Control Center
              </h1>
              <p style={{ color: '#555', marginTop: '6px', fontSize: '13px' }}>
                Female Replacement Intelligent Digital Assistant Youth
              </p>
            </div>

            {/* Session status card */}
            {session && (
              <div style={{
                background: '#111318',
                border: '1px solid #1e2028',
                borderRadius: '12px',
                padding: '20px 24px',
                marginBottom: '16px',
              }}>
                <div style={{ color: '#888', fontSize: '11px', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                  Active Model Session
                </div>
                <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
                  <div>
                    <div style={{ color: '#555', fontSize: '11px' }}>Provider</div>
                    <div style={{ color: '#fff', fontWeight: 600, marginTop: '2px' }}>
                      {session.provider_name.charAt(0).toUpperCase() + session.provider_name.slice(1)}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#555', fontSize: '11px' }}>Model</div>
                    <div style={{ color: '#fff', fontWeight: 600, marginTop: '2px', fontFamily: 'monospace', fontSize: '13px' }}>
                      {session.model_id}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#555', fontSize: '11px' }}>Set By</div>
                    <div style={{ color: '#aaa', marginTop: '2px', fontSize: '13px' }}>
                      {session.set_by}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#555', fontSize: '11px' }}>Status</div>
                    <div style={{ marginTop: '2px', fontSize: '13px' }}>
                      {status?.is_online
                        ? <span style={{ color: '#4caf50' }}>● Online</span>
                        : status?.ollama_available
                          ? <span style={{ color: '#ff9800' }}>● Local (Ollama)</span>
                          : <span style={{ color: '#f44336' }}>● Offline</span>
                      }
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Quick tip */}
            <div style={{
              background: '#0d1117',
              border: '1px solid #1e2028',
              borderRadius: '10px',
              padding: '14px 18px',
              fontSize: '12px',
              color: '#555',
              lineHeight: '1.6',
            }}>
              <span style={{ color: '#888', fontWeight: 600 }}>Tip:</span>{' '}
              Say <code style={{ color: '#7c6aff', background: '#1a1425', borderRadius: '4px', padding: '1px 5px' }}>"switch to GPT-4o"</code>{' '}
              or <code style={{ color: '#7c6aff', background: '#1a1425', borderRadius: '4px', padding: '1px 5px' }}>"use groq llama"</code>{' '}
              in chat to switch models instantly. Press{' '}
              <code style={{ color: '#7c6aff', background: '#1a1425', borderRadius: '4px', padding: '1px 5px' }}>Ctrl+Shift+M</code>{' '}
              to open the model panel.
            </div>
          </div>
        ) : activeTab === 'hud' ? (
          <FridayUI />
        ) : (
          <Excalidraw />
        )}
      </main>
    </div>
  )
}

export default App
