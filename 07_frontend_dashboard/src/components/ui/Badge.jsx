import React from 'react';

const VARIANTS = {
  active:    { dot: '#10b981', bg: 'rgba(16,185,129,0.12)',  text: '#10b981', label: 'ACTIVE'    },
  running:   { dot: '#10b981', bg: 'rgba(16,185,129,0.12)',  text: '#10b981', label: 'RUNNING'   },
  idle:      { dot: '#4a4a58', bg: 'rgba(74,74,88,0.2)',     text: '#7a7a8a', label: 'IDLE'      },
  standby:   { dot: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  text: '#f59e0b', label: 'STANDBY'   },
  error:     { dot: '#ef4444', bg: 'rgba(239,68,68,0.12)',   text: '#ef4444', label: 'ERROR'     },
  converged: { dot: '#10b981', bg: 'rgba(16,185,129,0.15)',  text: '#10b981', label: 'CONVERGED' },
  warning:   { dot: '#f59e0b', bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', label: 'WARNING'   },
};

export function Badge({ variant = 'idle', label, pulse = false }) {
  const cfg = VARIANTS[variant] ?? VARIANTS.idle;
  const text = label ?? cfg.label;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '6px',
      padding: '2px 8px', borderRadius: '3px',
      background: cfg.bg, color: cfg.text,
      fontSize: '10px', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase',
      fontFamily: 'var(--font-mono)',
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: '50%',
        background: cfg.dot, flexShrink: 0,
        animation: (pulse && (variant === 'active' || variant === 'running'))
          ? 'pulse-dot 1.4s ease-in-out infinite' : 'none',
      }} />
      {text}
    </span>
  );
}
