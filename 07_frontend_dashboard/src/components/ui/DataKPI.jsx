import React from 'react';

export function DataKPI({ label, value, unit, trend, color = 'var(--text-primary)', size = 'md' }) {
  const fontSize = size === 'lg' ? '36px' : size === 'sm' ? '20px' : '28px';
  const trendColor = trend > 0 ? 'var(--emerald)' : trend < 0 ? 'var(--red)' : 'var(--text-secondary)';
  const trendArrow = trend > 0 ? '↑' : trend < 0 ? '↓' : '—';
  const trendAbs = trend != null ? Math.abs(trend) : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
        <span style={{ fontSize, fontWeight: 300, color, letterSpacing: '-0.03em', fontVariantNumeric: 'tabular-nums', fontFamily: 'var(--font-mono)' }}>
          {value}
        </span>
        {unit && (
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 400 }}>{unit}</span>
        )}
        {trend != null && (
          <span style={{ fontSize: '12px', color: trendColor, fontWeight: 500 }}>
            {trendArrow} {trendAbs != null ? trendAbs.toFixed(2) : ''}
          </span>
        )}
      </div>
    </div>
  );
}
