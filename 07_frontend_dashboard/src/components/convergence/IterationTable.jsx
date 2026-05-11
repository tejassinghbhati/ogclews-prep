import React from 'react';
import { Panel } from '../ui/Panel';
import { Badge } from '../ui/Badge';

const COL_STYLE = { fontSize: 11, fontFamily: 'var(--font-mono)', padding: '7px 12px', textAlign: 'right' };
const HEAD_STYLE = { fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', padding: '7px 12px', textAlign: 'right', fontFamily: 'var(--font-ui)' };

export function IterationTable({ history, epsilon }) {
  const rows = history.length > 0 ? history : [];

  return (
    <Panel title="Iteration History" style={{ height: '100%' }}>
      <div style={{ overflowY: 'auto', maxHeight: 220 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
              <th style={{ ...HEAD_STYLE, textAlign: 'left' }}>Iter</th>
              <th style={HEAD_STYLE}>δ_tau</th>
              <th style={HEAD_STYLE}>τ_c</th>
              <th style={HEAD_STYLE}>α_G</th>
              <th style={HEAD_STYLE}>L2 Norm</th>
              <th style={{ ...HEAD_STYLE, textAlign: 'left' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '20px 12px', fontSize: 11, color: 'var(--text-muted)', textAlign: 'center', fontFamily: 'var(--font-mono)' }}>
                  No iteration data. Awaiting runtime.
                </td>
              </tr>
            ) : rows.map((row, i) => {
              const converged = row.l2norm != null && row.l2norm < (epsilon ?? 1e-4);
              return (
                <tr key={i} style={{
                  borderBottom: '1px solid var(--border-subtle)',
                  background: converged ? 'var(--emerald-glow)' : 'transparent',
                  animation: 'fade-in-up 0.3s ease both',
                }}>
                  <td style={{ ...COL_STYLE, textAlign: 'left', color: 'var(--text-secondary)' }}>{row.iter}</td>
                  <td style={{ ...COL_STYLE, color: 'var(--emerald)' }}>{row.delta_tau?.toExponential(3) ?? '—'}</td>
                  <td style={{ ...COL_STYLE, color: 'var(--amber)'  }}>{row.tau_c?.toExponential(3) ?? '—'}</td>
                  <td style={{ ...COL_STYLE, color: 'var(--blue)'   }}>{row.alpha_G?.toExponential(3) ?? '—'}</td>
                  <td style={{ ...COL_STYLE, color: 'var(--text-primary)', fontWeight: 600 }}>{row.l2norm?.toExponential(3) ?? '—'}</td>
                  <td style={{ ...COL_STYLE, textAlign: 'left' }}>
                    <Badge variant={converged ? 'converged' : 'running'} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
