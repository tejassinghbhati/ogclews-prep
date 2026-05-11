import React from 'react';
import { LayoutDashboard, Settings, Database, Activity, BarChart3, Cpu, Home } from 'lucide-react';
import { Badge } from '../ui/Badge';

const NAV_ITEMS = [
  { id: 'overview',   label: 'Project Overview',    icon: Home },
  { id: 'workspace',  label: 'Scenario Workspace',  icon: LayoutDashboard },
  { id: 'macro',      label: 'Macro Configuration', icon: Settings },
  { id: 'clews',      label: 'System Constraints',  icon: Database },
  { id: 'telemetry',  label: 'Live Telemetry',       icon: Activity },
  { id: 'results',    label: 'Results Analysis',     icon: BarChart3 },
];

export function Sidebar({ activeTab, onTabChange, systemState, iteration, maxIter }) {
  const wsVariant = systemState === 'running' ? 'active' : systemState === 'error' ? 'error' : 'idle';

  return (
    <nav style={{
      width: 240, background: 'var(--bg-surface)', borderRight: '1px solid var(--border-subtle)',
      display: 'flex', flexDirection: 'column', flexShrink: 0,
    }}>
      {/* Brand */}
      <div style={{ padding: '20px 18px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: 'linear-gradient(135deg, var(--emerald), var(--blue))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Cpu size={14} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
              OG-CLEWS
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 1 }}>
              v1.0 · Control Room
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <div style={{ padding: '10px 8px', flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const isActive = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              style={{
                width: '100%', textAlign: 'left',
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '7px 10px', borderRadius: 'var(--radius)',
                background: isActive ? 'var(--bg-active)' : 'transparent',
                border: 'none',
                borderLeft: isActive ? '2px solid var(--emerald)' : '2px solid transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                fontSize: 12, fontWeight: 500, cursor: 'pointer',
                transition: 'all 0.15s ease',
                fontFamily: 'var(--font-ui)',
              }}
              onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = 'var(--bg-hover)'; e.currentTarget.style.color = 'var(--text-primary)'; }}}
              onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}}
            >
              <Icon size={14} strokeWidth={1.8} />
              {label}
            </button>
          );
        })}
      </div>

      {/* Footer */}
      <div style={{ padding: '14px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: 10 }}>
        {/* Iteration counter */}
        {iteration > 0 && (
          <div style={{ padding: '6px 10px', background: 'var(--bg-active)', borderRadius: 'var(--radius)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>Iteration</span>
            <span style={{ fontSize: 12, color: 'var(--emerald)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
              {iteration} / {maxIter}
            </span>
          </div>
        )}
        {/* API Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 10px', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius)' }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            background: wsVariant === 'active' ? 'var(--emerald)' : wsVariant === 'error' ? 'var(--red)' : '#4a4a58',
            animation: wsVariant === 'active' ? 'pulse-dot 1.4s ease-in-out infinite' : 'none',
            flexShrink: 0,
          }} />
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-primary)', fontWeight: 500 }}>FastAPI Backend</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>localhost:8000</div>
          </div>
        </div>
      </div>
    </nav>
  );
}
