import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { Panel } from '../ui/Panel';
import { DataKPI } from '../ui/DataKPI';

const MAURITIUS_DATA = [
  { indicator: 'GDP Growth', baseline: 3.80, scenario: 4.06, unit: '%' },
  { indicator: 'Capital Share', baseline: 0.380, scenario: 0.386, unit: '' },
  { indicator: 'Wage Index', baseline: 1.000, scenario: 1.065, unit: '' },
  { indicator: 'Interest Rate', baseline: 4.20, scenario: 4.08, unit: '%' },
  { indicator: 'Tax Revenue / GDP', baseline: 19.2, scenario: 21.6, unit: '%' },
];

const CHART_TOOLTIP = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-muted)', borderRadius: 6, padding: '8px 12px', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
      <div style={{ color: 'var(--text-secondary)', marginBottom: 4 }}>{label}</div>
      {payload.map(p => (
        <div key={p.name} style={{ color: p.color }}>{p.name}: {p.value}</div>
      ))}
    </div>
  );
};

export function ResultsPanel({ isConverged }) {
  return (
    <div style={{ padding: 24, overflowY: 'auto', flex: 1 }}>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Results Analysis</h2>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
          Post-convergence macroeconomic outcomes — Republic of Mauritius renewable transition scenario.
        </p>
      </div>

      {/* KPI summary strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 16, marginBottom: 24 }}>
        {[
          { label: 'GDP Growth Δ', value: '+0.26pp', color: 'var(--emerald)', trend: 0.26 },
          { label: 'Wage Index',    value: '+6.5%',   color: 'var(--emerald)', trend: 6.5  },
          { label: 'Tax Base Δ',   value: '+2.4pp',   color: 'var(--emerald)', trend: 2.4  },
          { label: 'CO₂ Reduction', value: '−83%',   color: 'var(--amber)',   trend: -83  },
          { label: 'Interest Rate Δ', value: '−0.12pp', color: 'var(--blue)', trend: -0.12 },
        ].map(kpi => (
          <div key={kpi.label} style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-muted)', borderRadius: 'var(--radius-lg)', padding: '14px 16px' }}>
            <DataKPI label={kpi.label} value={kpi.value} color={kpi.color} trend={kpi.trend} size="sm" />
          </div>
        ))}
      </div>

      {/* Comparison bar chart */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20 }}>
        <Panel title="Baseline vs. Renewable Transition Scenario">
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MAURITIUS_DATA} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="indicator" tick={{ fontSize: 9, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} stroke="var(--border-muted)" />
                <YAxis tick={{ fontSize: 10, fill: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }} stroke="var(--border-muted)" />
                <Tooltip content={<CHART_TOOLTIP />} />
                <Legend iconSize={10} wrapperStyle={{ fontSize: 11, fontFamily: 'var(--font-mono)' }} />
                <Bar dataKey="baseline" name="Baseline" fill="#3b82f6" radius={[2,2,0,0]} />
                <Bar dataKey="scenario" name="RE Transition" fill="#10b981" radius={[2,2,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
        <Panel title="Detailed Outcomes Table">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11, fontFamily: 'var(--font-mono)' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '5px 8px', textAlign: 'left', color: 'var(--text-muted)', fontSize: 10, fontWeight: 500 }}>Indicator</th>
                <th style={{ padding: '5px 8px', color: 'var(--blue)', fontSize: 10, fontWeight: 500 }}>Base</th>
                <th style={{ padding: '5px 8px', color: 'var(--emerald)', fontSize: 10, fontWeight: 500 }}>Scenario</th>
                <th style={{ padding: '5px 8px', color: 'var(--text-muted)', fontSize: 10, fontWeight: 500 }}>Δ</th>
              </tr>
            </thead>
            <tbody>
              {MAURITIUS_DATA.map(row => {
                const delta = (row.scenario - row.baseline).toFixed(3);
                const pos = +delta > 0;
                return (
                  <tr key={row.indicator} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '6px 8px', color: 'var(--text-secondary)' }}>{row.indicator}</td>
                    <td style={{ padding: '6px 8px', textAlign: 'center', color: 'var(--blue)' }}>{row.baseline}</td>
                    <td style={{ padding: '6px 8px', textAlign: 'center', color: 'var(--emerald)' }}>{row.scenario}</td>
                    <td style={{ padding: '6px 8px', textAlign: 'center', color: pos ? 'var(--emerald)' : 'var(--amber)' }}>
                      {pos ? '+' : ''}{delta}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Panel>
      </div>
    </div>
  );
}
