const express = require('express');
const router = express.Router();
const PDFGenerator = require('../services/PDFGenerator');

const pdfGenerator = new PDFGenerator();

// POST /api/generate/pdf
router.post('/', async (req, res) => {
  try {
    const { prompt, title } = req.body;

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
    const task = taskManager.createTask('pdf', { prompt, title });
    
    // Start PDF generation in background
    setImmediate(async () => {
      try {
        await pdfGenerator.generatePDF(
          prompt, 
          title || 'Generated Document', 
          task.id, 
          taskManager, 
          wsManager
        );
      } catch (error) {
        console.error('Background PDF generation error:', error);
      }
    });

    res.json({
      success: true,
      taskId: task.id,
      message: 'PDF generation started'
    });

  } catch (error) {
    console.error('PDF generation route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

module.exports = router;
