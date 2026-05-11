import React, { useState, useCallback } from 'react';
import './index.css';
import './App.css';
import { Sidebar } from './components/layout/Sidebar';
import { Topbar } from './components/layout/Topbar';
import { ScenarioWorkspace } from './components/scenario/ScenarioWorkspace';
import { MacroConfigPanel } from './components/parameters/MacroConfigPanel';
import { CLEWSConstraintsPanel } from './components/parameters/CLEWSConstraintsPanel';
import { TelemetryStream } from './components/telemetry/TelemetryStream';
import { ResultsPanel } from './components/results/ResultsPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useConvergenceState } from './hooks/useConvergenceState';
import { useParameterState } from './hooks/useParameterState';
import { OverviewPage } from './components/overview/OverviewPage';

const WS_URL = 'ws://localhost:8000/ws/convergence';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemState, setSystemState] = useState('idle'); // idle | running | converged | error

  const { status: wsStatus, messages, connect, disconnect } = useWebSocket(WS_URL);
  const convergence = useConvergenceState(messages);
  const { macroParams, clewsParams, updateMacro, updateClews, resetAll } = useParameterState();

  // Derive system state from WS status + convergence
  React.useEffect(() => {
    if (wsStatus === 'open')   setSystemState('running');
    if (wsStatus === 'closed') setSystemState(convergence.isConverged ? 'converged' : 'idle');
    if (wsStatus === 'error')  setSystemState('error');
  }, [wsStatus, convergence.isConverged]);

  const handleRun = useCallback(() => {
    setSystemState('running');
    connect();
  }, [connect]);

  const handleAbort = useCallback(() => {
    disconnect();
    setSystemState('idle');
  }, [disconnect]);

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage onEnter={() => setActiveTab('workspace')} />;
      case 'workspace':
        return (
          <ScenarioWorkspace
            systemState={systemState}
            convergence={convergence}
            messages={messages}
          />
        );
      case 'macro':
        return (
          <MacroConfigPanel
            params={macroParams}
            onUpdate={updateMacro}
            onReset={resetAll}
          />
        );
      case 'clews':
        return (
          <CLEWSConstraintsPanel
            params={clewsParams}
            onUpdate={updateClews}
            onReset={resetAll}
          />
        );
      case 'telemetry':
        return (
          <div style={{ padding: 24, flex: 1, display: 'flex', flexDirection: 'column' }}>
            <TelemetryStream messages={messages} maxHeight={600} />
          </div>
        );
      case 'results':
        return <ResultsPanel isConverged={convergence.isConverged} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg-base)' }}>
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        systemState={systemState}
        iteration={convergence.iteration}
        maxIter={convergence.maxIter}
      />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar
          activeTab={activeTab}
          systemState={systemState}
          iteration={convergence.iteration}
          maxIter={convergence.maxIter}
          currentDelta={convergence.currentDelta}
          onRun={handleRun}
          onAbort={handleAbort}
        />
        <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {renderContent()}
        </div>
      </div>
    </div>
  );
}
