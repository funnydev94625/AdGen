const express = require('express');
const cors = require('cors');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs-extra');
require('dotenv').config();

// Import routes
const videoRoutes = require('./routes/video');
const imageRoutes = require('./routes/image');
const pdfRoutes = require('./routes/pdf');
const statusRoutes = require('./routes/status');
const downloadRoutes = require('./routes/download');

// Import services
const TaskManager = require('./services/TaskManager');
const WebSocketManager = require('./services/WebSocketManager');

const app = express();
const server = http.createServer(app);

// Initialize services
const taskManager = new TaskManager();
const wsManager = new WebSocketManager(server);

// Make services available to routes
app.locals.taskManager = taskManager;
app.locals.wsManager = wsManager;

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Create directories
const uploadDir = process.env.UPLOAD_DIR || './uploads';
const outputDir = process.env.OUTPUT_DIR || './output';
fs.ensureDirSync(uploadDir);
fs.ensureDirSync(outputDir);

// Static file serving
app.use('/uploads', express.static(uploadDir));
app.use('/output', express.static(outputDir));

// API Routes
app.use('/api/generate/video', videoRoutes);
app.use('/api/generate/image', imageRoutes);
app.use('/api/generate/pdf', pdfRoutes);
app.use('/api/status', statusRoutes);
app.use('/api/download', downloadRoutes);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ 
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

const PORT = process.env.PORT || 5000;

server.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📁 Upload directory: ${uploadDir}`);
  console.log(`📁 Output directory: ${outputDir}`);
  console.log(`🔗 WebSocket server ready`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
  });
});

module.exports = { app, server, taskManager, wsManager };
