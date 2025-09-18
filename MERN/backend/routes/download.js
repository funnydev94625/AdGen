const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs-extra');

// GET /api/download/:filename
router.get('/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const outputDir = process.env.OUTPUT_DIR || './output';

    // Security check - only allow specific file types
    const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.png', '.jpg', '.jpeg', '.pdf'];
    console.log(filename)
    const fileExt = path.extname(filename).toLowerCase();
    
    if (!allowedExtensions.includes(fileExt)) {
      return res.status(400).json({
        success: false,
        error: 'File type not allowed'
      });
    }

    // Check if file exists
    const filePath = path.join(outputDir, filename);
    
    if (!await fs.pathExists(filePath)) {
      return res.status(404).json({
        success: false,
        error: 'File not found'
      });
    }

    // Determine content type based on file extension
    let contentType = 'application/octet-stream';
    if (['.mp4', '.avi', '.mov', '.mkv'].includes(fileExt)) {
      contentType = 'video/mp4';
    } else if (['.png', '.jpg', '.jpeg'].includes(fileExt)) {
      contentType = fileExt === '.png' ? 'image/png' : 'image/jpeg';
    } else if (fileExt === '.pdf') {
      contentType = 'application/pdf';
    }

    // Set headers and send file
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    
    // Stream file to response
    const fileStream = fs.createReadStream(filePath);
    fileStream.pipe(res);

    fileStream.on('error', (error) => {
      console.error('File stream error:', error);
      if (!res.headersSent) {
        res.status(500).json({
          success: false,
          error: 'Error reading file'
        });
      }
    });

  } catch (error) {
    console.error('Download route error:', error);
    res.status(500).json({
      success: false,
      error: 'Server error occurred'
    });
  }
});

module.exports = router;
