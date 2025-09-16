"""
Visual generation module using OpenAI DALL-E API.
"""

import os
import time
from typing import Optional, List
from PIL import Image
import io
import requests
from openai import OpenAI

class VisualGenerator:
    """Generates images using OpenAI DALL-E API for video scenes."""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        
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
        # return any(keyword in text_lower for keyword in ad_keywords)
        return True
    
    def _analyze_ad_content(self, content: str) -> None:
        """Analyze advertisement content for visual consistency."""
        analysis_prompt = f"""
        Analyze this advertisement content and extract visual elements for promotional video generation:
        
        Content: {content}
        
        Please identify and extract:
        1. Brand/Product elements (logos, products, key visuals)
        2. Target audience (who this is for)
        3. Setting/location (where this takes place)
        4. Visual style (modern, classic, playful, professional, etc.)
        5. Color palette (brand colors, mood colors)
        6. Lighting (bright, warm, dramatic, etc.)
        7. Camera style (close-up, wide shot, etc.)
        8. Text elements (headlines, prices, contact info)
        
        Format your response as:
        BRAND: [brand/product elements]
        AUDIENCE: [target audience]
        SETTING: [setting description]
        STYLE: [visual style]
        COLORS: [color palette]
        LIGHTING: [lighting description]
        CAMERA: [camera style]
        TEXT: [key text elements]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            self._parse_ad_analysis(analysis)
            
            print("Advertisement visual analysis completed:")
            print(f"Brand: {self.visual_context.get('brand', 'N/A')}")
            print(f"Audience: {self.visual_context.get('audience', 'N/A')}")
            print(f"Style: {self.visual_context.get('style', 'N/A')}")
            
        except Exception as e:
            print(f"Error analyzing ad content: {str(e)}")
            self._set_default_ad_context()
    
    def _analyze_narrative_content(self, content: str) -> None:
        """Analyze narrative content for visual consistency."""
        analysis_prompt = f"""
        Analyze this story and extract consistent visual elements for video generation:
        
        Story: {content}
        
        Please identify and extract:
        1. Main characters (describe their appearance, clothing, age, etc.)
        2. Setting/location (describe the environment, time period, atmosphere)
        3. Visual style (realistic, cartoon, cinematic, etc.)
        4. Color palette (dominant colors, mood)
        5. Lighting (time of day, mood lighting)
        6. Camera style (close-up, wide shot, etc.)
        
        Format your response as:
        CHARACTERS: [character descriptions]
        SETTING: [setting description]
        STYLE: [visual style]
        COLORS: [color palette]
        LIGHTING: [lighting description]
        CAMERA: [camera style]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            self._parse_visual_analysis(analysis)
            
            print("Narrative visual analysis completed:")
            print(f"Characters: {self.visual_context.get('characters', 'N/A')}")
            print(f"Setting: {self.visual_context.get('setting', 'N/A')}")
            print(f"Style: {self.visual_context.get('style', 'N/A')}")
            
        except Exception as e:
            print(f"Error analyzing narrative content: {str(e)}")
            self._set_default_visual_context()
    
    def _parse_ad_analysis(self, analysis: str) -> None:
        """Parse the advertisement analysis response and update context."""
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('BRAND:'):
                self.visual_context['brand'] = line.replace('BRAND:', '').strip()
            elif line.startswith('AUDIENCE:'):
                self.visual_context['audience'] = line.replace('AUDIENCE:', '').strip()
            elif line.startswith('SETTING:'):
                self.visual_context['setting'] = line.replace('SETTING:', '').strip()
            elif line.startswith('STYLE:'):
                self.visual_context['style'] = line.replace('STYLE:', '').strip()
            elif line.startswith('COLORS:'):
                self.visual_context['color_palette'] = line.replace('COLORS:', '').strip()
            elif line.startswith('LIGHTING:'):
                self.visual_context['lighting'] = line.replace('LIGHTING:', '').strip()
            elif line.startswith('CAMERA:'):
                self.visual_context['camera_angle'] = line.replace('CAMERA:', '').strip()
            elif line.startswith('TEXT:'):
                self.visual_context['text_elements'] = line.replace('TEXT:', '').strip()
    
    def _parse_visual_analysis(self, analysis: str) -> None:
        """Parse the visual analysis response and update context."""
        lines = analysis.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('CHARACTERS:'):
                self.visual_context['characters'] = line.replace('CHARACTERS:', '').strip()
            elif line.startswith('SETTING:'):
                self.visual_context['setting'] = line.replace('SETTING:', '').strip()
            elif line.startswith('STYLE:'):
                self.visual_context['style'] = line.replace('STYLE:', '').strip()
            elif line.startswith('COLORS:'):
                self.visual_context['color_palette'] = line.replace('COLORS:', '').strip()
            elif line.startswith('LIGHTING:'):
                self.visual_context['lighting'] = line.replace('LIGHTING:', '').strip()
            elif line.startswith('CAMERA:'):
                self.visual_context['camera_angle'] = line.replace('CAMERA:', '').strip()
    
    def _set_default_ad_context(self) -> None:
        """Set default visual context for advertisements."""
        self.visual_context = {
            'brand': 'professional brand elements',
            'audience': 'general audience',
            'setting': 'modern, clean environment',
            'style': 'professional, realistic, eye-catching',
            'color_palette': 'vibrant, attention-grabbing colors',
            'lighting': 'well-lit, professional lighting',
            'camera_angle': 'medium shot',
            'text_elements': 'clear, readable text',
            'previous_scene_elements': []
        }
    
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
        
    def generate_visual(self, scene_text: str, scene_number: int) -> Optional[str]:
        """
        Generate an image for a scene using DALL-E.
        
        Args:
            scene_text: The text content of the scene
            scene_number: The scene number for naming
            
        Returns:
            Path to the generated image file, or None if generation failed
        """
        try:
            # Create enhanced prompt for image generation
            image_prompt = self._create_image_prompt(scene_text, scene_number)
            
            # Generate image using DALL-E API
            image_url = self._call_dalle_api(image_prompt)
            
            if not image_url:
                return None
                
            # Download and save the image
            image_path = self._download_and_save_image(image_url, scene_number)
            
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
        
        # Add advertisement-specific keywords
        ad_keywords = [
            "professional advertisement", "high quality promotional image", 
            "eye-catching", "commercial photography", "marketing material",
            "clean composition", "professional lighting"
        ]
        # Combine all elements
        if ad_elements:
            consistency_text = ", ".join(ad_elements)
            enhanced_prompt = f"{prompt}, {consistency_text}, {', '.join(ad_keywords[:3])}"
        else:
            enhanced_prompt = f"{prompt}, {', '.join(ad_keywords)}"
        
        # Ensure prompt isn't too long (DALL-E has limits)
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
        
        # Combine all elements
        if consistency_elements:
            consistency_text = ", ".join(consistency_elements)
            enhanced_prompt = f"{prompt}, {consistency_text}"
        else:
            # Fallback to basic enhancement
            visual_keywords = [
                "cinematic", "high quality", "detailed", "professional photography",
                "vibrant colors", "well-lit", "clear focus"
            ]
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
    
    def _download_and_save_image(self, image_url: str, scene_number: int) -> Optional[str]:
        """Download image from URL and save to local file."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.config.temp_dir, exist_ok=True)
            
            # Download image with increased timeout and retry logic
            max_retries = 3
            timeout = 30  # Increased from 30 to 60 seconds
            
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
            
            # Save image
            filename = f"scene_{scene_number:02d}.png"
            filepath = os.path.join(self.config.temp_dir, filename)
            
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
                print(f"Successfully downloaded and saved image: {filename}")
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
        
        print(f"Generating {len(scenes)} images with visual consistency...")
        
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
    
    def cleanup_temp_images(self, image_paths: List[Optional[str]]):
        """Clean up temporary image files."""
        for image_path in image_paths:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error cleaning up image {image_path}: {str(e)}")
