const OpenAI = require('openai');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const RunwayML = require('@runwayml/sdk');



class ImageGenerator {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    this.client = new RunwayML({
      apiKey: process.env.RUNWAY_API_KEY
    });
    this.outputDir = process.env.OUTPUT_DIR || './output';
  }

  async generateImage(prompt, taskId, taskManager, wsManager, filename = null, refImage = null) {
    try {
      // Update task status
      taskManager.updateTask(taskId, {
        status: 'running',
        progress: 20,
        message: 'Generating image with RunwayML...'
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

      // Generate image using RunwayML (matches Python implementation)
      const imagePath = await this.generateImageWithRunway(prompt, filename, refImage);
      
      if (imagePath) {
        taskManager.updateTask(taskId, {
          status: 'completed',
          progress: 100,
          message: 'Image generation completed successfully!',
          data: { imagePath }
        });
        wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));
        return imagePath;
      } else {
        throw new Error('Image generation failed');
      }

    } catch (error) {
      console.error('Image generation error:', error);
      taskManager.updateTask(taskId, {
        status: 'failed',
        error: error.message
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));
      throw error;
    }
  }


  async generateImageWithRunway(prompt, filename = null, refImage = null) {
    /**
     * Generate an image from a text prompt with retry logic.
     * Matches the Python implementation exactly.
     */
    console.log('----image prompt---', prompt);
    const maxRetries = 3;
    let retryCount = 0;
    
    while (retryCount < maxRetries) {
      try {
        let task = null;
        console.log(`Image generation attempt ${retryCount + 1}/${maxRetries}`);
        console.log(`Reference image length: ${refImage ? refImage.length : 0}`);
        
        if (refImage === "None" || !refImage) {
          task = await this.client.textToImage.create({
            model: 'gen4_image',
            ratio: '1280:720',
            promptText: prompt,
          }).waitForTaskOutput();
        } else {
          task = await this.client.textToImage.create({
            model: 'gen4_image',
            ratio: '1280:720',
            promptText: prompt + "Draw different from the reference image or Draw similar to the reference image",
            referenceImages: [
              {
                uri: refImage,
                tag: 'scene_5s_ago',
              },
            ],
          }).waitForTaskOutput();
        }
        
        console.log('Task complete:', task);
        console.log('Image URL:', task.output[0]);
        console.log('----------', filename);

        if (retryCount < maxRetries) {
          console.log("⏳ Retrying in 5 seconds...");
          await new Promise(resolve => setTimeout(resolve, 2500)); // retry_delay // 2
        }

        const result = await this._downloadAndSaveImage(task.output[0], filename);
        if (result) {
          return result;
        } else {
          throw new Error("Failed to download image");
        }
        
      } catch (error) {
        if (error.name === 'TaskFailedError') {
          retryCount++;
          console.log(`❌ Image generation failed (attempt ${retryCount}/${maxRetries})`);
          console.log(`Error details: ${error.taskDetails}`);
          
          if (retryCount < maxRetries) {
            console.log("⏳ Retrying in 5 seconds...");
            await new Promise(resolve => setTimeout(resolve, 2500)); // retry_delay // 2
          } else {
            console.log("💥 Max retries reached for image generation. Returning None.");
            return null;
          }
        } else {
          retryCount++;
          console.log(`❌ Error generating image (attempt ${retryCount}/${maxRetries}): ${error.message}`);
          
          if (retryCount < maxRetries) {
            console.log("⏳ Retrying in 5 seconds...");
            await new Promise(resolve => setTimeout(resolve, 2500)); // retry_delay // 2
          } else {
            console.log("💥 Max retries reached for image generation. Returning None.");
            return null;
          }
        }
      }
    }
    
    return null;
  }

  async generateVisualsForScenes(scenes) {
    /**
     * Generate images for all scenes with visual consistency.
     * Matches the Python implementation exactly.
     */
    const imagePaths = [];
    let refImage = "None";
    
    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      const baseFilename = `image_${String(i + 1).padStart(2, '0')}.png`;
      
      console.log(`Generating image for scene ${i + 1}/${scenes.length}: ${scene.text ? scene.text.substring(0, 50) : scene.substring(0, 50)}...`);
      console.log(scene.text || scene);
      
      const imagePath = await this.generateImageWithRunway(scene.text || scene, baseFilename, refImage);
      imagePaths.push(imagePath);
      
      if (imagePath) {
        refImage = await this.getImageAsDataUri(imagePath);
      }
      
      // Add delay to respect API rate limits
      if (i < scenes.length - 1) { // Don't delay after the last image
        console.log("⏳ Waiting 2 seconds before next request...");
        await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay between requests
      }
    }
    
    const successfulGenerations = imagePaths.filter(path => path !== null).length;
    console.log(`Successfully generated ${successfulGenerations}/${scenes.length} images`);
    return imagePaths;
  }

  async getImageAsDataUri(imagePath) {
    /**
     * Convert image file to data URI format.
     * Matches the Python implementation exactly.
     */
    try {
      const fs = require('fs');
      const path = require('path');
      
      // Read image file
      const imageBuffer = fs.readFileSync(imagePath);
      const base64Image = imageBuffer.toString('base64');
      
      // Determine content type based on file extension
      const ext = path.extname(imagePath).toLowerCase();
      let contentType;
      
      switch (ext) {
        case '.png':
          contentType = 'image/png';
          break;
        case '.jpg':
        case '.jpeg':
          contentType = 'image/jpeg';
          break;
        case '.gif':
          contentType = 'image/gif';
          break;
        case '.webp':
          contentType = 'image/webp';
          break;
        default:
          contentType = 'image/png'; // Default fallback
      }
      
      return `data:${contentType};base64,${base64Image}`;
    } catch (error) {
      console.error('Error converting image to data URI:', error);
      return "None";
    }
  }

  async generateImageWithDALLE(prompt) {
    try {
      const response = await this.openai.images.generate({
        model: 'dall-e-3',
        prompt: prompt,
        size: '1024x1024',
        quality: 'standard',
        n: 1
      });

      return response.data[0].url;
    } catch (error) {
      console.error('DALL-E 3 generation error:', error);
      throw new Error('Failed to generate image with DALL-E 3');
    }
  }

  async _downloadAndSaveImage(imageUrl, filename = null) {
    /**Download image from URL and save to local file. Matches Python implementation exactly.*/
    try {
      // Create output directory if it doesn't exist
      await fs.ensureDir(this.outputDir);
      
      // Generate filename if not provided
      if (!filename) {
        const timestamp = Date.now();
        filename = `image_${timestamp}.png`;
      }
      
      const imagePath = path.join(this.outputDir, filename);
      
      // Download image with retry logic
      const maxRetries = 3;
      let retryCount = 0;
      let lastError;
      
      while (retryCount < maxRetries) {
        try {
          console.log(`Downloading image (attempt ${retryCount + 1}/${maxRetries})...`);
          
          const response = await axios({
            method: 'GET',
            url: imageUrl,
            responseType: 'stream',
            timeout: 30000, // 30 seconds timeout
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
              'Accept': 'image/png,image/jpeg,image/*,*/*',
              'Accept-Encoding': 'gzip, deflate',
              'Connection': 'keep-alive'
            }
          });
          
          if (response.status === 200) {
            // Save image to file
            const writer = fs.createWriteStream(imagePath);
            response.data.pipe(writer);
            
            return new Promise((resolve, reject) => {
              writer.on('finish', () => {
                console.log(`✅ Image saved: ${imagePath}`);
                resolve(imagePath);
              });
              writer.on('error', reject);
            });
          } else {
            throw new Error(`HTTP ${response.status}: Failed to download image from ${imageUrl}`);
          }
          
        } catch (error) {
          lastError = error;
          console.error(`Request error on attempt ${retryCount + 1}:`, error.message);
          
          if (retryCount < maxRetries - 1) {
            const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
            console.log(`Retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
          }
          
          retryCount++;
        }
      }
      
      throw lastError;
      
    } catch (error) {
      console.error('Image download error:', error);
      return null;
    }
  }

  async downloadAndSaveImage(imageUrl, taskId) {
    try {
      const filename = `image_${taskId}.png`;
      const imagePath = path.join(this.outputDir, filename);

      // Download image with retry logic
      const maxRetries = 3;
      let lastError;

      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          console.log(`Downloading image (attempt ${attempt}/${maxRetries})...`);

          const response = await axios({
            method: 'GET',
            url: imageUrl,
            responseType: 'stream',
            timeout: 30000, // 30 seconds timeout
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
              'Accept': 'image/png,image/jpeg,image/*,*/*',
              'Accept-Encoding': 'gzip, deflate',
              'Connection': 'keep-alive'
            }
          });

          // Save image to file
          const writer = fs.createWriteStream(imagePath);
          response.data.pipe(writer);

          return new Promise((resolve, reject) => {
            writer.on('finish', () => {
              console.log(`✅ Image saved: ${imagePath}`);
              resolve(imagePath);
            });
            writer.on('error', reject);
          });

        } catch (error) {
          lastError = error;
          console.error(`Request error on attempt ${attempt}:`, error.message);

          if (attempt < maxRetries) {
            const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
            console.log(`Retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }

      throw lastError;

    } catch (error) {
      console.error('Image download error:', error);
      throw new Error('Failed to download image');
    }
  }
}

module.exports = ImageGenerator;
