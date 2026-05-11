import { useState, useCallback, useRef } from 'react';

export function useWebSocket(url) {
  const [status, setStatus] = useState('idle'); // idle | connecting | open | closed | error
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);

  const parseLevel = (text) => {
    if (text.includes('[ERROR]') || text.includes('ERROR')) return 'error';
    if (text.includes('[WARN]') || text.includes('WARNING')) return 'warning';
    if (text.includes('[CONVERGED]') || text.toLowerCase().includes('converged')) return 'converged';
    if (text.includes('── Iteration') || text.includes('Iteration ')) return 'iteration';
    if (text.includes('delta') || text.includes('Δ') || text.includes('norm')) return 'delta';
    if (text.includes('[SYSTEM]')) return 'system';
    return 'info';
  };

  const connect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setStatus('connecting');
    setMessages([]);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setStatus('open');
    ws.onmessage = (e) => {
      const text = e.data;
      const entry = {
        id: Date.now() + Math.random(),
        text,
        level: parseLevel(text),
        timestamp: new Date().toISOString().slice(11, 23),
      };
      setMessages(prev => [...prev, entry]);
    };
    ws.onclose = () => setStatus('closed');
    ws.onerror = () => setStatus('error');
  }, [url]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('idle');
  }, []);

  return { status, messages, connect, disconnect };
}
