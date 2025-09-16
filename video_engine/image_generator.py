"""
Standalone image generation module using OpenAI DALL-E API.
"""

import os
import time
from typing import Optional, List
from PIL import Image
import io
from openai import OpenAI

class ImageGenerator:
    """Generates standalone images using OpenAI DALL-E API."""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        
    def generate_image(self, prompt: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a single image from a text prompt.
        
        Args:
            prompt: The text prompt for image generation
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        try:
            # Create enhanced prompt for image generation
            image_prompt = self._create_image_prompt(prompt)
            
            # Generate image using DALL-E API
            image_url = self._call_dalle_api(image_prompt)
            
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
    
    def _create_image_prompt(self, text: str) -> str:
        """Create an enhanced prompt for image generation."""
        # Clean and enhance the text for image generation
        prompt = text.strip()
        
        # Add visual enhancement keywords
        visual_keywords = [
            "cinematic", "high quality", "detailed", "professional photography",
            "vibrant colors", "well-lit", "realistic focus", "beautiful composition"
        ]
        
        # Add some visual keywords to improve image quality
        enhanced_prompt = f"{prompt}, {', '.join(visual_keywords[:3])}"
        
        # Ensure prompt isn't too long (DALL-E has limits)
        if len(enhanced_prompt) > 1000:
            enhanced_prompt = enhanced_prompt[:1000] + "..."
            
        return enhanced_prompt
    
    def _call_dalle_api(self, prompt: str) -> Optional[str]:
        """Call OpenAI DALL-E API to generate an image."""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=self.config.image_size,
                quality=self.config.image_quality,
                style=self.config.image_style,
                n=1
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].url
            else:
                print("DALL-E API returned no data")
                return None
                
        except Exception as e:
            print(f"Error calling DALL-E API: {str(e)}")
            return None
    
    def _download_and_save_image(self, image_url: str, filename: Optional[str] = None) -> Optional[str]:
        """Download image from URL and save to local file."""
        try:
            import requests
            
            # Create output directory if it doesn't exist
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not filename:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}"
            
            # Save image
            filepath = os.path.join(self.config.output_dir, f"{filename}.png")
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
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
            print(f"Error downloading image: {str(e)}")
            return None
    
    def cleanup_images(self, image_paths: List[Optional[str]]):
        """Clean up generated image files."""
        for image_path in image_paths:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error cleaning up image {image_path}: {str(e)}")
