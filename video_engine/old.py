"""
RunwayML image generation module for creating images from text prompts.
"""

import os
import time
import requests
from typing import Optional, List
from PIL import Image
import io

class RunwayGenerator:
    """Generates images using RunwayML API."""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.runway_api_key
        self.base_url = "https://api.runwayml.com/v1"
        
        # Visual consistency tracking
        self.visual_context = {
            'characters': [],
            'setting': '',
            'style': '',
            'color_palette': '',
            'lighting': '',
            'camera_angle': '',
            'previous_scene_elements': []
        }
    
    def analyze_story_for_consistency(self, scenes: List) -> None:
        """
        Analyze all scenes to extract consistent visual elements.
        
        Args:
            scenes: List of Scene objects
        """
        try:
            # Combine all scene text for analysis
            full_story = ' '.join([scene.text for scene in scenes])
            
            # Check if this is advertisement content
            if self._is_advertisement_content(full_story):
                self._analyze_ad_content(full_story)
            else:
                self._analyze_narrative_content(full_story)
            
        except Exception as e:
            print(f"Error analyzing story for consistency: {str(e)}")
            # Set default values if analysis fails
            self._set_default_visual_context()
    
    def _is_advertisement_content(self, text: str) -> bool:
        """Check if content is advertisement/promotional."""
        ad_keywords = [
            'flyer', 'menu', 'sale', 'promo', 'promotion', 'advertisement', 'ad',
            'event', 'opening', 'discount', 'offer', 'deal', 'special', 'limited time',
            'buy now', 'shop', 'store', 'restaurant', 'cafe', 'boutique', 'fair',
            'festival', 'concert', 'show', 'exhibition', 'launch', 'announcement'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in ad_keywords)
    
    def _analyze_ad_content(self, content: str) -> None:
        """Analyze advertisement content for visual consistency."""
        # For RunwayML, we'll use a simpler analysis approach
        # Extract key elements from the content
        self.visual_context.update({
            'brand': 'professional brand elements',
            'audience': 'general audience',
            'setting': 'modern, clean environment',
            'style': 'professional, modern, eye-catching',
            'color_palette': 'vibrant, attention-grabbing colors',
            'lighting': 'bright, professional lighting',
            'camera_angle': 'medium shot',
            'text_elements': 'clear, readable text'
        })
        
        print("Advertisement visual analysis completed:")
        print(f"Brand: {self.visual_context.get('brand', 'N/A')}")
        print(f"Audience: {self.visual_context.get('audience', 'N/A')}")
        print(f"Style: {self.visual_context.get('style', 'N/A')}")
    
    def _analyze_narrative_content(self, content: str) -> None:
        """Analyze narrative content for visual consistency."""
        # For RunwayML, we'll use a simpler analysis approach
        self.visual_context.update({
            'characters': 'realistic human characters',
            'setting': 'realistic environment',
            'style': 'cinematic, professional photography',
            'color_palette': 'natural colors',
            'lighting': 'well-lit, natural lighting',
            'camera_angle': 'medium shot'
        })
        
        print("Narrative visual analysis completed:")
        print(f"Characters: {self.visual_context.get('characters', 'N/A')}")
        print(f"Setting: {self.visual_context.get('setting', 'N/A')}")
        print(f"Style: {self.visual_context.get('style', 'N/A')}")
    
    def _set_default_visual_context(self) -> None:
        """Set default visual context if analysis fails."""
        self.visual_context = {
            'characters': 'realistic human characters',
            'setting': 'realistic environment',
            'style': 'cinematic, professional photography',
            'color_palette': 'natural colors',
            'lighting': 'well-lit, natural lighting',
            'camera_angle': 'medium shot',
            'previous_scene_elements': []
        }
    
    def generate_image(self, prompt: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a single image from a text prompt using RunwayML.
        
        Args:
            prompt: The text prompt for image generation
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        try:
            # Create enhanced prompt for image generation
            image_prompt = self._create_image_prompt(prompt, 1)
            
            # Generate image using RunwayML API
            image_url = self._call_runway_api(image_prompt)
            
            if not image_url:
                return None
                
            # Download and save the image
            image_path = self._download_and_save_image(image_url, filename)
            
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None
    
    def generate_multiple_images(self, prompts: List[str], base_filename: str = "image") -> List[Optional[str]]:
        """
        Generate multiple images from a list of prompts.
        
        Args:
            prompts: List of text prompts
            base_filename: Base filename for generated images
            
        Returns:
            List of image file paths (or None for failed generations)
        """
        image_paths = []
        
        print(f"Generating {len(prompts)} images...")
        
        for i, prompt in enumerate(prompts):
            print(f"Generating image {i+1}/{len(prompts)}: {prompt[:50]}...")
            
            filename = f"{base_filename}_{i+1:02d}" if len(prompts) > 1 else base_filename
            image_path = self.generate_image(prompt, filename)
            image_paths.append(image_path)
            
            # Add delay to respect API rate limits
            if i < len(prompts) - 1:  # Don't delay after the last image
                time.sleep(2)  # 2 second delay between requests
        
        successful_generations = sum(1 for path in image_paths if path is not None)
        print(f"Successfully generated {successful_generations}/{len(prompts)} images")
        
        return image_paths
    
    def generate_visual(self, scene_text: str, scene_number: int) -> Optional[str]:
        """
        Generate an image for a scene using RunwayML.
        
        Args:
            scene_text: The text content of the scene
            scene_number: The scene number for naming
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        try:
            # Create enhanced prompt for image generation
            image_prompt = self._create_image_prompt(scene_text, scene_number)
            
            # Generate image using RunwayML API
            image_url = self._call_runway_api(image_prompt)
            
            if not image_url:
                return None
                
            # Download and save the image
            image_path = self._download_and_save_image(image_url, f"scene_{scene_number:02d}")
            
            return image_path
            
        except Exception as e:
            print(f"Error generating visual for scene {scene_number}: {str(e)}")
            return None
    
    def _create_image_prompt(self, scene_text: str, scene_number: int) -> str:
        """Create an enhanced prompt for image generation with visual consistency."""
        # Start with the scene text
        prompt = scene_text.strip()
        
        # Check if this is advertisement content
        if self._is_advertisement_content(prompt):
            return self._create_ad_image_prompt(prompt, scene_number)
        else:
            return self._create_narrative_image_prompt(prompt, scene_number)
    
    def _create_ad_image_prompt(self, scene_text: str, scene_number: int) -> str:
        """Create image prompt specifically for advertisement content."""
        # Start with the scene text
        prompt = scene_text.strip()
        
        # Add advertisement-specific visual elements
        ad_elements = []
        
        # Add brand elements
        if self.visual_context.get('brand'):
            ad_elements.append(f"featuring {self.visual_context['brand']}")
        
        # Add target audience appeal
        if self.visual_context.get('audience'):
            ad_elements.append(f"appealing to {self.visual_context['audience']}")
        
        # Add setting consistency
        if self.visual_context.get('setting'):
            ad_elements.append(f"in {self.visual_context['setting']}")
        
        # Add professional ad style
        if self.visual_context.get('style'):
            ad_elements.append(f"in {self.visual_context['style']} style")
        
        # Add brand colors
        if self.visual_context.get('color_palette'):
            ad_elements.append(f"with {self.visual_context['color_palette']}")
        
        # Add professional lighting
        if self.visual_context.get('lighting'):
            ad_elements.append(f"with {self.visual_context['lighting']}")
        
        # Add camera angle
        if self.visual_context.get('camera_angle'):
            ad_elements.append(f"shot from {self.visual_context['camera_angle']}")
        
        # Add text overlay elements
        if self.visual_context.get('text_elements'):
            ad_elements.append(f"with {self.visual_context['text_elements']}")
        
        # Add RunwayML-specific keywords for high quality
        runway_keywords = [
            "photorealistic", "high quality", "detailed", "professional photography",
            "realistic", "sharp focus", "natural lighting", "cinematic quality"
        ]
        
        # Combine all elements
        if ad_elements:
            consistency_text = ", ".join(ad_elements)
            enhanced_prompt = f"{prompt}, {consistency_text}, {', '.join(runway_keywords[:3])}"
        else:
            enhanced_prompt = f"{prompt}, {', '.join(runway_keywords)}"
        
        # Ensure prompt isn't too long
        if len(enhanced_prompt) > 1000:
            enhanced_prompt = enhanced_prompt[:1000] + "..."
            
        return enhanced_prompt
    
    def _create_narrative_image_prompt(self, scene_text: str, scene_number: int) -> str:
        """Create image prompt for narrative content."""
        # Start with the scene text
        prompt = scene_text.strip()
        
        # Add consistent visual elements
        consistency_elements = []
        
        # Add character consistency
        if self.visual_context.get('characters'):
            consistency_elements.append(f"featuring {self.visual_context['characters']}")
        
        # Add setting consistency
        if self.visual_context.get('setting'):
            consistency_elements.append(f"in {self.visual_context['setting']}")
        
        # Add style consistency
        if self.visual_context.get('style'):
            consistency_elements.append(f"in {self.visual_context['style']} style")
        
        # Add color palette consistency
        if self.visual_context.get('color_palette'):
            consistency_elements.append(f"with {self.visual_context['color_palette']} color palette")
        
        # Add lighting consistency
        if self.visual_context.get('lighting'):
            consistency_elements.append(f"with {self.visual_context['lighting']}")
        
        # Add camera angle consistency
        if self.visual_context.get('camera_angle'):
            consistency_elements.append(f"shot from {self.visual_context['camera_angle']}")
        
        # Add scene transition elements for continuity
        if scene_number > 1:
            consistency_elements.append("maintaining visual continuity with previous scenes")
        
        # Add RunwayML-specific keywords
        runway_keywords = [
            "photorealistic", "high quality", "detailed", "professional photography",
            "realistic", "sharp focus", "natural lighting", "cinematic quality"
        ]
        
        # Combine all elements
        if consistency_elements:
            consistency_text = ", ".join(consistency_elements)
            enhanced_prompt = f"{prompt}, {consistency_text}, {', '.join(runway_keywords[:3])}"
        else:
            enhanced_prompt = f"{prompt}, {', '.join(runway_keywords)}"
        
        # Ensure prompt isn't too long
        if len(enhanced_prompt) > 1000:
            enhanced_prompt = enhanced_prompt[:1000] + "..."
            
        return enhanced_prompt
    
    def _call_runway_api(self, prompt: str) -> Optional[str]:
        """Call RunwayML API to generate an image."""
        try:
            # RunwayML API endpoint for image generation
            url = f"{self.base_url}/images/generations"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "runway-gen3a-turbo",  # RunwayML's latest model
                "prompt": prompt,
                "size": self.config.image_size,
                "quality": self.config.image_quality,
                "style": self.config.image_style,
                "n": 1
            }
            
            print(f"Calling RunwayML API with prompt: {prompt[:100]}...")
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('data') and len(result['data']) > 0:
                image_url = result['data'][0].get('url')
                if image_url:
                    print("RunwayML API returned image URL successfully")
                    return image_url
                else:
                    print("RunwayML API returned no image URL")
                    return None
            else:
                print("RunwayML API returned no data")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error calling RunwayML API: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error calling RunwayML API: {str(e)}")
            return None
    
    def _download_and_save_image(self, image_url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download image from URL and save to local file."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.config.temp_dir, exist_ok=True)
            
            # Download image with increased timeout and retry logic
            max_retries = 3
            timeout = 60
            
            for attempt in range(max_retries):
                try:
                    print(f"Downloading image (attempt {attempt + 1}/{max_retries})...")
                    print(f"Image URL: {image_url}")
                    
                    # Add headers to mimic a browser request
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    
                    # Use proxy configuration for downloading
                    proxies = {
                        "http": "http://fwmkyuda:5olb28q1kp2i@45.43.167.180:6362",
                        "https": "http://fwmkyuda:5olb28q1kp2i@45.43.167.180:6362"
                    }
                    
                    response = requests.get(image_url, timeout=timeout, headers=headers, proxies=proxies, stream=True)
                    response.raise_for_status()
                    
                    # Check if we got valid content
                    print(f"Response status: {response.status_code}")
                    print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                    print(f"Content length: {response.headers.get('content-length', 'unknown')}")
                    
                    break
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        print(f"Timeout on attempt {attempt + 1}, retrying...")
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        raise
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Request error on attempt {attempt + 1}: {str(e)}, retrying...")
                        time.sleep(2)
                        continue
                    else:
                        raise
            
            # Generate filename if not provided
            if not filename:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"runway_image_{timestamp}"
            
            # Save image
            filepath = os.path.join(self.config.temp_dir, f"{filename}.png")
            
            print(f"Saving image to: {filepath}")
            
            # Use streaming to save the image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
            
            print(f"Image saved successfully. File size: {os.path.getsize(filepath)} bytes")
            
            # Verify image is valid
            try:
                with Image.open(filepath) as img:
                    img.verify()
                print(f"✅ Image saved: {filepath}")
                return filepath
            except Exception as e:
                print(f"Downloaded image is invalid: {str(e)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
                
        except Exception as e:
            print(f"Error downloading image after {max_retries} attempts: {str(e)}")
            return None
    
    def generate_visuals_for_scenes(self, scenes: List) -> List[Optional[str]]:
        """
        Generate images for all scenes with visual consistency.
        
        Args:
            scenes: List of Scene objects
            
        Returns:
            List of image file paths (or None for failed generations)
        """
        image_paths = []
        
        print(f"Generating {len(scenes)} images with visual consistency using RunwayML...")
        
        # First, analyze the story for visual consistency
        print("Analyzing story for visual consistency...")
        self.analyze_story_for_consistency(scenes)
        print()
        
        for i, scene in enumerate(scenes):
            print(f"Generating image for scene {i+1}/{len(scenes)}: {scene.text[:50]}...")
            print(scene.text)
            
            image_path = self.generate_visual(scene.text, scene.scene_number)
            image_paths.append(image_path)
            
            # Add delay to respect API rate limits
            if i < len(scenes) - 1:  # Don't delay after the last image
                time.sleep(2)  # 2 second delay between requests
        
        successful_generations = sum(1 for path in image_paths if path is not None)
        print(f"Successfully generated {successful_generations}/{len(scenes)} images")
        
        return image_paths
    
    def reset_visual_context(self):
        """Reset visual context for a new video generation."""
        self.visual_context = {
            'characters': [],
            'setting': '',
            'style': '',
            'color_palette': '',
            'lighting': '',
            'camera_angle': '',
            'previous_scene_elements': []
        }
        print("Visual context reset for new video generation")
    
    def cleanup_images(self, image_paths: List[Optional[str]]):
        """Clean up generated image files."""
        for image_path in image_paths:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error cleaning up image {image_path}: {str(e)}")
    
    def cleanup_temp_images(self, image_paths: List[Optional[str]]):
        """Clean up temporary image files."""
        for image_path in image_paths:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error cleaning up image {image_path}: {str(e)}")
