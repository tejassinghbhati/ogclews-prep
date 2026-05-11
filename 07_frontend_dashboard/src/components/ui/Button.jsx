import React from 'react';

export function Button({ children, onClick, variant = 'primary', loading = false, disabled = false, style = {} }) {
  const base = {
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
    padding: '9px 20px', borderRadius: 'var(--radius)',
    fontFamily: 'var(--font-ui)', fontWeight: 500, fontSize: '13px',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled || loading ? 0.5 : 1,
    border: '1px solid transparent',
    transition: 'all 0.15s ease',
    outline: 'none',
    letterSpacing: '0.01em',
    ...style,
  };

  const styles = {
    primary: { background: 'var(--text-primary)', color: 'var(--bg-base)', borderColor: 'var(--text-primary)' },
    ghost:   { background: 'transparent', color: 'var(--text-secondary)', borderColor: 'var(--border-muted)' },
    danger:  { background: 'var(--red-glow)', color: 'var(--red)', borderColor: 'var(--red-dim)' },
    emerald: { background: 'var(--emerald-glow)', color: 'var(--emerald)', borderColor: 'var(--emerald-dim)' },
  };

  return (
    <button style={{ ...base, ...styles[variant] }} onClick={onClick} disabled={disabled || loading}>
      {loading && (
        <span style={{
          width: 13, height: 13, border: '2px solid currentColor',
          borderTopColor: 'transparent', borderRadius: '50%',
          animation: 'spin 0.6s linear infinite', display: 'inline-block',
        }} />
      )}
      {children}
    </button>
  );
}
