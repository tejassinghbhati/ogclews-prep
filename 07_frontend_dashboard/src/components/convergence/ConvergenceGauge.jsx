import React from 'react';
import { Panel } from '../ui/Panel';

function polarToXY(cx, cy, r, angleDeg) {
  const rad = (angleDeg - 90) * (Math.PI / 180);
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const s = polarToXY(cx, cy, r, startAngle);
  const e = polarToXY(cx, cy, r, endAngle);
  const large = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
}

export function ConvergenceGauge({ pct = 0, isConverged = false }) {
  const cx = 80, cy = 80, r = 60;
  const startAngle = -135;
  const totalAngle = 270;
  const fillAngle = startAngle + (totalAngle * Math.min(pct, 100) / 100);

  const trackColor = 'var(--border-muted)';
  const fillColor = isConverged
    ? 'var(--emerald)'
    : pct > 75 ? 'var(--emerald)'
    : pct > 40 ? 'var(--amber)'
    : 'var(--red)';

  return (
    <Panel title="Convergence Progress">
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <svg width={160} height={160} viewBox="0 0 160 160">
          {/* Track */}
          <path d={describeArc(80, 80, r, startAngle, startAngle + totalAngle)}
            fill="none" stroke={trackColor} strokeWidth={8} strokeLinecap="round" />
          {/* Fill */}
          {pct > 0 && (
            <path d={describeArc(80, 80, r, startAngle, fillAngle)}
              fill="none" stroke={fillColor} strokeWidth={8} strokeLinecap="round"
              style={{ transition: 'stroke 0.5s ease' }}
            />
          )}
          {/* Center text */}
          <text x="80" y="76" textAnchor="middle" fill="var(--text-primary)" fontSize="22"
            fontFamily="var(--font-mono)" fontWeight="300">
            {Math.round(pct)}%
          </text>
          <text x="80" y="96" textAnchor="middle" fill="var(--text-muted)" fontSize="10"
            fontFamily="var(--font-ui)" letterSpacing="0.05em">
            {isConverged ? 'CONVERGED' : 'PROGRESS'}
          </text>
        </svg>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[
            { label: 'Status', value: isConverged ? 'Converged ✓' : pct > 0 ? 'Running' : 'Idle', color: isConverged ? 'var(--emerald)' : 'var(--text-primary)' },
            { label: 'Progress', value: `${Math.round(pct)}%`, color: fillColor },
            { label: 'Threshold', value: '1×10⁻⁴', color: 'var(--text-secondary)' },
          ].map(({ label, value, color }) => (
            <div key={label}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 2 }}>{label}</div>
              <div style={{ fontSize: 13, color, fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{value}</div>
            </div>
          ))}
        </div>
      </div>
    </Panel>
  );
}
