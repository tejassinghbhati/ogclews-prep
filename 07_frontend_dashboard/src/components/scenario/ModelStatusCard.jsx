import React from 'react';
import { Badge } from '../ui/Badge';
import { DataKPI } from '../ui/DataKPI';

export function ModelStatusCard({ title, model, status, kpis, glowColor }) {
  const glowMap = { emerald: 'var(--glow-emerald)', amber: 'var(--glow-amber)', blue: 'var(--glow-blue)', red: 'var(--glow-red)' };
  const isActive = status === 'running' || status === 'active';

  return (
    <div style={{
      background: 'var(--bg-surface)', border: '1px solid var(--border-muted)',
      borderRadius: 'var(--radius-lg)', padding: '18px 20px',
      display: 'flex', flexDirection: 'column', gap: 16,
      boxShadow: isActive ? (glowMap[glowColor] ?? 'none') : 'none',
      transition: 'box-shadow 0.4s ease',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4 }}>
            {model}
          </div>
          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            {title}
          </div>
        </div>
        <Badge variant={status} pulse={isActive} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {kpis.map((kpi, i) => (
          <DataKPI key={i} label={kpi.label} value={kpi.value} unit={kpi.unit} trend={kpi.trend} color={kpi.color} size="sm" />
        ))}
      </div>
    </div>
  );
}
