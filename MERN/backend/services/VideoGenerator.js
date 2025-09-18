const OpenAI = require('openai');
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const ImageGenerator = require('./ImageGenerator');
const RunwayML = require('@runwayml/sdk');

class VideoGenerator {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    console.log('OPENAI_API_KEY', process.env.OPENAI_API_KEY);
    console.log('RUNWAY_API_KEY', process.env.RUNWAY_API_KEY);
    this.outputDir = process.env.OUTPUT_DIR || './output';
    this.imageGenerator = new ImageGenerator();
    this.client = new RunwayML({
      apiKey: process.env.RUNWAY_API_KEY
    });
  }

  async generateVideo(prompt, taskId, taskManager, wsManager) {
    try {
      // Update task status
      taskManager.updateTask(taskId, {
        status: 'running',
        progress: 10,
        message: 'Generating video script...'
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

      // Generate script using OpenAI
      const scriptResponse = await this.generateScript(prompt);
      console.log('script response', scriptResponse);
      // Parse the script response into scenes
      const scenes = this.parseScene(scriptResponse);
      console.log('parsed scenes', scenes);
      
      if (!scenes || scenes.length === 0) {
        throw new Error('Failed to parse scenes from script');
      }
      
      taskManager.updateTask(taskId, {
        progress: 30,
        message: 'Script generated, creating video...'
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

      // Generate video using RunwayML
      const videoPath = await this.generate(scenes.slice(0,1), taskId, taskManager, wsManager);

      if (videoPath) {
        taskManager.updateTask(taskId, {
          status: 'completed',
          progress: 100,
          message: 'Video generation completed successfully!',
          data: { videoPath }
        });
        wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));
        return videoPath;
      } else {
        throw new Error('Video generation failed');
      }

    } catch (error) {
      console.error('Video generation error:', error);
      taskManager.updateTask(taskId, {
        status: 'failed',
        error: error.message
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));
      throw error;
    }
  }

  async generateScript(prompt) {
    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a professional video script writer. Create engaging, concise scripts for video content.'
          },
          {
            role: 'user',
            content: `
            You are a professional video director and storyteller.  
            Your task is to take any simple text input (for example, an event description, product launch, campaign idea, or brand story) and transform it into a scene-by-scene video plan.  

            ⚡ Instructions:  
            1. The video should last between 1–3 minutes.  
            2. Break the video into **scenes of exactly 10 seconds each**.  
            3. Output format must be:  
            SCENE 1: [Detailed, cinematic, modern visual description] | Duration: 10 seconds  
            SCENE 2: [Detailed, cinematic, modern visual description] | Duration: 10 seconds  
            … continue until the full story is covered.  
            4. Each scene should feel **authentic, realistic, and engaging**—like a professionally filmed live-action commercial or promotional video.  
            5. Use **modern, clear, and visually compelling language** (avoid generic words). Make the viewer feel immersed.  
            6. Add **text overlays** where appropriate (such as event names, slogans, calls to action).  
            7. Maintain **consistency of style and atmosphere** across all scenes.  
            8. End with a strong **closing scene** that reinforces the main message.  

            🎬 Example Input:  
            "Create a vibrant flyer for the 'Summer Fun Fair' happening on July 20, 2025, from 10 AM to 4 PM at Maplewood Park. Include a headline that says 'Join Us for a Day of Family Fun!' and a short description mentioning games, food stalls, a petting zoo, and live music. Add images of a carousel, kids playing games, and a food stall."  

            🎥 Example Output:  
            SCENE 1: A sunny, wide shot of Maplewood Park with families entering through an archway decorated with balloons and streamers. Children run with excitement, while the headline text "Summer Fun Fair – July 20, 2025" animates onto the screen in bold, vibrant colors. | Duration: 10 seconds  

            SCENE 2: A close-up of a brightly lit carousel spinning, with kids waving and laughing as the ride turns. The scene feels joyful and energetic. | Duration: 10 seconds  

            SCENE 3: Transition to a lively area where kids are playing fair games—ring toss, balloon darts, and beanbag throws. Excited cheers and laughter fill the background.  | Duration: 10 seconds  

            SCENE 4: Pan across colorful food stalls—cotton candy being spun, lemonade being poured, and sizzling hotdogs on the grill. Families are smiling while holding tasty treats. | Duration: 10 seconds  

            SCENE 5: A cheerful petting zoo scene: kids pet goats and rabbits, while parents snap photos. A pony with a small child on its back walks gently in the background. | Duration: 10 seconds  

            SCENE 6: A small stage with a live band performing upbeat music, families dancing and clapping along. Close-up of guitar strumming and kids jumping to the beat. | Duration: 10 seconds  

            SCENE 7: Wide panoramic shot of the entire fair in full swing—carousel spinning, food stalls buzzing, and the stage lit up. The atmosphere is festive and filled with color.  | Duration: 10 seconds  

            SCENE 8: Animated banner fills the screen with "Join Us for a Day of Family Fun!" followed by the event details: July 20, 2025 | 10 AM – 4 PM | Maplewood Park. | Duration: 10 seconds  

            SCENE 9: Closing shot of families waving at the camera, kids holding balloons, and the sun setting softly over the park. Final overlay: "Don't Miss It!" | Duration: 10 seconds  
            try with this ${prompt}

        `
          }
        ],
        max_tokens: 1500,
        temperature: 0.7
      });

      return response.choices[0].message.content;
    } catch (error) {
      console.error('Script generation error:', error);
      throw new Error('Failed to generate video script');
    }
  }

  parseScene(aiResponse) {
    /**
     * Parse AI-generated scene response into Scene objects.
     * Based on the Python implementation from script_generator.py
     */
    try {
      const scenes = [];
      let currentTime = 0.0;
      
      // Split response into lines and process each scene
      const lines = aiResponse.split('\n');
      
      for (const line of lines) {
        
        // Look for scene patterns like "SCENE 1: [description] | Duration: [X seconds]"
        if (line.startsWith('SCENE') && line.includes('| Duration:')) {
          try {
            // Extract scene number
            const scenePart = line.split(':')[0]; // "SCENE 1"
            const sceneNumber = parseInt(scenePart.split(' ')[1]);
            
            // Extract description and duration
            const parts = line.split('| Duration:');
            if (parts.length === 2) {
              const description = "This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene(door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, The Real scene. **manequins mustn't move. People should be real and not cartoonish and overlay text should be real.** When describing a mirror, the image reflected in the mirror and the image outside must be exactly the same. description: " + parts[0].split(':')[1];
              const durationText = parts[1];
              
              // Extract duration (remove "seconds" if present)
              const durationStr = durationText.replace(/seconds?/g, '');
              const duration = parseFloat(durationStr);
              
              // Create scene object
              const scene = {
                text: description,
                duration: duration,
                scene_number: sceneNumber,
                start_time: currentTime,
                end_time: currentTime + duration
              };
              
              scenes.push(scene);
              currentTime += duration;
              
            }
          } catch (error) {
            console.log(`Error parsing scene line '${line}': ${error.message}`);
            continue;
          }
        }
      }
      
      // Sort scenes by scene number to ensure proper order
      scenes.sort((a, b) => a.scene_number - b.scene_number);
      
      // Recalculate start times
      currentTime = 0.0;
      for (const scene of scenes) {
        scene.start_time = currentTime;
        scene.end_time = scene.start_time + scene.duration;
        currentTime += scene.duration;
      }
      
      console.log(`Successfully parsed ${scenes.length} scenes from AI response`);
      return scenes;
      
    } catch (error) {
      console.log(`Error parsing AI scenes: ${error.message}`);
      return [];
    }
  }

  async generateVideoWithRunway(videoScripts, imagePaths) {
    try {
      const videoPaths = []

      // Generate individual videos for each scene
      for (let i = 0; i < videoScripts.length; i++) {
        const maxRetries = 3;
        let retryCount = 0;
        let success = false;

        while (retryCount < maxRetries && !success) {
          try {
            console.log(`Generating video for scene ${i + 1}/${videoScripts.length} (attempt ${retryCount + 1}/${maxRetries}): ${videoScripts[i].substring(0, 50)}...`);
            console.log(`Video script: ${videoScripts[i]}`);
            console.log(`Image path: ${imagePaths[i]}`);

            const imageBuffer = fs.readFileSync(imagePaths[i]);
            const dataUri = `data:image/png;base64,${imageBuffer.toString('base64')}`;

            const task = await this.client.imageToVideo.create({
              model: 'gen3a_turbo',
              promptImage: dataUri,
              promptText: videoScripts[i],
              ratio: '1280:768',
              duration: 10
            }).waitForTaskOutput();

            console.log('Task complete:', task);
            console.log('Video URL:', task.output[0]);

            const videoPath = await this.downloadAndSaveVideo(task.output[0], `video_${String(i + 1).padStart(2, '0')}.mp4`);

            if (videoPath) {
              videoPaths.push(videoPath);
              success = true;
              console.log(`✅ Successfully generated video for scene ${i + 1}`);
            } else {
              throw new Error("Failed to download video");
            }

          } catch (error) {
            retryCount++;
            console.log(`❌ Error generating video for scene ${i + 1} (attempt ${retryCount}/${maxRetries}): ${error.message}`);

            if (retryCount < maxRetries) {
              console.log("⏳ Retrying in 10 seconds...");
              await new Promise(resolve => setTimeout(resolve, 10000));
            } else {
              console.log(`💥 Max retries reached for scene ${i + 1}. Skipping this scene.`);
              videoPaths.push(null); // Add null for failed scene
            }
          }
        }

        // Add delay to respect API rate limits (only if successful)
        if (success && i < videoScripts.length - 1) {
          console.log("⏳ Waiting 5 seconds before next request...");
          await new Promise(resolve => setTimeout(resolve, 5000));
        }
      }

      const successfulGenerations = videoPaths.filter(path => path !== null).length;
      console.log(`🎬 Successfully generated ${successfulGenerations}/${videoScripts.length} videos`);

      // Concatenate all videos into a single video with fading effects
      // if (videoPaths.length > 0) {
      //   const finalVideoPath = await this.concatenateVideos(videoPaths);
      //   return finalVideoPath;
      // } else {
      //   throw new Error('No videos were generated successfully');
      // }
      return videoPaths;
    } catch (error) {
      console.error('RunwayML video generation error:', error);
      throw new Error('Failed to generate video with RunwayML');
    }
  }

  async downloadAndSaveVideo(video_url, filename) {
    try {
      const response = await axios.get(video_url, { responseType: 'stream' });
      const filePath = path.join(this.outputDir, filename);

      const writer = fs.createWriteStream(filePath);
      response.data.pipe(writer);

      return new Promise((resolve, reject) => {
        writer.on('finish', () => {
          console.log(`✅ Video saved: ${filePath}`);
          resolve(filePath);
        });
        writer.on('error', reject);
      });
    } catch (error) {
      console.error('Error downloading video:', error);
      return null;
    }
  }

  async concatenateVideos(videoPaths) {
    /**
     * Concatenate multiple video files into a single video with fading effects.
     * Matches the Python implementation using FFmpeg.
     */
    try {
      if (!videoPaths || videoPaths.length === 0) {
        console.log("No video paths provided for concatenation");
        return null;
      }

      // Filter out null values and check if files exist
      const validVideoPaths = [];
      for (const videoPath of videoPaths) {
        console.log(`Checking video path: ${videoPath}`);
        console.log(`Path exists: ${await fs.pathExists(videoPath)}`);
        
        if (videoPath && await fs.pathExists(videoPath)) {
          validVideoPaths.push(videoPath);
          console.log(`Added valid path: ${videoPath}`);
        } else {
          console.log(`Warning: Video file not found or invalid: ${videoPath}`);
        }
      }

      if (validVideoPaths.length === 0) {
        console.log("No valid video files found for concatenation");
        return null;
      }

      console.log(`Concatenating ${validVideoPaths.length} video files...`);

      // Generate output filename
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const outputFilename = `combined_video_${timestamp}.mp4`;
      const outputPath = path.join(this.outputDir, outputFilename);

      // Create FFmpeg command for concatenation with crossfade transitions
      const ffmpegCommand = await this.createFFmpegConcatenationCommand(validVideoPaths, outputPath);

      // Execute FFmpeg command
      const { exec } = require('child_process');
      const util = require('util');
      const execAsync = util.promisify(exec);

      console.log(`Exporting concatenated video to: ${outputPath}`);
      console.log(`FFmpeg command: ${ffmpegCommand}`);

      await execAsync(ffmpegCommand);

      // Clean up temporary file list if it exists
      const fileListPath = path.join(path.dirname(outputPath), 'filelist.txt');
      if (await fs.pathExists(fileListPath)) {
        await fs.remove(fileListPath);
        console.log('Cleaned up temporary file list');
      }

      console.log(`Video concatenation completed successfully: ${outputPath}`);
      return outputPath;

    } catch (error) {
      console.error('Error concatenating videos:', error);
      return null;
    }
  }

  async createFFmpegConcatenationCommand(videoPaths, outputPath) {
    /**
     * Create FFmpeg command for concatenating videos with crossfade transitions.
     * This creates a complex filter that adds fade-in and fade-out effects.
     */
    const transitionDuration = 1.0; // 1 second crossfade

    if (videoPaths.length === 1) {
      // Single video, no transitions needed
      return `ffmpeg -i "${videoPaths[0]}" -c copy "${outputPath}"`;
    }

    // For multiple videos, use a simpler approach with concat filter
    // First, create a file list for FFmpeg concat
    const fileListPath = path.join(path.dirname(outputPath), 'filelist.txt');
    
    // Convert all paths to absolute paths and normalize them
    const absoluteVideoPaths = videoPaths.map(videoPath => {
      // If path is already absolute, use it as is
      if (path.isAbsolute(videoPath)) {
        return videoPath;
      }
      // Otherwise, make it absolute relative to the output directory
      return path.resolve(this.outputDir, videoPath.split('\\')[1]);
    });
    
    // Create file list content with proper path formatting for Windows
    const fileListContent = absoluteVideoPaths.map(videoPath => {
      // Use forward slashes for FFmpeg compatibility on Windows
      const normalizedPath = videoPath.replace(/\\/g, '/');
      return `file '${normalizedPath}'`;
    }).join('\n');
    
    console.log('File list content:', fileListContent);
    console.log('File list path:', fileListPath);
    
    // Write the file list
    await fs.writeFile(fileListPath, fileListContent);

    // Use concat demuxer for simple concatenation
    return `ffmpeg -f concat -safe 0 -i "${fileListPath}" -c copy "${outputPath}"`;
  }

  async generate(scenes, taskId, taskManager, wsManager) {
    try {
      // This is a simplified implementation
      // In a real implementation, you would integrate with RunwayML API

      // For now, we'll simulate video generation
      await new Promise(resolve => setTimeout(resolve, 5000)); // Simulate processing

      // Create a placeholder video file
      const filename = `video_${taskId}.mp4`;

      // Generate images for scenes using ImageGenerator
      const ImageGenerator = require('./ImageGenerator');
      const imageGenerator = new ImageGenerator();

      // Update task status
      taskManager.updateTask(taskId, {
        progress: 40,
        message: 'Generating images for scenes...'
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

      const imagePaths = await imageGenerator.generateVisualsForScenes(scenes);
      console.log("Generating images for scenes...")

      if (!imagePaths || imagePaths.length === 0) {
        throw new Error('Failed to generate images for scenes');
      }

      // In a real implementation, you would download the actual video from RunwayML
      // For now, create a placeholder file

      const videoScripts = [];

      console.log('Processing scenes:', scenes)
      for (const scene of scenes) {
        console.log('Processing scene:', scene)
        const videScript = await this.openai.chat.completions.create({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: `Your role is to generate a prompt for video generation. The input is a scene description. A 9.5 second video must be generated from the scene description. This requires a prompt for video generation. The video must be realistic; sudden appearances and disappearances of people or objects are not permitted. Surrealistic phenomena, such as people flying, are also not permitted. The video must have a transition effect that lasts 0.5 seconds.The number of people and objects must not change.
                input example: 'This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene (door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: A close-up of a brightly lit carousel spinning, with kids waving and laughing as the ride turns. The scene feels joyful and energetic. Overlay text reads: 'Games & Rides for Everyone!
                output example: 'The entire scene is realistic, sharp, and natural. A close-up of a brightly lit carousel spinning with colorful lights. Children are waving and laughing with joy as the ride turns, creating a lively and energetic atmosphere. The environment looks like a real outdoor fun fair on a sunny day. Overlay text in bold, playful font reads: 'Games & Rides for Everyone!' above is for 4.5 seconds. A smooth cinematic transition effect of 0.5 seconds is used at the end of the video.'`
            },
            {
              role: 'user',
              content: `
                Now Try with this ${scene.text}`,
              max_tokens: 1500,
              temperature: 0.7
            }
          ]
        });
        videoScripts.push("This is a high-quality cinematic scene captured by a professional camera, not a photo, not a cartoon. The motion is continuous and natural — no sudden appearances or disappearances of people or objects, no surreal effects. " + videScript.choices[0].message.content);
      }
      console.log('Generated video scripts:', videoScripts)
      console.log('---------------- --------------------------------')
      // Update task status
      taskManager.updateTask(taskId, {
        progress: 60,
        message: 'Generating videos from images...'
      });
      wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

      const videoPaths = await this.generateVideoWithRunway(videoScripts, imagePaths);
      // const videoPaths = ['output\\video_01.mp4', 'output\\video_02.mp4', 'output\\video_03.mp4']
      console.log('videoPaths', videoPaths);

      // Concatenate videos into a single file
      if (videoPaths && videoPaths.length > 0) {
        // Update task status
        taskManager.updateTask(taskId, {
          progress: 80,
          message: 'Concatenating videos with transitions...'
        });
        wsManager.broadcastTaskUpdate(taskId, taskManager.getTask(taskId));

        const finalVideoPath = await this.concatenateVideos(videoPaths);
        return finalVideoPath;
      } else {
        throw new Error('No videos were generated successfully');
      }
    } catch (error) {
      console.error('RunwayML video generation error:', error);
      throw new Error('Failed to generate video with RunwayML');
    }
  }
}

module.exports = VideoGenerator;

