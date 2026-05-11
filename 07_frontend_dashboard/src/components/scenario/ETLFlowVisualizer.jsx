import React from 'react';
import { ETL_MAPPING } from '../../constants/modelConstants';

const COLOR_MAP = { emerald: 'var(--emerald)', amber: 'var(--amber)', blue: 'var(--blue)' };

function PipelineNode({ label, sublabel, color, isActive }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, minWidth: 90,
    }}>
      <div style={{
        padding: '8px 12px', borderRadius: 'var(--radius)',
        border: `1px solid ${isActive ? color : 'var(--border-muted)'}`,
        background: isActive ? `${color}18` : 'var(--bg-elevated)',
        fontSize: 11, fontWeight: 600, color: isActive ? color : 'var(--text-secondary)',
        textAlign: 'center', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap',
        boxShadow: isActive ? `0 0 10px ${color}40` : 'none',
        transition: 'all 0.4s ease',
      }}>
        {label}
      </div>
      {sublabel && (
        <div style={{ fontSize: 9, color: 'var(--text-muted)', textAlign: 'center', maxWidth: 90 }}>{sublabel}</div>
      )}
    </div>
  );
}

function Arrow({ color, isActive }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0, position: 'relative', width: 32 }}>
      <div style={{ height: 1, width: '100%', background: isActive ? color : 'var(--border-subtle)', transition: 'background 0.4s ease' }} />
      {/* Animated packet dot */}
      {isActive && (
        <div style={{
          position: 'absolute', width: 7, height: 7, borderRadius: '50%',
          background: color, top: '50%', transform: 'translateY(-50%)',
          animation: 'flow-packet 1.8s linear infinite',
        }} />
      )}
      <svg width="6" height="10" viewBox="0 0 6 10" style={{ flexShrink: 0 }}>
        <path d="M0 0 L6 5 L0 10" fill="none" stroke={isActive ? color : 'var(--border-subtle)'} strokeWidth="1.2" />
      </svg>
    </div>
  );
}

export function ETLFlowVisualizer({ isRunning }) {
  return (
    <div style={{ padding: '14px 18px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius)', border: '1px solid var(--border-subtle)' }}>
      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 14 }}>
        ETL Data Pipeline
      </div>

      {/* Top-level pipeline */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 0, overflowX: 'auto' }}>
        <PipelineNode label="CLEWS" sublabel="OSeMOSYS output" color="var(--violet)" isActive={isRunning} />
        <Arrow color="var(--violet)" isActive={isRunning} />
        <PipelineNode label="Validator" sublabel="pydantic + jsonschema" color="var(--amber)" isActive={isRunning} />
        <Arrow color="var(--amber)" isActive={isRunning} />
        <PipelineNode label="ETL Transform" sublabel="YAML schema driven" color="var(--blue)" isActive={isRunning} />
        <Arrow color="var(--blue)" isActive={isRunning} />
        <PipelineNode label="OG-Core" sublabel="Macro parameter input" color="var(--emerald)" isActive={isRunning} />
      </div>

      {/* Variable mapping rows */}
      <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ETL_MAPPING.map(({ clews, var: v, transform, og, color }) => (
          <div key={og} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 10, fontFamily: 'var(--font-mono)' }}>
            <span style={{ color: 'var(--text-muted)', minWidth: 160 }}>{clews}</span>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{transform}</span>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <span style={{ color: COLOR_MAP[color] ?? 'var(--text-primary)', fontWeight: 600 }}>{og}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
