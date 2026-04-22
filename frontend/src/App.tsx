import { useState } from 'react'
import { Excalidraw } from '@excalidraw/excalidraw'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'whiteboard'>('dashboard')

  return (
    <div style={{ height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', backgroundColor: '#1e1e1e', color: 'white', display: 'flex', gap: '1rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>FRIDAY Agent</h1>
        <button 
          onClick={() => setActiveTab('dashboard')}
          style={{ background: activeTab === 'dashboard' ? '#333' : 'transparent', border: '1px solid #555', color: 'white', padding: '0.5rem 1rem', cursor: 'pointer' }}
        >
          Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('whiteboard')}
          style={{ background: activeTab === 'whiteboard' ? '#333' : 'transparent', border: '1px solid #555', color: 'white', padding: '0.5rem 1rem', cursor: 'pointer' }}
        >
          Whiteboard (Excalidraw)
        </button>
      </header>
      
      <main style={{ flex: 1, position: 'relative' }}>
        {activeTab === 'dashboard' ? (
          <div style={{ padding: '2rem' }}>
            <h2>FRIDAY Control Center</h2>
            <p>Welcome to the FRIDAY Agent development frontend.</p>
            {/* Repo visualizer component can go here */}
          </div>
        ) : (
          <Excalidraw />
        )}
      </main>
    </div>
  )
}

export default App
