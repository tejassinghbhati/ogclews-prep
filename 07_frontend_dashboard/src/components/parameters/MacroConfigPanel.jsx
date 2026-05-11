import React from 'react';
import { Panel } from '../ui/Panel';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

function SectionHeader({ label }) {
  return (
    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, padding: '10px 0 4px', borderBottom: '1px solid var(--border-subtle)', marginBottom: 12 }}>
      {label}
    </div>
  );
}

function ParamRow({ paramKey, def, onChange }) {
  const { value, label, unit, description, min, max, step, options, readOnly } = def;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, alignItems: 'start', paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
      <div>
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', marginBottom: 2 }}>{label}</div>
        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{description}</div>
        {unit && <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>Unit: {unit}</div>}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {readOnly ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 13, fontFamily: 'var(--font-mono)', color: 'var(--emerald)', fontWeight: 600 }}>{value}</span>
            <Badge variant="active" label="ETL Injected" />
          </div>
        ) : options ? (
          <select
            value={value}
            onChange={e => onChange(paramKey, isNaN(e.target.value) ? e.target.value : +e.target.value)}
            style={{ background: 'var(--bg-base)', border: '1px solid var(--border-muted)', color: 'var(--text-primary)', padding: '5px 8px', borderRadius: 'var(--radius-sm)', fontSize: 12, fontFamily: 'var(--font-mono)', outline: 'none' }}
          >
            {options.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        ) : (
          <>
            <input
              type="range" min={min} max={max} step={step ?? 1} value={value}
              onChange={e => onChange(paramKey, +e.target.value)}
              style={{ accentColor: 'var(--emerald)', width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <input
                type="number" min={min} max={max} step={step ?? 1} value={value}
                onChange={e => onChange(paramKey, +e.target.value)}
                style={{ background: 'var(--bg-base)', border: '1px solid var(--border-muted)', color: 'var(--text-primary)', padding: '4px 8px', borderRadius: 'var(--radius-sm)', fontSize: 12, fontFamily: 'var(--font-mono)', outline: 'none', width: 100 }}
              />
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>[{min}, {max}]</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export function MacroConfigPanel({ params, onUpdate, onReset }) {
  const sections = [
    { label: 'Household Demographics', keys: ['S', 'J', 'lambdas'] },
    { label: 'Fiscal Policy',          keys: ['tau_b', 'tau_payroll', 'alpha_G', 'budget_closure'] },
    { label: 'Economic Parameters',    keys: ['delta', 'sigma', 'delta_tau_annual'] },
    { label: 'Solver Settings',        keys: ['T_S', 'maxiter', 'nu'] },
  ];

  return (
    <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h2 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>OG-Core Parameters</h2>
          <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>Configure macroeconomic household, fiscal, and solver specifications.</p>
        </div>
        <Button variant="ghost" onClick={onReset}>Reset to Defaults</Button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {sections.map(({ label, keys }) => (
          <Panel key={label} title={label}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {keys.map(k => params[k] ? (
                <ParamRow key={k} paramKey={k} def={params[k]} onChange={onUpdate} />
              ) : null)}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
