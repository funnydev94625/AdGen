"""
Fallback video assembly module for when moviepy.editor has import issues.
"""

import os
import numpy as np
from typing import List, Optional, Tuple

# Try different import methods for MoviePy
try:
    from moviepy.editor import (
        ImageClip, AudioFileClip, CompositeVideoClip, 
        CompositeAudioClip
    )
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.video.fx.resize import resize
    from moviepy.video.fx.fadein import fadein
    from moviepy.video.fx.fadeout import fadeout
    from moviepy.audio.fx.volumex import volumex
    MOVIEPY_AVAILABLE = True
    except ImportError:
        try:
            # Try importing individual components
            from moviepy.video.io.VideoFileClip import VideoFileClip
            from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
            from moviepy.video.VideoClip import VideoClip
            from moviepy.audio.io.AudioFileClip import AudioFileClip
            from moviepy.video.fx.resize import resize
            from moviepy.video.fx.fadein import fadein
            from moviepy.video.fx.fadeout import fadeout
            from moviepy.audio.fx.volumex import volumex
            from moviepy.video.compositing.concatenate import concatenate_videoclips
            from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
            from moviepy.audio.AudioClip import CompositeAudioClip
            
            # Create aliases
            ImageClip = VideoClip
            AudioFileClip = AudioFileClip
            
            MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False
        print("Warning: MoviePy not available. Video assembly will be limited.")

# Fix for PIL ANTIALIAS deprecation in newer Pillow versions
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

class VideoAssemblerFallback:
    """Fallback video assembler that works around MoviePy import issues."""
    
    def __init__(self, config):
        self.config = config
        
    def assemble_video(
        self, 
        scenes: List, 
        image_paths: List[Optional[str]], 
        audio_paths: List[Optional[str]],
        narration_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Assemble the final video from scenes, images, and audio.
        """
        if not MOVIEPY_AVAILABLE:
            print("❌ MoviePy not available. Cannot assemble video.")
            print("   Please install FFmpeg and fix MoviePy import issues.")
            return None
        
        try:
            print("Starting video assembly (fallback mode)...")
            
            # Create video clips from images
            video_clips = self._create_video_clips(scenes, image_paths)
            
            if not video_clips:
                print("No valid video clips created")
                return None
            
            # Concatenate video clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio if available
            if narration_path and os.path.exists(narration_path):
                try:
                    narration = AudioFileClip(narration_path)
                    final_video = final_video.set_audio(narration)
                    print("Added narration audio")
                except Exception as e:
                    print(f"Warning: Could not add narration: {str(e)}")
            
            # Export final video
            output_path = self._export_video(final_video)
            
            # Clean up clips
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error assembling video: {str(e)}")
            return None
    
    def _create_video_clips(self, scenes: List, image_paths: List[Optional[str]]) -> List:
        """Create video clips from images."""
        video_clips = []
        
        for i, (scene, image_path) in enumerate(zip(scenes, image_paths)):
            if image_path and os.path.exists(image_path):
                try:
                    # Create image clip
                    clip = ImageClip(image_path, duration=scene.duration)
                    
                    # Resize to target resolution
                    clip = clip.fx(resize, (self.config.video_width, self.config.video_height))
                    
                    video_clips.append(clip)
                    print(f"Created video clip for scene {i+1}")
                    
                except Exception as e:
                    print(f"Error creating clip for scene {i+1}: {str(e)}")
                    continue
            else:
                print(f"No valid image for scene {i+1}, skipping...")
        
        return video_clips
    
    def _export_video(self, video_clip) -> Optional[str]:
        """Export the final video to file."""
        try:
            # Create output directory
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # Generate output filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"generated_video_{timestamp}.mp4"
            output_path = os.path.join(self.config.output_dir, output_filename)
            
            # Export video
            print(f"Exporting video to: {output_path}")
            video_clip.write_videofile(
                output_path,
                fps=self.config.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            print(f"Video exported successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error exporting video: {str(e)}")
            return None
    
    def cleanup_temp_files(self, image_paths: List[Optional[str]], audio_paths: List[Optional[str]]):
        """Clean up temporary files."""
        # Clean up temp files
        temp_files = [
            os.path.join(self.config.temp_dir, "temp-audio.m4a")
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file}: {str(e)}")
