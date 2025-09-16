"""
Main video generation engine that orchestrates the entire process.
"""

import os
import time
from typing import Optional, Dict, Any
from .config import Config
from .script_generator import ScriptGenerator, Scene
from .runway_generator import RunwayGenerator
from .tts_generator import TTSGenerator
from .video_assembler import VideoAssembler, MOVIEPY_AVAILABLE
from .video_assembler_fallback import VideoAssemblerFallback
from .image_generator import ImageGenerator
from .pdf_generator import PDFGenerator

class VideoEngine:
    """Main engine for generating videos from text prompts."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the video generation engine.
        
        Args:
            config: Configuration object. If None, creates default config.
        """
        self.config = config or Config()
        
        # Initialize components
        self.script_generator = ScriptGenerator(self.config)
        self.visual_generator = RunwayGenerator(self.config)
        self.tts_generator = TTSGenerator(self.config)
        
        # Use fallback assembler if MoviePy is not available
        if MOVIEPY_AVAILABLE:
            self.video_assembler = VideoAssembler(self.config)
        else:
            print("Using fallback video assembler due to MoviePy import issues")
            self.video_assembler = VideoAssemblerFallback(self.config)
        
        # Create necessary directories
        self._create_directories()
        
    def _create_directories(self):
        """Create necessary directories for output and temporary files."""
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.temp_dir, exist_ok=True)
    
    def generate_video(self, prompt: str, cleanup: bool = True) -> Optional[str]:
        """
        Generate a complete video from a text prompt.
        
        Args:
            prompt: The input text prompt
            cleanup: Whether to clean up temporary files after generation
            
        Returns:
            Path to the generated video file, or None if generation failed
        """
        try:
            print("=" * 60)
            print("VIDEO GENERATION ENGINE STARTING")
            print("=" * 60)
            print(f"Input prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print()
            
            start_time = time.time()
            
            # Step 1: Generate script and scenes
            print("STEP 1: Generating script and scene breakdown...")
            scenes = self.script_generator.generate_script(prompt)
            # scenes = [Scene(text='This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene(door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: A sleek, eye-catching shot of a modern boutique storefront with a grand \'Bella Boutique\' neon sign. The headline "Grand Opening Sale – August 5, 2025" fades onto the screen in bold, stylish letters.', duration=10.0, scene_number=1, start_time=0.0), Scene(text='This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene(door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: Cut to an interior shot of the boutique, filled with elegant clothing racks. On the racks are trendy outfits, sparkling under soft ambient lighting. Overlay text reads: “Fashion at Its Finest.”', duration=10.0, scene_number=2, start_time=10.0), Scene(text="This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene(door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: Close-up of the price tags on various items, showing their original prices. A red '50% Off' sticker animates onto each tag. The scene feels exciting and irresistible. On-screen text: “Unbelievable Discounts.”", duration=10.0, scene_number=3, start_time=20.0)]
            
            if not scenes:
                print("ERROR: Failed to generate scenes from prompt")
                return None
            
            print("scenes: ", scenes)
            # scenes = scenes[:3]
            
            script_summary = self.script_generator.get_script_summary(scenes)
            print(f"Generated {script_summary['total_scenes']} scenes")
            print(f"Total duration: {script_summary['total_duration']:.1f} seconds")
            print(f"Total words: {script_summary['total_words']}")
            # print()
            
            # # Step 2: Generate visuals
            # ###############################
            print("STEP 2: Generating visuals...")
            # Reset visual context for new video
            # self.visual_generator.reset_visual_context() used in openAI
            # image_paths = self.visual_generator.generate_visuals_for_scenes(scenes) used in openAI
            image_paths = self.visual_generator.generate_visuals_for_scenes(scenes)
            # image_paths = ['temp/image_01.png', 'temp/image_02.png', 'temp/image_03.png', 'temp/image_04.png', 'temp/image_05.png', 'temp/image_06.png', 'temp/image_07.png', 'temp/image_08.png', 'temp/image_09.png']
            successful_images = sum(1 for path in image_paths if path is not None)
            if successful_images == 0:
                print("ERROR: No images were generated successfully")
                return None
            
            print(f"Successfully generated {successful_images}/{len(scenes)} images")
            print('image_paths: ', image_paths)
            
            # Step 3: Generate TTS
            print("STEP 3: Generating text-to-speech...")
            audio_paths = self.tts_generator.generate_tts_for_scenes(scenes)
            
            successful_audio = sum(1 for path in audio_paths if path is not None)
            if successful_audio == 0:
                print("ERROR: No TTS audio was generated successfully")
                return None
            
            print(f"Successfully generated {successful_audio}/{len(scenes)} TTS files")
            print()
            
            # # Step 4: Create full narration
            print("STEP 4: Creating full narration...")
            narration_path = self.tts_generator.create_full_narration(scenes, audio_paths)
            
            if not narration_path:
                print("WARNING: Failed to create full narration, proceeding without it")
            else:
                print("Full narration created successfully")
            print()
            time.sleep(5)  # 2 second delay between requests
            #############################

            # Step 5: Assemble video
            print("STEP 5: Generating individual scene videos...")

            video_script = []
            for i in range(len(scenes)):
                video_script.append(self.script_generator.create_video_script(f"""{scenes[i].text}
                """))
            print(video_script)
            
            # # Generate individual scene videos
            video_paths = self.visual_generator.generate_videos(scenes, image_paths, video_script)
            # video_paths = ['output/video_01.mp4', 'output/video_02.mp4', 'output/video_03.mp4', 'output/video_04.mp4', 'output/video_05.mp4', 'output/video_06.mp4', 'output/video_07.mp4', 'output/video_08.mp4', 'output/video_09.mp4']
            
            if not video_paths:
                print("ERROR: Failed to generate scene videos")
                return None
            
            print(f"Generated {len(video_paths)} individual scene videos")
            
            # Step 6: Combine all scene videos into final video
            print("STEP 6: Combining scene videos into final video...")
            final_video_path = self.video_assembler.concatenate_videos(video_paths)
            
            if not final_video_path:
                print("ERROR: Failed to combine scene videos")
                return None
            
            print("Video combination completed successfully")
            print()
            
            # Use the final combined video path
            video_path = final_video_path
            
            # Step 7: Cleanup (if requested)
            if cleanup:
                print("STEP 7: Cleaning up temporary files...")
                self._cleanup_temp_files(image_paths, audio_paths, narration_path, video_paths)
                print("Cleanup completed")
                print()
            
            # Calculate total time
            total_time = time.time() - start_time
            
            print("=" * 60)
            print("VIDEO GENERATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Output video: {video_path}")
            print(f"Total generation time: {total_time:.1f} seconds")
            print(f"Video duration: {script_summary['total_duration']:.1f} seconds")
            print("=" * 60)
            
            return video_path
            
        except Exception as e:
            print(f"ERROR: Video generation failed: {str(e)}")
            return None
    
    def _cleanup_temp_files(
        self, 
        image_paths: list, 
        audio_paths: list, 
        narration_path: Optional[str],
        video_paths: Optional[list] = None
    ):
        """Clean up temporary files."""
        # Clean up images
        # self.visual_generator.cleanup_temp_images(image_paths) used in openAI
        
        # Clean up audio files
        self.tts_generator.cleanup_temp_audio(audio_paths)
        
        # Clean up narration
        if narration_path and os.path.exists(narration_path):
            try:
                os.remove(narration_path)
            except Exception as e:
                print(f"Error cleaning up narration: {str(e)}")
        
        # Clean up individual scene videos (keep only the final combined video)
        if video_paths:
            for video_path in video_paths:
                if video_path and os.path.exists(video_path):
                    try:
                        os.remove(video_path)
                        print(f"Cleaned up temporary video: {video_path}")
                    except Exception as e:
                        print(f"Error cleaning up video file {video_path}: {str(e)}")
        
        # Clean up other temp files
        self.video_assembler.cleanup_temp_files(image_paths, audio_paths)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the video generation process."""
        return {
            "config": self.config.to_dict(),
            "directories": {
                "output": self.config.output_dir,
                "temp": self.config.temp_dir
            },
            "api_settings": {
                "image_size": self.config.image_size,
                "image_quality": self.config.image_quality,
                "tts_voice": self.config.tts_voice,
                "tts_model": self.config.tts_model
            }
        }
    
    def validate_setup(self) -> bool:
        """Validate that all required components are properly configured."""
        try:
            # Check API key
            if not self.config.openai_api_key:
                print("ERROR: OpenAI API key not found")
                return False
            
            # Check directories
            if not os.path.exists(self.config.output_dir):
                print(f"ERROR: Output directory does not exist: {self.config.output_dir}")
                return False
            
            if not os.path.exists(self.config.temp_dir):
                print(f"ERROR: Temp directory does not exist: {self.config.temp_dir}")
                return False
            
            # Check MoviePy installation
            try:
                from moviepy.editor import ImageClip
                print("MoviePy: OK")
            except ImportError:
                print("ERROR: MoviePy not installed")
                return False
            
            # Check pydub installation
            try:
                from pydub import AudioSegment
                print("pydub: OK")
            except ImportError:
                print("ERROR: pydub not installed")
                return False
            
            print("Setup validation: PASSED")
            return True
            
        except Exception as e:
            print(f"ERROR: Setup validation failed: {str(e)}")
            return False


class ContentEngine:
    """Enhanced engine for generating multiple content types (video, image, PDF) from text prompts."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the content generation engine.
        
        Args:
            config: Configuration object. If None, creates default config.
        """
        self.config = config or Config()
        
        # Initialize components
        self.script_generator = ScriptGenerator(self.config)
        self.visual_generator = VisualGenerator(self.config)
        self.image_generator = ImageGenerator(self.config)
        self.tts_generator = TTSGenerator(self.config)
        self.video_assembler = VideoAssembler(self.config)
        self.pdf_generator = PDFGenerator(self.config)
        
        # Create necessary directories
        self._create_directories()
        
    def _create_directories(self):
        """Create necessary directories for output and temporary files."""
        os.makedirs(self.config.output_dir, exist_ok=True)
        os.makedirs(self.config.temp_dir, exist_ok=True)
    
    def generate_all_content(self, prompt: str, cleanup: bool = True) -> Dict[str, Optional[str]]:
        """
        Generate all content types (video, image, PDF) from a text prompt.
        
        Args:
            prompt: The input text prompt
            cleanup: Whether to clean up temporary files after generation
            
        Returns:
            Dictionary with paths to generated files:
            {
                'video': video_path or None,
                'images': [image_paths],
                'pdf': pdf_path or None,
                'scenes': [Scene objects]
            }
        """
        try:
            print("=" * 80)
            print("CONTENT GENERATION ENGINE STARTING")
            print("=" * 80)
            print(f"Input prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            print()
            
            start_time = time.time()
            results = {
                'video': None,
                'images': [],
                'pdf': None,
                'scenes': []
            }
            
            # Step 1: Generate script and scenes
            print("STEP 1: Generating script and scene breakdown...")
            scenes = self.script_generator.generate_script(prompt)
            
            if not scenes:
                print("ERROR: Failed to generate scenes from prompt")
                return results
            
            results['scenes'] = scenes
            script_summary = self.script_generator.get_script_summary(scenes)
            print(f"Generated {script_summary['total_scenes']} scenes")
            print(f"Total duration: {script_summary['total_duration']:.1f} seconds")
            print()
            
            # Step 2: Generate images for scenes
            print("STEP 2: Generating images for scenes...")
            scene_images = self.visual_generator.generate_visuals_for_scenes(scenes)
            results['images'] = scene_images
            
            successful_images = sum(1 for path in scene_images if path is not None)
            print(f"Successfully generated {successful_images}/{len(scenes)} scene images")
            print()
            
            # Step 3: Generate standalone image
            print("STEP 3: Generating standalone image...")
            standalone_image = self.image_generator.generate_image(prompt, "standalone_image")
            if standalone_image:
                results['images'].append(standalone_image)
                print(f"✅ Standalone image generated: {standalone_image}")
            else:
                print("❌ Failed to generate standalone image")
            print()
            
            # Step 4: Generate PDF document
            print("STEP 4: Generating PDF document...")
            pdf_path = self.pdf_generator.generate_pdf_from_scenes(
                scenes, scene_images, "Video Script Document"
            )
            results['pdf'] = pdf_path
            
            if pdf_path:
                print(f"✅ PDF generated: {pdf_path}")
            else:
                print("❌ Failed to generate PDF")
            print()
            
            # Step 5: Generate video (if FFmpeg is available)
            print("STEP 5: Generating video...")
            try:
                # Generate TTS
                audio_paths = self.tts_generator.generate_tts_for_scenes(scenes)
                narration_path = self.tts_generator.create_full_narration(scenes, audio_paths)
                
                # Assemble video
                video_path = self.video_assembler.assemble_video(
                    scenes, scene_images, audio_paths, narration_path
                )
                results['video'] = video_path
                
                if video_path:
                    print(f"✅ Video generated: {video_path}")
                else:
                    print("❌ Failed to generate video (FFmpeg may not be available)")
                    
            except Exception as e:
                print(f"❌ Video generation failed: {str(e)}")
                print("   This is likely due to FFmpeg not being installed")
            print()
            
            # Step 6: Cleanup (if requested)
            if cleanup:
                print("STEP 6: Cleaning up temporary files...")
                self._cleanup_temp_files(scene_images, audio_paths if 'audio_paths' in locals() else [], narration_path if 'narration_path' in locals() else None)
                print("Cleanup completed")
                print()
            
            # Calculate total time
            total_time = time.time() - start_time
            
            print("=" * 80)
            print("CONTENT GENERATION COMPLETED!")
            print("=" * 80)
            print("Generated content:")
            if results['video']:
                print(f"📹 Video: {results['video']}")
            if results['images']:
                print(f"🖼️  Images: {len([img for img in results['images'] if img])} files")
            if results['pdf']:
                print(f"📄 PDF: {results['pdf']}")
            print(f"⏱️  Total generation time: {total_time:.1f} seconds")
            print("=" * 80)
            
            return results
            
        except Exception as e:
            print(f"ERROR: Content generation failed: {str(e)}")
            return results
    
    def generate_image_only(self, prompt: str, filename: Optional[str] = None) -> Optional[str]:
        """Generate only an image from the prompt."""
        return self.image_generator.generate_image(prompt, filename)
    
    def generate_pdf_only(self, prompt: str, filename: Optional[str] = None) -> Optional[str]:
        """Generate only a PDF from the prompt."""
        scenes = self.script_generator.generate_script(prompt)
        if not scenes:
            return None
        
        # Generate images for the PDF
        images = self.visual_generator.generate_visuals_for_scenes(scenes)
        
        return self.pdf_generator.generate_pdf_from_scenes(scenes, images, filename or "Generated Document")
    
    def generate_video_only(self, prompt: str, cleanup: bool = True) -> Optional[str]:
        """Generate only a video from the prompt (same as original VideoEngine)."""
        video_engine = VideoEngine(self.config)
        return video_engine.generate_video(prompt, cleanup)
    
    def _cleanup_temp_files(self, image_paths: list, audio_paths: list, narration_path: Optional[str]):
        """Clean up temporary files."""
        # Clean up images
        # self.visual_generator.cleanup_temp_images(image_paths) used in openAI
        
        # Clean up audio files
        self.tts_generator.cleanup_temp_audio(audio_paths)
        
        # Clean up narration
        if narration_path and os.path.exists(narration_path):
            try:
                os.remove(narration_path)
            except Exception as e:
                print(f"Error cleaning up narration: {str(e)}")
        
        # Clean up other temp files
        self.video_assembler.cleanup_temp_files(image_paths, audio_paths)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about the content generation process."""
        return {
            "config": self.config.to_dict(),
            "directories": {
                "output": self.config.output_dir,
                "temp": self.config.temp_dir
            },
            "supported_formats": ["video", "image", "pdf"],
            "api_settings": {
                "image_size": self.config.image_size,
                "image_quality": self.config.image_quality,
                "tts_voice": self.config.tts_voice,
                "tts_model": self.config.tts_model
            }
        }
    
    def validate_setup(self) -> bool:
        """Validate that all required components are properly configured."""
        try:
            # Check API key
            if not self.config.openai_api_key:
                print("ERROR: OpenAI API key not found")
                return False
            
            # Check directories
            if not os.path.exists(self.config.output_dir):
                print(f"ERROR: Output directory does not exist: {self.config.output_dir}")
                return False
            
            if not os.path.exists(self.config.temp_dir):
                print(f"ERROR: Temp directory does not exist: {self.config.temp_dir}")
                return False
            
            # Check MoviePy installation
            try:
                from moviepy.editor import ImageClip
                print("MoviePy: OK")
            except ImportError:
                print("WARNING: MoviePy not installed - video generation will be limited")
            
            # Check pydub installation
            try:
                from pydub import AudioSegment
                print("pydub: OK")
            except ImportError:
                print("WARNING: pydub not installed - audio processing will be limited")
            
            # Check reportlab installation
            try:
                from reportlab.lib.pagesizes import A4
                print("reportlab: OK")
            except ImportError:
                print("WARNING: reportlab not installed - PDF generation will be limited")
            
            print("Setup validation: PASSED")
            return True
            
        except Exception as e:
            print(f"ERROR: Setup validation failed: {str(e)}")
            return False
