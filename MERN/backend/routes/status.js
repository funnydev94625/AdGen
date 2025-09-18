const express = require('express');
const router = express.Router();

// GET /api/status/:taskId
router.get('/:taskId', (req, res) => {
  try {
    const { taskId } = req.params;
    const { taskManager } = req.app.locals;

    const task = taskManager.getTask(taskId);
    
    if (!task) {
      return res.status(404).json({
        success: false,
        error: 'Task not found'
      });
    }

    // Extract filename for response
    let filename = null;
    if (task.data && task.data.videoPath) {
      filename = task.data.videoPath.split('/').pop();
    } else if (task.data && task.data.imagePath) {
      filename = task.data.imagePath.split('/').pop();
    } else if (task.data && task.data.pdfPath) {
      filename = task.data.pdfPath.split('/').pop();
    }

    res.json({
      success: true,
      taskId: task.id,
      status: task.status,
      progress: task.progress,
      message: task.message,
      type: task.type,
      filename,
      error: task.error,
      createdAt: task.createdAt,
      updatedAt: task.updatedAt
    });

  } catch (error) {
    console.error('Status route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

// GET /api/status - Get all tasks
router.get('/', (req, res) => {
  try {
    const { taskManager } = req.app.locals;
    const tasks = taskManager.getAllTasks();

    res.json({
      success: true,
      tasks: tasks.map(task => ({
        id: task.id,
        type: task.type,
        status: task.status,
        progress: task.progress,
        message: task.message,
        createdAt: task.createdAt,
        updatedAt: task.updatedAt
      }))
    });

  } catch (error) {
    console.error('Status route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

module.exports = router;
