import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import toast from 'react-hot-toast';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [taskUpdates, setTaskUpdates] = useState({});
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = () => {
    try {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:5000';
      const newSocket = new WebSocket(wsUrl);

      newSocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setSocket(newSocket);
        toast.success('Connected to server');
      };

      newSocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      newSocket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setSocket(null);
        
        // Attempt to reconnect after 3 seconds
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connect();
        }, 3000);
      };

      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error');
      };

      wsRef.current = newSocket;
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  };

  const handleMessage = (data) => {
    switch (data.type) {
      case 'task_update':
        setTaskUpdates(prev => ({
          ...prev,
          [data.taskId]: data.task
        }));
        break;
      
      case 'connection':
        console.log('WebSocket connection established');
        break;
      
      case 'error':
        toast.error(data.message);
        break;
      
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const subscribeToTask = (taskId) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'subscribe',
        taskId
      }));
    }
  };

  const unsubscribeFromTask = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'unsubscribe'
      }));
    }
  };

  const sendPing = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'ping'
      }));
    }
  };

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Send ping every 30 seconds to keep connection alive
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(sendPing, 30000);
      return () => clearInterval(pingInterval);
    }
  }, [isConnected]);

  const value = {
    socket,
    isConnected,
    taskUpdates,
    subscribeToTask,
    unsubscribeFromTask,
    connect
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
