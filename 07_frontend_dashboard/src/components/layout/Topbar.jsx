import React from 'react';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

const TAB_META = {
  overview:   { title: 'Project Overview',     subtitle: 'OG-CLEWS Integration Framework · UN DESA Policy Modeling Research.' },
  workspace:  { title: 'Scenario Workspace',   subtitle: 'Orchestrate and monitor the OG-CLEWS iterative coupling loop.' },
  macro:      { title: 'Macro Configuration',  subtitle: 'Configure OG-Core household, fiscal, and solver parameters.' },
  clews:      { title: 'System Constraints',   subtitle: 'Define CLEWS/OSeMOSYS energy, emissions, water, and land bounds.' },
  telemetry:  { title: 'Live Telemetry',        subtitle: 'Real-time stream of convergence loop execution logs.' },
  results:    { title: 'Results Analysis',      subtitle: 'Post-convergence macroeconomic indicators and parameter history.' },
};

const STATE_BADGE = {
  idle:      'idle',
  running:   'running',
  converged: 'converged',
  error:     'error',
};

export function Topbar({ activeTab, systemState, iteration, maxIter, currentDelta, onRun, onAbort }) {
  const meta = TAB_META[activeTab] ?? TAB_META.workspace;
  const isRunning = systemState === 'running';
  const deltaStr = currentDelta != null ? currentDelta.toExponential(4) : '—';

  return (
    <header style={{
      padding: '18px 28px',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
      gap: 24, flexShrink: 0,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
          <h1 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            {meta.title}
          </h1>
          <Badge variant={STATE_BADGE[systemState] ?? 'idle'} pulse />
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, maxWidth: 640 }}>
          {meta.subtitle}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        {/* Delta display */}
        {(isRunning || systemState === 'converged') && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 3 }}>L2 Norm Δ</div>
            <div style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--emerald)', fontWeight: 500 }}>
              {deltaStr}
            </div>
          </div>
        )}
        {/* Iteration counter */}
        {isRunning && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 3 }}>Iteration</div>
            <div style={{ fontSize: 14, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 500 }}>
              {iteration} <span style={{ color: 'var(--text-muted)' }}>/ {maxIter}</span>
            </div>
          </div>
        )}
        {/* Run / Abort button */}
        {isRunning ? (
          <Button variant="danger" onClick={onAbort}>Abort Run</Button>
        ) : (
          <Button
            variant="primary"
            onClick={onRun}
            disabled={activeTab !== 'workspace' && systemState !== 'idle'}
            loading={systemState === 'running'}
          >
            Initialize Runtime
          </Button>
        )}
      </div>
    </header>
  );
}
