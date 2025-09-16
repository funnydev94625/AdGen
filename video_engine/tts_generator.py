"""
Text-to-Speech generation module using OpenAI TTS API.
"""

import os
import time
from typing import Optional, List
from openai import OpenAI

# Handle audioop compatibility for Python 3.13+
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
    except ImportError:
        # Fallback: create a dummy audioop module
        class DummyAudioop:
            @staticmethod
            def mul(fragment, width, factor):
                return fragment
            @staticmethod
            def add(fragment1, fragment2, width):
                return fragment1
            @staticmethod
            def bias(fragment, width, bias):
                return fragment
        audioop = DummyAudioop()

from pydub import AudioSegment
from pydub.utils import which

class TTSGenerator:
    """Generates speech audio using OpenAI TTS API."""
    
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
        
    def generate_tts(self, text: str, scene_number: int) -> Optional[str]:
        """
        Generate TTS audio for a scene.
        
        Args:
            text: The text to convert to speech
            scene_number: The scene number for naming
            
        Returns:
            Path to the generated audio file, or None if generation failed
        """
        try:
            # Clean text for TTS
            cleaned_text = self._clean_text_for_tts(text)
            
            # Generate audio using OpenAI TTS API
            audio_data = self._call_tts_api(cleaned_text)
            
            if not audio_data:
                return None
                
            # Save audio file
            audio_path = self._save_audio(audio_data, scene_number)
            
            return audio_path
            
        except Exception as e:
            print(f"Error generating TTS for scene {scene_number}: {str(e)}")
            return None
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output."""
        # Remove extra whitespace
        text = text.strip()
        
        # Replace common abbreviations with full words for better pronunciation
        replacements = {
            "Dr.": "Doctor",
            "Mr.": "Mister", 
            "Mrs.": "Misses",
            "Ms.": "Miss",
            "Prof.": "Professor",
            "vs.": "versus",
            "etc.": "etcetera",
            "&": "and",
            "%": "percent",
            "$": "dollars",
            "#": "number",
            "@": "at"
        }
        
        for abbrev, full_word in replacements.items():
            text = text.replace(abbrev, full_word)
        
        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'
            
        return text
    
    def _call_tts_api(self, text: str) -> Optional[bytes]:
        """Call OpenAI TTS API to generate speech audio."""
        try:
            response = self.client.audio.speech.create(
                model=self.config.tts_model,
                voice=self.config.tts_voice,
                input=text,
                response_format="mp3"
            )
            
            return response.content
            
        except Exception as e:
            print(f"Error calling TTS API: {str(e)}")
            return None
    
    def _save_audio(self, audio_data: bytes, scene_number: int) -> Optional[str]:
        """Save audio data to file."""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.config.temp_dir, exist_ok=True)
            
            # Save audio file
            filename = f"scene_{scene_number:02d}_tts.mp3"
            filepath = os.path.join(self.config.temp_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            # Convert to WAV for better compatibility with MoviePy
            wav_path = self._convert_to_wav(filepath)
            
            # Clean up original MP3 file
            if os.path.exists(filepath):
                os.remove(filepath)
                
            return wav_path
            
        except Exception as e:
            print(f"Error saving audio: {str(e)}")
            return None
    
    def _convert_to_wav(self, mp3_path: str) -> Optional[str]:
        """Convert MP3 to WAV format for better MoviePy compatibility."""
        try:
            # Load MP3 audio
            audio = AudioSegment.from_mp3(mp3_path)
            
            # Convert to WAV
            wav_path = mp3_path.replace('.mp3', '.wav')
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            print(f"Error converting audio to WAV: {str(e)}")
            return None
    
    def generate_tts_for_scenes(self, scenes: List) -> List[Optional[str]]:
        """
        Generate TTS audio for all scenes.
        
        Args:
            scenes: List of Scene objects
            
        Returns:
            List of audio file paths (or None for failed generations)
        """
        audio_paths = []
        
        print(f"Generating TTS for {len(scenes)} scenes...")
        
        for i, scene in enumerate(scenes):
            print(f"Generating TTS for scene {i+1}/{len(scenes)}: {scene.text[:50]}...")
            
            audio_path = self.generate_tts(scene.text, scene.scene_number)
            audio_paths.append(audio_path)
            
            # Add delay to respect API rate limits
            if i < len(scenes) - 1:  # Don't delay after the last scene
                time.sleep(1)  # 1 second delay between requests
        
        successful_generations = sum(1 for path in audio_paths if path is not None)
        print(f"Successfully generated {successful_generations}/{len(scenes)} TTS audio files")
        
        return audio_paths
    
    def create_full_narration(self, scenes: List, audio_paths: List[Optional[str]]) -> Optional[str]:
        """
        Combine all scene audio files into a single narration track.
        
        Args:
            scenes: List of Scene objects
            audio_paths: List of audio file paths
            
        Returns:
            Path to the combined narration file, or None if failed
        """
        try:
            # Filter out None values
            valid_audio_paths = [path for path in audio_paths if path is not None]
            
            if not valid_audio_paths:
                print("No valid audio files to combine")
                return None
            
            # Load and combine audio files
            combined_audio = AudioSegment.empty()
            
            for audio_path in valid_audio_paths:
                if os.path.exists(audio_path):
                    audio_segment = AudioSegment.from_wav(audio_path)
                    combined_audio += audio_segment
                    
                    # Add small pause between scenes
                    pause = AudioSegment.silent(duration=500)  # 0.5 second pause
                    combined_audio += pause
            
            # Save combined narration
            os.makedirs(self.config.temp_dir, exist_ok=True)
            narration_path = os.path.join(self.config.temp_dir, "full_narration.wav")
            combined_audio.export(narration_path, format="wav")
            
            print(f"Created full narration: {narration_path}")
            return narration_path
            
        except Exception as e:
            print(f"Error creating full narration: {str(e)}")
            return None
    
    def cleanup_temp_audio(self, audio_paths: List[Optional[str]]):
        """Clean up temporary audio files."""
        for audio_path in audio_paths:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"Error cleaning up audio {audio_path}: {str(e)}")
