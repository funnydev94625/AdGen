from runwayml import RunwayML, TaskFailedError
from typing import Optional, List
import time
import os
import base64
import mimetypes


class RunwayGenerator:
    def __init__(self, config):
        self.config = config
        self.client = RunwayML(api_key="key_e235cd7ef45451ae9e7997f3be715387f50267689db439de60035b74b8cdf15323ad03cc3ddf3748e0e94c5eeba51e762ae11772fd50944391e18c82b2de5e7a")
    
    def get_image_as_data_uri(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        content_type = mimetypes.guess_file_type(image_path)[0]
        return f"data:{content_type};base64,{base64_image}"

    def generate_image(self, prompt: str, filename: Optional[str] = None, ref_image: Optional[str] = None) -> Optional[str]:
        """
        Generate an image from a text prompt with retry logic.
        """
        print('----image prompt---', prompt)
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                task = None
                print(f"Image generation attempt {retry_count + 1}/{max_retries}")
                print(f"Reference image length: {len(ref_image) if ref_image else 0}")
                
                if ref_image == "None":
                    task = self.client.text_to_image.create(
                        model='gen4_image',
                        ratio='1280:720',
                        prompt_text=prompt,
                    ).wait_for_task_output()
                else:
                    task = self.client.text_to_image.create(
                        model='gen4_image',
                        ratio='1280:720',
                        prompt_text=prompt + "Draw different from the reference image or Draw similar to the reference image",
                        reference_images=[
                            {
                                'uri': ref_image,
                                'tag': 'scene_5s_ago',
                            },
                        ],
                    ).wait_for_task_output()
                
                print('Task complete:', task)
                print('Image URL:', task.output[0])
                print('----------', filename)
                
                result = self._download_and_save_image(task.output[0], filename)
                if result:
                    return result
                else:
                    raise Exception("Failed to download image")
                    
            except TaskFailedError as e:
                retry_count += 1
                print(f'❌ Image generation failed (attempt {retry_count}/{max_retries})')
                print(f'Error details: {e.task_details}')
                
                if retry_count < max_retries:
                    print(f"⏳ Retrying in 5 seconds...")
                    time.sleep(self.config.retry_delay // 2)  # Shorter delay for image generation
                else:
                    print(f"💥 Max retries reached for image generation. Returning None.")
                    return None
                    
            except Exception as e:
                retry_count += 1
                print(f'❌ Error generating image (attempt {retry_count}/{max_retries}): {str(e)}')
                
                if retry_count < max_retries:
                    print(f"⏳ Retrying in 5 seconds...")
                    time.sleep(self.config.retry_delay // 2)  # Shorter delay for image generation
                else:
                    print(f"💥 Max retries reached for image generation. Returning None.")
            return None
        
            return None
    
    def _download_and_save_image(self, image_url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download image from URL and save to local file."""
        try:
            import requests
            
            # Create output directory if it doesn't exist
            os.makedirs(self.config.temp_dir, exist_ok=True)
            
            # Download image
            response = requests.get(image_url)
            if response.status_code == 200:
                image_path = os.path.join(self.config.temp_dir, filename)
                print('----------', image_path)
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_url, image_path
            else:
                print(f"Failed to download image from {image_url}")
                return None
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None
    
    def generate_visuals_for_scenes(self, scenes: List[str]) -> List[Optional[str]]:
        
        """
        Generate images for all scenes with visual consistency.
        """
        image_paths = []
        ref_image = "None"
        for i, scene in enumerate(scenes):
            base_filename = f"image_{i+1:02d}.png"
            print(f"Generating image for scene {i+1}/{len(scenes)}: {scene.text[:50]}...")
            print(scene.text)
            image_path, image_path_download = self.generate_image(scene.text, base_filename, ref_image=ref_image)
            image_paths.append(image_path_download)
            ref_image = self.get_image_as_data_uri(image_path_download)
            
            # Add delay to respect API rate limits
            if i < len(scenes) - 1:  # Don't delay after the last image
                time.sleep(2)  # 2 second delay between requests
        
        successful_generations = sum(1 for path in image_paths if path is not None)
        print(f"Successfully generated {successful_generations}/{len(scenes)} images")
        return image_paths
    
    def generate_videos(self, scenes: List, image_paths: List[str], video_script: List[str]) -> Optional[str]:
        """
        Generate a video from a list of scenes, images, audio, and narration.
        """
        print(scenes)
        print(image_paths)
        video_urls = []
        video_paths = []
        max_retries = self.config.max_retries  # Maximum number of retry attempts
        
        for i in range(len(scenes)):
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:    
                    print(f"Generating video for scene {i+1}/{len(scenes)} (attempt {retry_count + 1}/{max_retries}): {scenes[i].text[:50]}...")
                    print(f"Video script: {video_script[i]}")
                    print(f"Image path: {image_paths[i]}")
                    
                    task = self.client.image_to_video.create(
                        model='gen3a_turbo',
                        ratio='1280:768',
                        prompt_text=video_script[i],
                        prompt_image=[
                                {
                                    'uri': self.get_image_as_data_uri(image_paths[i]),
                                    'position': 'first'
                                },
                            ],
                            duration= 10
                    ).wait_for_task_output()
                    
                    print('Task complete:', task)
                    print('Video URL:', task.output[0])
                    
                    video_url, video_path = self._download_and_save_video(task.output[0], f"video_{i+1:02d}.mp4")
                    
                    if video_url and video_path:
                        video_urls.append(video_url)
                        video_paths.append(video_path)
                        success = True
                        print(f"✅ Successfully generated video for scene {i+1}")
                    else:
                        raise Exception("Failed to download video")
                        
                except TaskFailedError as e:
                    retry_count += 1
                    print(f"❌ Task failed for scene {i+1} (attempt {retry_count}/{max_retries})")
                    print(f"Error details: {e.task_details}")
                    
                    if retry_count < max_retries:
                        print(f"⏳ Retrying in 10 seconds...")
                        time.sleep(self.config.retry_delay)
                    else:
                        print(f"💥 Max retries reached for scene {i+1}. Skipping this scene.")
                        video_paths.append(None)  # Add None for failed scene
                        
                except Exception as e:
                    retry_count += 1
                    print(f"❌ Error generating video for scene {i+1} (attempt {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count < max_retries:
                        print(f"⏳ Retrying in 10 seconds...")
                        time.sleep(self.config.retry_delay)
                    else:
                        print(f"💥 Max retries reached for scene {i+1}. Skipping this scene.")
                        video_paths.append(None)  # Add None for failed scene
            
            # Add delay to respect API rate limits (only if successful)
            if success and i < len(scenes) - 1:
                print("⏳ Waiting 5 seconds before next request...")
                time.sleep(5)

        successful_generations = sum(1 for path in video_paths if path is not None)
        print(f"🎬 Successfully generated {successful_generations}/{len(scenes)} videos")
        
        return video_paths
    
    def generate_videos_without_images(self, scenes: List, video_script: List[str]) -> Optional[str]:
        """
        Generate a video from a list of scenes and audio.
        """
        print(scenes)
        print(video_script)
        video_paths = []
        max_retries = self.config.max_retries  # Maximum number of retry attempts
        
        for i in range(len(scenes)):
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    print(f"Generating video for scene {i+1}/{len(scenes)} (attempt {retry_count + 1}/{max_retries}): {scenes[i].text[:50]}...")
                    print(f"Video script: {video_script[i]}")
                    
                    task = self.client.text_to_video.create(
                        model='veo3',
                        ratio='1280:720',
                        prompt_text=video_script[i],
                        duration=8,
                    ).wait_for_task_output()
                    
                    print('Task complete:', task)
                    print('Video URL:', task.output[0])
                    
                    video_url, video_path = self._download_and_save_video(task.output[0], f"video_{i+1:02d}.mp4")
                    
                    if video_url and video_path:
                        video_paths.append(video_path)
                        success = True
                        print(f"✅ Successfully generated video for scene {i+1}")
                    else:
                        raise Exception("Failed to download video")
                        
                except TaskFailedError as e:
                    retry_count += 1
                    print(f"❌ Task failed for scene {i+1} (attempt {retry_count}/{max_retries})")
                    print(f"Error details: {e.task_details}")
                    
                    if retry_count < max_retries:
                        print(f"⏳ Retrying in 10 seconds...")
                        time.sleep(self.config.retry_delay)
                    else:
                        print(f"💥 Max retries reached for scene {i+1}. Skipping this scene.")
                        video_paths.append(None)  # Add None for failed scene
                        
                except Exception as e:
                    retry_count += 1
                    print(f"❌ Error generating video for scene {i+1} (attempt {retry_count}/{max_retries}): {str(e)}")
                    
                    if retry_count < max_retries:
                        print(f"⏳ Retrying in 10 seconds...")
                        time.sleep(self.config.retry_delay)
                    else:
                        print(f"💥 Max retries reached for scene {i+1}. Skipping this scene.")
                        video_paths.append(None)  # Add None for failed scene
            
            # Add delay to respect API rate limits (only if successful)
            if success and i < len(scenes) - 1:
                print("⏳ Waiting 5 seconds before next request...")
                time.sleep(5)
        
        successful_generations = sum(1 for path in video_paths if path is not None)
        print(f"🎬 Successfully generated {successful_generations}/{len(scenes)} videos")
        
        return video_paths

    def _download_and_save_video(self, video_url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download video from URL and save to local file."""
        try:
            import requests
            
            # Create output directory if it doesn't exist
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # Download video
            response = requests.get(video_url)
            if response.status_code == 200:
                video_path = os.path.join(self.config.output_dir, filename)
                with open(video_path, 'wb') as f:
                    f.write(response.content)
                return video_url, video_path
            else:
                print(f"Failed to download video from {video_url}")
                return None
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return None