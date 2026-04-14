import React, { useState } from 'react';
import './index.css';

function App() {
  const [isRunning, setIsRunning] = useState(false);
  const [iteration, setIteration] = useState(0);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('Scenario Workspace');

  const tabs = ['Scenario Workspace', 'Macro Configuration', 'System Constraints'];

  const handleRunConvergence = () => {
    setIsRunning(true);
    setIteration(0);
    setLogs([]);
    
    const ws = new WebSocket('ws://localhost:8000/ws/convergence');
    
    ws.onmessage = (event) => {
      const msg = event.data;
      setLogs(prev => [...prev, msg].slice(-15));
      
      if (msg.includes('── Iteration')) {
        const match = msg.match(/Iteration (\d+)/);
        if (match) {
          setIteration(parseInt(match[1], 10));
        }
      }
      
      if (msg.includes('[SYSTEM] Convergence loop finished')) {
        setIsRunning(false);
      }
    };
    
    ws.onclose = () => {
      setIsRunning(false);
    };
    
    ws.onerror = (error) => {
      console.error(error);
      setIsRunning(false);
    };
  };

  const renderContent = () => {
    if (activeTab === 'Macro Configuration') {
      return (
        <div className="workspace-grid" style={{ padding: '32px' }}>
          <div className="panel" style={{ gridColumn: '1 / -1' }}>
            <div className="panel-header">OG-Core Configuration Editor</div>
            <div className="panel-body">
              <p className="text-subtle text-sm">Advanced configuration environment for macroeconomic boundaries.</p>
              <div className="text-subtle text-xs monospace" style={{ marginTop: '20px', padding: '16px', border: '1px dashed var(--border-subtle)' }}>
                // TODO: Component integration for advanced_og_parameters.json
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    if (activeTab === 'System Constraints') {
      return (
        <div className="workspace-grid" style={{ padding: '32px' }}>
          <div className="panel" style={{ gridColumn: '1 / -1' }}>
            <div className="panel-header">CLEWS System Bounds</div>
            <div className="panel-body">
              <p className="text-subtle text-sm">Resource capacity constraints and technical definitions.</p>
              <div className="text-subtle text-xs monospace" style={{ marginTop: '20px', padding: '16px', border: '1px dashed var(--border-subtle)' }}>
                // TODO: Component integration for OSeMOSYS technical bounds UI
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
        <section className="workspace-grid">
          {/* Macro Panel */}
          <div className="panel">
            <div className="panel-header">
              Macroeconomic Module [OG-Core]
            </div>
            <div className="panel-body">
              <div className="data-display">
                <div className="form-label">Total Factor Productivity</div>
                <div className="data-value">{isRunning ? (1.084 + Math.random() * 0.005).toFixed(4) : '1.0840'}</div>
              </div>
              
              <div className="form-group">
                <label className="form-label">Base Tax Rate (%)</label>
                <input type="number" className="form-input" defaultValue="21.0" step="0.1" />
              </div>
              <div className="form-group">
                <label className="form-label">Budget Closure Protocol</label>
                <select className="form-select" defaultValue="debt">
                  <option value="debt">Unrestricted Debt</option>
                  <option value="tax">Tax Revenue Supported</option>
                  <option value="mixed">Mixed Optimization</option>
                </select>
              </div>
            </div>
          </div>

          {/* Resource Panel */}
          <div className="panel">
            <div className="panel-header">
              Resource Systems [CLEWS]
            </div>
            <div className="panel-body">
              <div className="data-display">
                <div className="form-label">Discounted System Cost (USD M)</div>
                <div className="data-value">{isRunning ? (254.2 + (iteration * 1.5)).toFixed(2) : '254.20'}</div>
              </div>
              
              <div className="form-group">
                <label className="form-label">Emission Penalty (USD/Ton)</label>
                <input type="number" className="form-input" defaultValue="45.00" step="1.00" />
              </div>
              <div className="form-group">
                <label className="form-label">Grid Renewables Bound (%)</label>
                <input type="number" className="form-input" defaultValue="60.0" step="0.5" />
              </div>
            </div>
          </div>

          {/* Telemetry Panel */}
          <div className="panel" style={{ gridColumn: '1 / -1' }}>
            <div className="panel-header">
              Live Telemetry Stream
            </div>
            <div className="panel-body" style={{ minHeight: '160px', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-base)', borderTop: '1px solid var(--border-subtle)', overflowY: 'auto' }}>
              {logs.length > 0 ? (
                <div className="text-sm text-subtle monospace" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {logs.map((log, idx) => (
                    <span key={idx} style={{ color: log.includes('delta') ? 'var(--status-active)' : log.includes('Iteration') ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                      {log}
                    </span>
                  ))}
                </div>
              ) : (
                <div className="text-subtle text-sm monospace" style={{ margin: 'auto' }}>
                  System idle. Variables pending dispatch.
                </div>
              )}
            </div>
          </div>
        </section>
    );
  };

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2 className="text-lg text-primary">OG-CLEWS Engine</h2>
          <p className="text-subtle text-xs" style={{ marginTop: '4px' }}>v1.0 Integration Controller</p>
        </div>
        
        <div className="nav-links">
          {tabs.map(tab => (
            <div 
              key={tab} 
              className={`nav-item ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </div>
          ))}
        </div>
        
        <div className="sidebar-footer">
          <div className="status-box">
            <div className="dot"></div>
            <div>
              <div className="text-sm">API Connected</div>
              <div className="text-xs text-subtle monospace">localhost:8000</div>
            </div>
          </div>
        </div>
      </nav>

      <main className="main-area">
        <header className="topbar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'flex-start' }}>
            <div style={{ maxWidth: '800px' }}>
              <h1 className="text-lg">OG-CLEWS Soft-Linking Operations</h1>
              <p className="text-subtle text-sm" style={{ marginTop: '12px', lineHeight: '1.6' }}>
                This console orchestrates the iterative mathematical convergence between the <strong>OSeMOSYS physical energy architecture</strong> and the <strong>OG-Core macroeconomic DSGE model</strong>. 
                Ensure boundaries are strictly configured before dispatching parameters. Upon initialization, the system actively monitors and converges the bilateral feedback loop connecting energy constraints, capital stock, and total factor productivity.
              </p>
            </div>
            
            <button 
              className="btn btn-primary flex-center" 
              onClick={handleRunConvergence}
              disabled={isRunning || activeTab !== 'Scenario Workspace'}
              style={{ flexShrink: 0, padding: '10px 24px', marginLeft: '32px' }}
            >
              {isRunning ? (
                <>
                  <span className="spinner"></span>
                  Computing ({iteration})
                </>
              ) : (
                "Initialize Runtime"
              )}
            </button>
          </div>
        </header>

        {renderContent()}
        
      </main>
    </div>
  );
}

export default App;
