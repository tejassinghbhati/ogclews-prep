import React, { useRef, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, Legend, ResponsiveContainer,
} from 'recharts';
import { Panel } from '../ui/Panel';
import { CONVERGENCE_EPSILON } from '../../constants/modelConstants';

// Mock data so chart is never empty during dev/demo
const MOCK = Array.from({ length: 8 }, (_, i) => ({
  iter: i + 1,
  delta_tau: +(0.048 / Math.pow(2.1, i)).toFixed(6),
  tau_c:     +(0.009 / Math.pow(1.8, i)).toFixed(6),
  alpha_G:   +(0.023 / Math.pow(2.3, i)).toFixed(6),
}));

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'var(--bg-elevated)', border: '1px solid var(--border-muted)',
      borderRadius: 'var(--radius)', padding: '10px 14px',
      fontSize: 11, fontFamily: 'var(--font-mono)',
    }}>
      <div style={{ color: 'var(--text-secondary)', marginBottom: 6 }}>Iteration {label}</div>
      {payload.map(p => (
        <div key={p.dataKey} style={{ color: p.color, marginBottom: 3 }}>
          {p.dataKey}: {p.value?.toExponential(4)}
        </div>
      ))}
    </div>
  );
};

export function ConvergenceChart({ history }) {
  const data = history?.length > 0
    ? history.map(h => ({ iter: h.iter, delta_tau: h.delta_tau, tau_c: h.tau_c, alpha_G: h.alpha_G }))
    : MOCK;

  return (
    <Panel title="Convergence Trajectory" style={{ height: '100%' }}>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
            <XAxis
              dataKey="iter" tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
              label={{ value: 'Iteration', position: 'insideBottom', offset: -2, fontSize: 10, fill: 'var(--text-muted)' }}
              stroke="var(--border-muted)"
            />
            <YAxis
              scale="log" domain={['auto', 'auto']}
              tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}
              stroke="var(--border-muted)"
              tickFormatter={v => v.toExponential(0)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              iconType="plainline" iconSize={14}
              wrapperStyle={{ fontSize: 11, fontFamily: 'var(--font-mono)', paddingTop: 6 }}
            />
            <ReferenceLine
              y={CONVERGENCE_EPSILON} stroke="var(--emerald)"
              strokeDasharray="6 3" label={{ value: 'ε threshold', fill: 'var(--emerald)', fontSize: 10, position: 'right' }}
            />
            <Line type="monotone" dataKey="delta_tau" stroke="#10b981" strokeWidth={1.5} dot={false} name="delta_tau" />
            <Line type="monotone" dataKey="tau_c"     stroke="#f59e0b" strokeWidth={1.5} dot={false} name="tau_c" />
            <Line type="monotone" dataKey="alpha_G"   stroke="#3b82f6" strokeWidth={1.5} dot={false} name="alpha_G" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}
