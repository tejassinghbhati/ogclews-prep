import React from 'react';
import { ModelStatusCard } from './ModelStatusCard';
import { ConvergenceChart } from '../convergence/ConvergenceChart';
import { ConvergenceGauge } from '../convergence/ConvergenceGauge';
import { IterationTable } from '../convergence/IterationTable';
import { ETLFlowVisualizer } from './ETLFlowVisualizer';
import { ParameterDriftPanel } from '../parameters/ParameterDriftPanel';
import { TelemetryStream } from '../telemetry/TelemetryStream';

export function ScenarioWorkspace({ systemState, convergence, messages }) {
  const { iteration, history, currentDelta, isConverged, convergencePct, maxIter, epsilon } = convergence;
  const isRunning = systemState === 'running';

  const ogStatus  = isRunning ? 'running'  : isConverged ? 'converged' : 'idle';
  const clewsStatus = isRunning ? 'standby' : isConverged ? 'converged' : 'idle';

  const tfp = isRunning ? (1.084 + iteration * 0.0003).toFixed(4) : '1.0840';
  const gdpDelta = isRunning ? +(0.26 + iteration * 0.004).toFixed(3) : 0.260;
  const sysCost  = isRunning ? (254.2 + iteration * 1.5).toFixed(1) : '254.2';
  const co2Proj  = isRunning ? (0.547 + iteration * 0.002).toFixed(3) : '0.547';

  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20, overflowY: 'auto', flex: 1 }}>

      {/* Row 1: Model status cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16 }}>
        <ModelStatusCard
          title="OG-Core"
          model="Macroeconomic Model"
          status={ogStatus}
          glowColor="emerald"
          kpis={[
            { label: 'TFP', value: tfp, unit: '', trend: isRunning ? 0.0003 : 0 },
            { label: 'GDP Δ', value: `+${gdpDelta}%`, unit: '', color: 'var(--emerald)', trend: gdpDelta },
            { label: 'Wage Index', value: isRunning ? (1.065 + iteration * 0.001).toFixed(3) : '1.065', unit: '' },
            { label: 'Tax Base Δ', value: '+2.4pp', unit: '', color: 'var(--emerald)' },
          ]}
        />
        <ModelStatusCard
          title="CLEWS / OSeMOSYS"
          model="Resource Systems Model"
          status={clewsStatus}
          glowColor="amber"
          kpis={[
            { label: 'System Cost', value: `$${sysCost}M`, unit: '' },
            { label: 'RE Share', value: '60.0%', unit: '' },
            { label: 'CO₂ Proj.', value: `${co2Proj} Mt`, unit: '', color: 'var(--amber)' },
            { label: 'Solar Cap', value: '0.8 GW', unit: '' },
          ]}
        />
        <ModelStatusCard
          title="Convergence Engine"
          model="Iterative Coupling Loop"
          status={isConverged ? 'converged' : isRunning ? 'running' : 'idle'}
          glowColor={isConverged ? 'emerald' : 'blue'}
          kpis={[
            { label: 'L2 Norm Δ', value: currentDelta != null ? currentDelta.toExponential(3) : '—', color: 'var(--emerald)' },
            { label: 'Iteration', value: `${iteration} / ${maxIter}`, unit: '' },
            { label: 'ε Threshold', value: '1×10⁻⁴', unit: '' },
            { label: 'Progress', value: `${Math.round(convergencePct)}%`, color: isConverged ? 'var(--emerald)' : 'var(--blue)' },
          ]}
        />
      </div>

      {/* Row 2: Chart (2/3) + Gauge + Drift (1/3) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
        <ConvergenceChart history={history} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <ConvergenceGauge pct={convergencePct} isConverged={isConverged} />
          <ParameterDriftPanel history={history} />
        </div>
      </div>

      {/* Row 3: ETL Visualizer (left) + Telemetry stream (right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <ETLFlowVisualizer isRunning={isRunning} />
          <IterationTable history={history} epsilon={epsilon} />
        </div>
        <TelemetryStream messages={messages} maxHeight={380} />
      </div>
    </div>
  );
}
