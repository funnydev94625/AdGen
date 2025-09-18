const express = require('express');
const router = express.Router();
const ImageGenerator = require('../services/ImageGenerator');

const imageGenerator = new ImageGenerator();

// POST /api/generate/image
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
    const task = taskManager.createTask('image', { prompt });
    
    // Start image generation in background
    setImmediate(async () => {
      try {
        await imageGenerator.generateImage(prompt, task.id, taskManager, wsManager);
      } catch (error) {
        console.error('Background image generation error:', error);
      }
    });

    res.json({
      success: true,
      taskId: task.id,
      message: 'Image generation started'
    });

  } catch (error) {
    console.error('Image generation route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

module.exports = router;
