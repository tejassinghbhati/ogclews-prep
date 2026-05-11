import React from 'react';

const LEVEL_STYLES = {
  system:    { color: '#7a7a8a', prefix: 'SYS' },
  iteration: { color: '#f0f0f4', prefix: 'ITR', fontWeight: 700 },
  delta:     { color: '#10b981', prefix: 'Δ  ' },
  converged: { color: '#10b981', prefix: '✓  ', fontWeight: 700, textShadow: '0 0 8px rgba(16,185,129,0.5)' },
  error:     { color: '#ef4444', prefix: 'ERR' },
  warning:   { color: '#f59e0b', prefix: 'WRN' },
  info:      { color: '#7a7a8a', prefix: '···' },
};

export function LogEntry({ timestamp, level, text }) {
  const cfg = LEVEL_STYLES[level] ?? LEVEL_STYLES.info;
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: '80px 36px 1fr',
      gap: 8, padding: '3px 0', alignItems: 'baseline',
      animation: 'fade-in-up 0.2s ease both',
    }}>
      <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
        {timestamp}
      </span>
      <span style={{
        fontSize: 9, fontFamily: 'var(--font-mono)', fontWeight: 700,
        letterSpacing: '0.05em', color: cfg.color,
      }}>
        {cfg.prefix}
      </span>
      <span style={{
        fontSize: 11, fontFamily: 'var(--font-mono)', color: cfg.color,
        fontWeight: cfg.fontWeight ?? 400, textShadow: cfg.textShadow ?? 'none',
        wordBreak: 'break-all',
      }}>
        {text}
      </span>
    </div>
  );
}
