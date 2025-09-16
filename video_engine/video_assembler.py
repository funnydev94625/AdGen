"""
Video assembly module using MoviePy for creating final video.
"""

import os
import numpy as np
from typing import List, Optional, Tuple
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, VideoFileClip
)
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.resize import resize
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.audio.fx.volumex import volumex

# Fix for PIL ANTIALIAS deprecation in newer Pillow versions
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

class VideoAssembler:
    """Assembles video clips, audio, and effects into final video."""
    
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
        
        Args:
            scenes: List of Scene objects
            image_paths: List of image file paths
            audio_paths: List of audio file paths for individual scenes
            narration_path: Path to full narration audio file
            
        Returns:
            Path to the final video file, or None if assembly failed
        """
        try:
            print("Starting video assembly...")
            
            # Create video clips from images
            video_clips = self._create_video_clips(scenes, image_paths)
            
            if not video_clips:
                print("No valid video clips created")
                return None
            
            # Add transitions between clips
            video_clips = self._add_transitions(video_clips)
            
            # Concatenate video clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add audio (narration + background music)
            final_video = self._add_audio(final_video, narration_path)
            
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
    
    def _create_video_clips(self, scenes: List, image_paths: List[Optional[str]]) -> List[ImageClip]:
        """Create video clips from images."""
        video_clips = []
        
        for i, (scene, image_path) in enumerate(zip(scenes, image_paths)):
            if image_path and os.path.exists(image_path):
                try:
                    # Create image clip
                    clip = ImageClip(image_path, duration=scene.duration)
                    
                    # Resize to target resolution
                    clip = clip.fx(resize, (self.config.video_width, self.config.video_height))
                    
                    # Add simple pan/zoom effect for visual interest
                    clip = self._add_pan_zoom_effect(clip, scene.duration)
                    
                    video_clips.append(clip)
                    print(f"Created video clip for scene {i+1}")
                    
                except Exception as e:
                    print(f"Error creating clip for scene {i+1}: {str(e)}")
                    continue
            else:
                print(f"No valid image for scene {i+1}, skipping...")
        
        return video_clips
    
    def _add_pan_zoom_effect(self, clip: ImageClip, duration: float) -> ImageClip:
        """Add subtle pan and zoom effect to image clip."""
        try:
            # Simple zoom effect - start slightly zoomed in, zoom out over time
            def make_frame(t):
                # Calculate zoom factor (1.1 to 1.0 over duration)
                zoom_factor = 1.1 - (t / duration) * 0.1
                
                # Apply zoom
                zoomed_clip = clip.fx(resize, zoom_factor)
                
                # Center the zoomed clip
                x_center = (zoomed_clip.w - self.config.video_width) // 2
                y_center = (zoomed_clip.h - self.config.video_height) // 2
                
                return zoomed_clip.get_frame(t)[
                    y_center:y_center + self.config.video_height,
                    x_center:x_center + self.config.video_width
                ]
            
            # Create new clip with pan/zoom effect
            effect_clip = clip.fl(lambda gf, t: make_frame(t), apply_to=['mask'])
            return effect_clip
            
        except Exception as e:
            print(f"Error adding pan/zoom effect: {str(e)}")
            return clip  # Return original clip if effect fails
    
    def _add_transitions(self, video_clips: List[ImageClip]) -> List[ImageClip]:
        """Add transitions between video clips."""
        if len(video_clips) <= 1:
            return video_clips
        
        transition_duration = self.config.transition_duration
        clips_with_transitions = []
        
        for i, clip in enumerate(video_clips):
            # Add fade in to first clip
            if i == 0:
                clip = clip.fx(fadein, transition_duration)
            
            # Add fade out to last clip
            if i == len(video_clips) - 1:
                clip = clip.fx(fadeout, transition_duration)
            
            # Add crossfade to middle clips
            elif i > 0:
                clip = clip.fx(fadein, transition_duration)
                clip = clip.fx(fadeout, transition_duration)
            
            clips_with_transitions.append(clip)
        
        return clips_with_transitions
    
    def _add_video_transitions(self, video_clips: List[VideoFileClip]) -> List[VideoFileClip]:
        """Add fading transitions between video clips."""
        if len(video_clips) <= 1:
            return video_clips
        
        transition_duration = self.config.transition_duration
        clips_with_transitions = []
        
        for i, clip in enumerate(video_clips):
            # Add fade in to first clip
            if i == 0:
                clip = clip.fx(fadein, transition_duration)
            
            # Add fade out to last clip
            elif i == len(video_clips) - 1:
                clip = clip.fx(fadeout, transition_duration)
            
            # Add crossfade to middle clips (both fade in and fade out)
            else:
                clip = clip.fx(fadein, transition_duration)
                clip = clip.fx(fadeout, transition_duration)
            
            clips_with_transitions.append(clip)
        
        return clips_with_transitions
    
    def _add_crossfade_transitions(self, video_clips: List[VideoFileClip]) -> List[VideoFileClip]:
        """Add crossfade transitions between video clips for smoother blending."""
        if len(video_clips) <= 1:
            return video_clips
        
        transition_duration = self.config.transition_duration
        clips_with_crossfade = []
        
        for i, clip in enumerate(video_clips):
            if i == 0:
                # First clip: only fade in
                clip = clip.fx(fadein, transition_duration)
            elif i == len(video_clips) - 1:
                # Last clip: only fade out
                clip = clip.fx(fadeout, transition_duration)
            else:
                # Middle clips: both fade in and fade out for crossfade effect
                clip = clip.fx(fadein, transition_duration)
                clip = clip.fx(fadeout, transition_duration)
            
            clips_with_crossfade.append(clip)
        
        return clips_with_crossfade
    
    def _add_audio(self, video_clip: ImageClip, narration_path: Optional[str]) -> ImageClip:
        """Add narration and background music to video."""
        try:
            audio_clips = []
            
            # Add narration if available
            if narration_path and os.path.exists(narration_path):
                narration = AudioFileClip(narration_path)
                
                # Adjust narration duration to match video
                if narration.duration > video_clip.duration:
                    narration = narration.subclip(0, video_clip.duration)
                elif narration.duration < video_clip.duration:
                    # Loop narration if it's shorter than video
                    loops_needed = int(video_clip.duration / narration.duration) + 1
                    narration = concatenate_audioclips([narration] * loops_needed)
                    narration = narration.subclip(0, video_clip.duration)
                
                audio_clips.append(narration)
                print("Added narration audio")
            
            # Add background music if enabled
            if self.config.enable_bg_music:
                bg_music = self._create_background_music(video_clip.duration)
                if bg_music:
                    audio_clips.append(bg_music)
                    print("Added background music")
            
            # Combine audio clips
            if audio_clips:
                if len(audio_clips) == 1:
                    final_audio = audio_clips[0]
                else:
                    final_audio = CompositeAudioClip(audio_clips)
                
                # Set audio to video
                video_clip = video_clip.set_audio(final_audio)
            
            return video_clip
            
        except Exception as e:
            print(f"Error adding audio: {str(e)}")
            return video_clip  # Return video without audio if audio fails
    
    def _create_background_music(self, duration: float) -> Optional[AudioFileClip]:
        """Create background music for the video."""
        try:
            # Generate a simple background tone using numpy
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create a gentle background tone (low frequency sine wave)
            frequency = 220  # A3 note
            background_tone = 0.1 * np.sin(2 * np.pi * frequency * t)
            
            # Add some variation to make it more interesting
            background_tone += 0.05 * np.sin(2 * np.pi * frequency * 1.5 * t)
            
            # Convert to audio clip
            audio_array = (background_tone * 32767).astype(np.int16)
            
            # Create temporary audio file
            import tempfile
            temp_audio_path = os.path.join(self.config.temp_dir, "bg_music.wav")
            
            # Save as WAV file
            import wave
            with wave.open(temp_audio_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_array.tobytes())
            
            # Load as MoviePy audio clip
            bg_music = AudioFileClip(temp_audio_path)
            
            # Adjust volume
            bg_music = bg_music.fx(volumex, self.config.bg_music_volume)
            
            return bg_music
            
        except Exception as e:
            print(f"Error creating background music: {str(e)}")
            return None
    
    def _export_video(self, video_clip: ImageClip) -> Optional[str]:
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
    
    def concatenate_videos(self, video_paths: List[str]) -> Optional[str]:
        """
        Concatenate multiple video files into a single video.
        
        Args:
            video_paths: List of video file paths to concatenate
            
        Returns:
            Path to the concatenated video file, or None if concatenation failed
        """
        try:
            if not video_paths:
                print("No video paths provided for concatenation")
                return None
            
            # Filter out None values and check if files exist
            valid_video_paths = []
            for video_path in video_paths:
                if video_path and os.path.exists(video_path):
                    valid_video_paths.append(video_path)
                else:
                    print(f"Warning: Video file not found or invalid: {video_path}")
            
            if not valid_video_paths:
                print("No valid video files found for concatenation")
                return None
            
            print(f"Concatenating {len(valid_video_paths)} video files...")
            
            # Load video clips
            video_clips = []
            for i, video_path in enumerate(valid_video_paths):
                try:
                    print(f"Loading video {i+1}/{len(valid_video_paths)}: {video_path}")
                    clip = VideoFileClip(video_path)
                    video_clips.append(clip)
                except Exception as e:
                    print(f"Error loading video {video_path}: {str(e)}")
                    continue
            
            if not video_clips:
                print("No video clips could be loaded")
                return None
            
            # Add fading effects between video clips
            print(f"Adding {self.config.video_transition_type} transitions between video clips...")
            if self.config.video_transition_type == "crossfade":
                video_clips_with_transitions = self._add_crossfade_transitions(video_clips)
            elif self.config.video_transition_type == "fade":
                video_clips_with_transitions = self._add_video_transitions(video_clips)
            else:
                # No transitions
                video_clips_with_transitions = video_clips
            
            # Concatenate video clips with transitions
            print("Concatenating video clips with transitions...")
            final_video = concatenate_videoclips(video_clips_with_transitions, method="compose")
            
            # Generate output filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"combined_video_{timestamp}.mp4"
            output_path = os.path.join(self.config.output_dir, output_filename)
            
            # Export concatenated video
            print(f"Exporting concatenated video to: {output_path}")
            final_video.write_videofile(
                output_path,
                fps=self.config.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Close clips to free memory
            for clip in video_clips:
                clip.close()
            final_video.close()
            
            print(f"Video concatenation completed successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error concatenating videos: {str(e)}")
            return None

    def cleanup_temp_files(self, image_paths: List[Optional[str]], audio_paths: List[Optional[str]]):
        """Clean up temporary files."""
        # Clean up background music file
        bg_music_path = os.path.join(self.config.temp_dir, "bg_music.wav")
        if os.path.exists(bg_music_path):
            try:
                os.remove(bg_music_path)
            except Exception as e:
                print(f"Error cleaning up background music: {str(e)}")
        
        # Clean up other temp files
        temp_files = [
            os.path.join(self.config.temp_dir, "full_narration.wav"),
            os.path.join(self.config.temp_dir, "temp-audio.m4a")
        ]
        
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file}: {str(e)}")
