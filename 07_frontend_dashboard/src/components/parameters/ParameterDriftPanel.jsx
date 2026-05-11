import React from 'react';
import { Panel } from '../ui/Panel';

const PARAMS = [
  { key: 'delta_tau', label: 'δ_tau_annual', color: 'var(--emerald)' },
  { key: 'tau_c',     label: 'τ_c',          color: 'var(--amber)'   },
  { key: 'alpha_G',   label: 'α_G',          color: 'var(--blue)'    },
];

export function ParameterDriftPanel({ history }) {
  // Get last two entries to compute per-param drift
  const last  = history.length > 0 ? history[history.length - 1] : null;
  const prev  = history.length > 1 ? history[history.length - 2] : null;

  const drifts = PARAMS.map(({ key, label, color }) => {
    const curr = last?.[key] ?? 0;
    const p    = prev?.[key] ?? curr;
    const maxRef = history.length > 0 ? Math.max(...history.map(h => h[key] ?? 0)) : 1;
    const pct = maxRef > 0 ? Math.min(100, (curr / maxRef) * 100) : 0;
    const delta = curr - p;
    return { label, color, curr, pct, delta };
  });

  return (
    <Panel title="Parameter Drift" style={{ height: '100%' }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
        {drifts.map(({ label, color, curr, pct, delta }) => (
          <div key={label}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>{label}</span>
              <span style={{ fontSize: 11, color, fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                {curr > 0 ? curr.toExponential(3) : '—'}
              </span>
            </div>
            <div style={{ height: 5, background: 'var(--bg-active)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{
                height: '100%', borderRadius: 3,
                width: `${pct}%`, background: color,
                boxShadow: `0 0 8px ${color}80`,
                transition: 'width 0.6s ease',
              }} />
            </div>
            {delta !== 0 && (
              <div style={{ fontSize: 10, color: delta < 0 ? 'var(--emerald)' : 'var(--amber)', marginTop: 3, fontFamily: 'var(--font-mono)' }}>
                {delta < 0 ? '▼' : '▲'} {Math.abs(delta).toExponential(2)}
              </div>
            )}
          </div>
        ))}
        {history.length === 0 && (
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', textAlign: 'center', padding: '10px 0' }}>
            Awaiting iteration data…
          </div>
        )}
      </div>
    </Panel>
  );
}
