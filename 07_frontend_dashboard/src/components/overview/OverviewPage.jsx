import React from 'react';
import { Button } from '../ui/Button';

const MODELS = [
  {
    name: 'OG-Core',
    type: 'Macroeconomic Model',
    color: 'var(--emerald)',
    glow: 'var(--emerald-glow)',
    border: 'var(--emerald-dim)',
    description: 'An overlapping-generations dynamic general equilibrium model that computes long-run trajectories of GDP, wages, capital stock, and interest rates under policy shocks.',
    outputs: ['GDP Growth Rate', 'Real Wage Index', 'Capital Deepening', 'Tax Revenue / GDP'],
  },
  {
    name: 'CLEWS / OSeMOSYS',
    type: 'Resource Systems Model',
    color: 'var(--amber)',
    glow: 'var(--amber-glow)',
    border: 'var(--amber-dim)',
    description: 'A physical systems model simulating the interdependencies of Climate, Land, Energy, and Water resources. Determines feasibility of infrastructure investments under resource constraints.',
    outputs: ['Installed Capacity (GW)', 'Annual CO₂ Emissions', 'System Cost (MUSD)', 'Renewable Share (%)'],
  },
];

const MODULES = [
  { id: '01', name: 'OG-Core Runner',         desc: 'Programmatic execution wrapper with YAML configuration and metadata logging.' },
  { id: '02', name: 'ETL Pipeline',            desc: 'Schema-driven CLEWS-to-OG-Core data translation via declarative YAML mapping.' },
  { id: '03', name: 'Validation Framework',    desc: 'Pre/post-transform integrity checks using pydantic and jsonschema.' },
  { id: '04', name: 'Convergence Prototype',   desc: 'Iterative L2-norm coupling loop that locates a mutually consistent model equilibrium.' },
  { id: '05', name: 'Flask API',               desc: 'Async REST endpoints extending the MUIOGO backend for OG-Core execution.' },
  { id: '06', name: 'Country Scenario',        desc: 'End-to-end renewable transition analysis for the Republic of Mauritius (NDC-aligned).' },
  { id: '07', name: 'Frontend Dashboard',      desc: 'This interface — real-time React control room for convergence orchestration.' },
  { id: '08', name: 'Integration API',         desc: 'FastAPI WebSocket backend streaming live convergence telemetry to the UI.' },
];

const STATS = [
  { value: '2030',    label: 'Program Horizon' },
  { value: 'SIDS',    label: 'Primary Target: Small Island Developing States' },
  { value: 'L2 Norm', label: 'Convergence Metric' },
  { value: '< 1×10⁻⁴', label: 'Convergence Threshold' },
];

export function OverviewPage({ onEnter }) {
  return (
    <div style={{ overflowY: 'auto', flex: 1, padding: '40px 48px', display: 'flex', flexDirection: 'column', gap: 48 }}>

      {/* Hero */}
      <div style={{ maxWidth: 800 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 12px', borderRadius: 20, background: 'var(--emerald-glow)', border: '1px solid var(--emerald-dim)', marginBottom: 20 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--emerald)', animation: 'pulse-dot 1.4s ease-in-out infinite' }} />
          <span style={{ fontSize: 10, color: 'var(--emerald)', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', fontFamily: 'var(--font-mono)' }}>
            UN DESA · Policy Modeling Research · 2026
          </span>
        </div>

        <h1 style={{ fontSize: 38, fontWeight: 300, color: 'var(--text-primary)', letterSpacing: '-0.03em', lineHeight: 1.15, marginBottom: 20 }}>
          OG-CLEWS Integration{' '}
          <span style={{ fontWeight: 600, background: 'linear-gradient(135deg, var(--emerald), var(--blue))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Framework
          </span>
        </h1>

        <p style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.75, maxWidth: 700 }}>
          A soft-linking integration framework bridging two mature open-source policy modeling systems:
          the <strong style={{ color: 'var(--amber)' }}>CLEWS physical resource model</strong> and the{' '}
          <strong style={{ color: 'var(--emerald)' }}>OG-Core macroeconomic DSGE model</strong>. The framework
          enables simultaneous analysis of physical resource feasibility and macroeconomic general equilibrium,
          deployed by the <strong style={{ color: 'var(--text-primary)' }}>United Nations DESA</strong> to
          support evidence-based policy analysis across Small Island Developing States, Least Developed Countries,
          and Land-Locked Developing Countries.
        </p>

        <div style={{ marginTop: 28 }}>
          <Button variant="primary" onClick={onEnter} style={{ padding: '11px 28px', fontSize: 14 }}>
            Open Control Room →
          </Button>
        </div>
      </div>

      {/* Stats bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1, background: 'var(--border-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        {STATS.map(({ value, label }) => (
          <div key={label} style={{ background: 'var(--bg-surface)', padding: '20px 24px' }}>
            <div style={{ fontSize: 22, fontWeight: 300, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', letterSpacing: '-0.02em', marginBottom: 6 }}>{value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{label}</div>
          </div>
        ))}
      </div>

      {/* The two models */}
      <div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 16 }}>Core Scientific Models</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          {MODELS.map(({ name, type, color, glow, border, description, outputs }) => (
            <div key={name} style={{ background: 'var(--bg-surface)', border: `1px solid ${border}`, borderRadius: 'var(--radius-lg)', padding: '24px 26px', boxShadow: `0 0 24px ${glow}` }}>
              <div style={{ fontSize: 10, color, textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 6 }}>{type}</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12, letterSpacing: '-0.01em' }}>{name}</div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: 18 }}>{description}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {outputs.map(o => (
                  <span key={o} style={{ fontSize: 10, padding: '3px 10px', borderRadius: 20, background: `${glow}`, border: `1px solid ${border}`, color, fontFamily: 'var(--font-mono)' }}>{o}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Integration summary */}
      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-muted)', borderRadius: 'var(--radius-lg)', padding: '28px 32px' }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 12 }}>The Integration Problem</div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.8, maxWidth: 820 }}>
          CLEWS and OG-Core have historically operated in complete isolation. CLEWS determines whether a physical energy transition is <em>feasible</em> given land, water, and infrastructure constraints,
          while OG-Core determines whether it is <em>macroeconomically optimal</em> — its impact on long-run GDP, fiscal balances, wages, and capital formation.
          OG-CLEWS establishes an <strong style={{ color: 'var(--text-primary)' }}>iterative soft-linking engine</strong>: CLEWS outputs (capacity, emissions, costs) are translated
          via a declarative ETL schema into OG-Core parameters, which are then used to compute macroeconomic feedback that updates CLEWS boundary conditions.
          This loop repeats until the parameter vector converges under the <strong style={{ color: 'var(--emerald)' }}>L2-norm criterion (Δ &lt; 1×10⁻⁴)</strong>,
          yielding a solution that satisfies both physical and macroeconomic equilibrium simultaneously.
        </p>
      </div>

      {/* Module grid */}
      <div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600, marginBottom: 16 }}>Repository Modules</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          {MODULES.map(({ id, name, desc }) => (
            <div key={id} style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius)', padding: '14px 16px' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: 6 }}>Module {id}</div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6 }}>{name}</div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer attribution */}
      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
          United Nations Office of Information and Communications Technology (UN OICT) · Economic Analysis and Policy Division (UN DESA)
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Apache License 2.0
        </div>
      </div>

    </div>
  );
}
