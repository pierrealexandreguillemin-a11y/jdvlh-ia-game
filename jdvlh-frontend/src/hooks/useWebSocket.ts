import { useEffect, useState, useRef, useCallback } from 'react';

export const useWebSocket = (playerId: string) => {
  const socketRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/${playerId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      // Request sync state
      ws.send(JSON.stringify({ action: 'sync' }));
    };

    ws.onclose = () => setIsConnected(false);

    ws.onerror = (error) => console.error('WS error', error);

    socketRef.current = ws;

    return () => {
      ws.close();
    };
  }, [playerId]);

  const send = useCallback((message: Record<string, unknown>) => {
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    }
  }, []);

  return { socket: () => socketRef.current!, isConnected, send };
};