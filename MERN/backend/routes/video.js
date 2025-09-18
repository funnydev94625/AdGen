const express = require('express');
const router = express.Router();
const VideoGenerator = require('../services/VideoGenerator');

const videoGenerator = new VideoGenerator();

// POST /api/generate/video
router.post('/', async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt || !prompt.trim()) {
      return res.status(400).json({
        success: false,
        error: 'Prompt is required'
      });
    }

    // Check for OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({
        success: false,
        error: 'OpenAI API key not configured'
      });
    }

    // Get task manager and WebSocket manager from app
    const { taskManager, wsManager } = req.app.locals;

    // Create task
    const task = taskManager.createTask('video', { prompt });
    
    // Start video generation in background
    setImmediate(async () => {
      try {
        await videoGenerator.generateVideo(prompt, task.id, taskManager, wsManager);
      } catch (error) {
        console.error('Background video generation error:', error);
      }
    });

    res.json({
      success: true,
      taskId: task.id,
      message: 'Video generation started'
    });

  } catch (error) {
    console.error('Video generation route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

module.exports = router;
