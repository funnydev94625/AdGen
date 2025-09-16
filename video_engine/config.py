"""
Configuration settings for the video generation engine.
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class for video generation settings."""
    
    def __init__(self):
        # OpenAI API settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # RunwayML API settings
        self.runway_api_key = os.getenv("RUNWAY_API_KEY")
        if not self.runway_api_key:
            print("Warning: RUNWAY_API_KEY environment variable not set. RunwayML features will be disabled.")
        
        # Video settings
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 30
        self.scene_duration_min = 10  # seconds
        self.scene_duration_max = 20  # seconds
        self.total_duration_max = 180  # 3 minutes max
        
        # Image generation settings
        self.image_size = "1792x1024"  # DALL-E 3 supported size
        self.image_quality = "standard"
        self.image_style = "natural"
        
        # TTS settings
        self.tts_voice = "alloy"  # OpenAI TTS voices: alloy, echo, fable, onyx, nova, shimmer
        self.tts_model = "tts-1"  # tts-1 (fast) or tts-1-hd (high quality)
        
        # Output settings
        self.output_dir = "output"
        self.temp_dir = "temp"
        
        # Background music settings
        self.enable_bg_music = True
        self.bg_music_volume = 0.3  # 30% volume
        
        # Transition settings
        self.transition_duration = 1.0  # seconds
        self.transition_type = "crossfade"  # crossfade, fade, dissolve, none
        self.video_transition_type = "crossfade"  # crossfade, fade, dissolve, none
        
        # Retry settings
        self.max_retries = 3  # Maximum number of retry attempts for failed operations
        self.retry_delay = 10  # Delay between retry attempts in seconds
        
        # Multi-format settings
        self.enable_video_generation = True
        self.enable_image_generation = True
        self.enable_pdf_generation = True
        
        # PDF settings
        self.pdf_page_size = "A4"  # A4, letter
        self.pdf_font_size = 12
        self.pdf_title_font_size = 24
        self.pdf_heading_font_size = 16
        self.pdf_images_per_page = 1  # How many images to include per page
        
        # Image settings
        self.generate_standalone_image = True
        self.image_format = "png"  # png, jpg
        self.image_quality_jpg = 95  # For JPEG compression (1-100)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "video_width": self.video_width,
            "video_height": self.video_height,
            "fps": self.fps,
            "scene_duration_min": self.scene_duration_min,
            "scene_duration_max": self.scene_duration_max,
            "total_duration_max": self.total_duration_max,
            "image_size": self.image_size,
            "image_quality": self.image_quality,
            "image_style": self.image_style,
            "tts_voice": self.tts_voice,
            "tts_model": self.tts_model,
            "output_dir": self.output_dir,
            "temp_dir": self.temp_dir,
            "enable_bg_music": self.enable_bg_music,
            "bg_music_volume": self.bg_music_volume,
            "transition_duration": self.transition_duration,
            "transition_type": self.transition_type,
            "enable_video_generation": self.enable_video_generation,
            "enable_image_generation": self.enable_image_generation,
            "enable_pdf_generation": self.enable_pdf_generation,
            "pdf_page_size": self.pdf_page_size,
            "pdf_font_size": self.pdf_font_size,
            "pdf_title_font_size": self.pdf_title_font_size,
            "pdf_heading_font_size": self.pdf_heading_font_size,
            "pdf_images_per_page": self.pdf_images_per_page,
            "generate_standalone_image": self.generate_standalone_image,
            "image_format": self.image_format,
            "image_quality_jpg": self.image_quality_jpg,
        }
