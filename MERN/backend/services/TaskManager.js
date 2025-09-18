const { v4: uuidv4 } = require('uuid');

class TaskManager {
  constructor() {
    this.tasks = new Map();
    this.cleanupInterval = setInterval(() => {
      this.cleanupOldTasks();
    }, 5 * 60 * 1000); // Clean up every 5 minutes
  }

  createTask(type, data = {}) {
    const taskId = uuidv4();
    const task = {
      id: taskId,
      type,
      status: 'pending',
      progress: 0,
      message: 'Task created',
      data,
      createdAt: new Date(),
      updatedAt: new Date(),
      error: null
    };

    this.tasks.set(taskId, task);
    return task;
  }

  updateTask(taskId, updates) {
    const task = this.tasks.get(taskId);
    if (!task) {
      throw new Error(`Task ${taskId} not found`);
    }

    Object.assign(task, updates, { updatedAt: new Date() });
    return task;
  }

  getTask(taskId) {
    return this.tasks.get(taskId);
  }

  getAllTasks() {
    return Array.from(this.tasks.values());
  }

  deleteTask(taskId) {
    return this.tasks.delete(taskId);
  }

  cleanupOldTasks() {
    const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago
    
    for (const [taskId, task] of this.tasks.entries()) {
      if (task.createdAt < cutoffTime) {
        this.tasks.delete(taskId);
        console.log(`Cleaned up old task: ${taskId}`);
      }
    }
  }

  destroy() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.tasks.clear();
  }
}

module.exports = TaskManager;
