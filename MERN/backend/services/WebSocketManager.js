const WebSocket = require('ws');

class WebSocketManager {
  constructor(server) {
    this.wss = new WebSocket.Server({ server });
    this.clients = new Set();
    this.setupWebSocketServer();
  }

  setupWebSocketServer() {
    this.wss.on('connection', (ws, req) => {
      console.log('New WebSocket connection');
      this.clients.add(ws);

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'connection',
        message: 'Connected to AdGen WebSocket server',
        timestamp: new Date().toISOString()
      }));

      // Handle client messages
      ws.on('message', (message) => {
        try {
          const data = JSON.parse(message);
          this.handleClientMessage(ws, data);
        } catch (error) {
          console.error('Invalid WebSocket message:', error);
          ws.send(JSON.stringify({
            type: 'error',
            message: 'Invalid message format'
          }));
        }
      });

      // Handle client disconnect
      ws.on('close', () => {
        console.log('WebSocket connection closed');
        this.clients.delete(ws);
      });

      // Handle errors
      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });
    });

    console.log('WebSocket server initialized');
  }

  handleClientMessage(ws, data) {
    switch (data.type) {
      case 'subscribe':
        // Client wants to subscribe to task updates
        ws.taskId = data.taskId;
        ws.send(JSON.stringify({
          type: 'subscribed',
          taskId: data.taskId,
          message: `Subscribed to task ${data.taskId}`
        }));
        break;
      
      case 'unsubscribe':
        // Client wants to unsubscribe
        ws.taskId = null;
        ws.send(JSON.stringify({
          type: 'unsubscribed',
          message: 'Unsubscribed from task updates'
        }));
        break;
      
      case 'ping':
        // Heartbeat
        ws.send(JSON.stringify({
          type: 'pong',
          timestamp: new Date().toISOString()
        }));
        break;
      
      default:
        ws.send(JSON.stringify({
          type: 'error',
          message: `Unknown message type: ${data.type}`
        }));
    }
  }

  broadcastTaskUpdate(taskId, taskData) {
    const message = JSON.stringify({
      type: 'task_update',
      taskId,
      task: taskData,
      timestamp: new Date().toISOString()
    });

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN && 
          (client.taskId === taskId || !client.taskId)) {
        client.send(message);
      }
    });
  }

  broadcastToAll(message) {
    const data = JSON.stringify({
      type: 'broadcast',
      message,
      timestamp: new Date().toISOString()
    });

    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    });
  }

  getConnectedClientsCount() {
    return this.clients.size;
  }

  close() {
    this.wss.close();
  }
}

module.exports = WebSocketManager;
