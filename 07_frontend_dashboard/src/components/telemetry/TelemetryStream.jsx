import React, { useRef, useEffect, useState } from 'react';
import { LogEntry } from './LogEntry';
import { Panel } from '../ui/Panel';

export function TelemetryStream({ messages, maxHeight = 500 }) {
  const bottomRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  const handleDownload = () => {
    const text = messages.map(m => `[${m.timestamp}] ${m.text}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'ogclews_telemetry.txt'; a.click();
    URL.revokeObjectURL(url);
  };

  const filtered = filter
    ? messages.filter(m => m.text.toLowerCase().includes(filter.toLowerCase()))
    : messages;

  return (
    <Panel
      title="Live Telemetry Stream"
      actions={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {messages.length} lines
          </span>
          <button onClick={() => setAutoScroll(v => !v)} style={{
            fontSize: 10, padding: '2px 8px', borderRadius: 3, cursor: 'pointer',
            background: autoScroll ? 'var(--emerald-glow)' : 'var(--bg-active)',
            border: `1px solid ${autoScroll ? 'var(--emerald-dim)' : 'var(--border-muted)'}`,
            color: autoScroll ? 'var(--emerald)' : 'var(--text-muted)',
            fontFamily: 'var(--font-mono)',
          }}>
            {autoScroll ? '⬇ PIN' : 'PIN'}
          </button>
          <button onClick={handleDownload} style={{
            fontSize: 10, padding: '2px 8px', borderRadius: 3, cursor: 'pointer',
            background: 'var(--bg-active)', border: '1px solid var(--border-muted)',
            color: 'var(--text-muted)', fontFamily: 'var(--font-mono)',
          }}>
            ↓ LOG
          </button>
        </div>
      }
      style={{ height: '100%' }}
    >
      {/* Filter bar */}
      <div style={{ marginBottom: 10 }}>
        <input
          type="text"
          placeholder="Filter logs…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          style={{
            width: '100%', padding: '5px 10px', fontSize: 11,
            background: 'var(--bg-base)', border: '1px solid var(--border-muted)',
            borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)',
            fontFamily: 'var(--font-mono)', outline: 'none',
          }}
        />
      </div>
      <div style={{
        maxHeight, overflowY: 'auto', padding: '4px 0',
        background: 'var(--bg-base)', borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border-subtle)',
        paddingLeft: 10, paddingRight: 10,
      }}>
        {filtered.length === 0 ? (
          <div style={{ padding: '24px 0', textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            System idle. Variables pending dispatch.
          </div>
        ) : (
          filtered.map(msg => (
            <LogEntry key={msg.id} timestamp={msg.timestamp} level={msg.level} text={msg.text} />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </Panel>
  );
}
