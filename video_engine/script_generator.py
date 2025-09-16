"""
Script generation and scene breakdown module.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Scene:
    """Represents a single scene in the video."""
    text: str
    duration: float
    scene_number: int
    start_time: float = 0.0
    
    def __post_init__(self):
        """Calculate end time after initialization."""
        self.end_time = self.start_time + self.duration

class ScriptGenerator:
    """Generates script breakdown and scene segmentation from text prompts."""
    
    def __init__(self, config):
        self.config = config
        
    def generate_script(self, prompt: str) -> List[Scene]:
        """
        Generate script for video content (narrative or advertisement).
        
        Args:
            prompt: The input text prompt
            
        Returns:
            List of Scene objects with text, duration, and timing
        """
        # Clean and normalize the prompt
        cleaned_prompt = self._clean_text(prompt)
        
        # Detect if this is an ad/promotional content
        return self._generate_ad_script(cleaned_prompt)
    
    def _is_advertisement_content(self, prompt: str) -> bool:
        """Detect if the prompt is for advertisement content."""
        ad_keywords = [
            'flyer', 'menu', 'sale', 'promo', 'promotion', 'advertisement', 'ad',
            'event', 'opening', 'discount', 'offer', 'deal', 'special', 'limited time',
            'buy now', 'shop', 'store', 'restaurant', 'cafe', 'boutique', 'fair',
            'festival', 'concert', 'show', 'exhibition', 'launch', 'announcement'
        ]
        
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in ad_keywords)
    
    def _generate_ad_script(self, prompt: str) -> List[Scene]:
        """Generate script specifically for advertisement content."""
        try:
            # Use AI to create ad-optimized scenes
            ad_script_prompt = f"""
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
                SCENE 1: A sunny, wide shot of Maplewood Park with families entering through an archway decorated with balloons and streamers. Children run with excitement, while the headline text “Summer Fun Fair – July 20, 2025” animates onto the screen in bold, vibrant colors. | Duration: 10 seconds  

                SCENE 2: A close-up of a brightly lit carousel spinning, with kids waving and laughing as the ride turns. The scene feels joyful and energetic. Overlay text reads: “Games & Rides for Everyone!” | Duration: 10 seconds  

                SCENE 3: Transition to a lively area where kids are playing fair games—ring toss, balloon darts, and beanbag throws. Excited cheers and laughter fill the background. On-screen text: “Exciting Activities All Day Long.” | Duration: 10 seconds  

                SCENE 4: Pan across colorful food stalls—cotton candy being spun, lemonade being poured, and sizzling hotdogs on the grill. Families are smiling while holding tasty treats. Text overlay: “Delicious Food & Treats.” | Duration: 10 seconds  

                SCENE 5: A cheerful petting zoo scene: kids pet goats and rabbits, while parents snap photos. A pony with a small child on its back walks gently in the background. Overlay text: “Perfect for Animal Lovers.” | Duration: 10 seconds  

                SCENE 6: A small stage with a live band performing upbeat music, families dancing and clapping along. Close-up of guitar strumming and kids jumping to the beat. Overlay text: “Enjoy Live Music Performances.” | Duration: 10 seconds  

                SCENE 7: Wide panoramic shot of the entire fair in full swing—carousel spinning, food stalls buzzing, and the stage lit up. The atmosphere is festive and filled with color. Overlay text: “Fun for the Whole Family!” | Duration: 10 seconds  

                SCENE 8: Animated banner fills the screen with “Join Us for a Day of Family Fun!” followed by the event details: July 20, 2025 | 10 AM – 4 PM | Maplewood Park. | Duration: 10 seconds  

                SCENE 9: Closing shot of families waving at the camera, kids holding balloons, and the sun setting softly over the park. Final overlay: “Don’t Miss It!” | Duration: 10 seconds  
                try with this {prompt}

            """
            
            # Make OpenAI API call to generate the scenes
            from openai import OpenAI
            client = OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": ad_script_prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            print("AI Generated Scene Structure:")
            print(ai_response)
            print("-" * 50)
            
            # Parse the AI response into Scene objects
            scenes = self._parse_ai_scenes(ai_response)
            
            if scenes:
                return scenes
            else:
                print("Failed to parse AI response, using fallback")
                return self._create_basic_ad_scenes(prompt)
            
        except Exception as e:
            print(f"Error generating ad script with AI: {str(e)}")
            return self._create_basic_ad_scenes(prompt)
    
    def _create_basic_ad_scenes(self, prompt: str) -> List[Scene]:
        """Create basic ad scenes when AI analysis fails."""
        # Extract key elements from prompt
        scenes = []
        
        # Scene 1: Hook/Opening
        scenes.append(Scene(
            text="Eye-catching opening shot with main visual element",
            duration=4.0,
            scene_number=1,
            start_time=0.0
        ))
        
        # Scene 2: Main content
        scenes.append(Scene(
            text=prompt[:100] + "..." if len(prompt) > 100 else prompt,
            duration=8.0,
            scene_number=2,
            start_time=4.0
        ))
        
        # Scene 3: Details/Features
        scenes.append(Scene(
            text="Highlighting key features and benefits",
            duration=6.0,
            scene_number=3,
            start_time=12.0
        ))
        
        # Scene 4: Call to Action
        scenes.append(Scene(
            text="Call to action - visit, call, or take action now",
            duration=4.0,
            scene_number=4,
            start_time=18.0
        ))
        
        return scenes
    
    def _parse_ai_scenes(self, ai_response: str) -> List[Scene]:
        """Parse AI-generated scene response into Scene objects."""
        try:
            scenes = []
            current_time = 0.0
            
            # Split response into lines and process each scene
            lines = ai_response.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for scene patterns like "SCENE 1: [description] | Duration: [X seconds]"
                if line.startswith('SCENE') and '| Duration:' in line:
                    try:
                        # Extract scene number
                        scene_part = line.split(':')[0]  # "SCENE 1"
                        scene_number = int(scene_part.split()[1])
                        
                        # Extract description and duration
                        parts = line.split('| Duration:')
                        if len(parts) == 2:
                            description = "This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene(door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: " + parts[0].split(':', 1)[1].strip()
                            duration_text = parts[1].strip()
                            
                            # Extract duration (remove "seconds" if present)
                            duration_str = duration_text.replace('seconds', '').replace('second', '').strip()
                            duration = float(duration_str)
                            
                            # Create scene
                            scene = Scene(
                                text=description,
                                duration=duration,
                                scene_number=scene_number,
                                start_time=current_time
                            )
                            
                            scenes.append(scene)
                            current_time += duration
                            
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing scene line '{line}': {str(e)}")
                        continue
            
            # Sort scenes by scene number to ensure proper order
            scenes.sort(key=lambda x: x.scene_number)
            
            # Recalculate start times
            current_time = 0.0
            for scene in scenes:
                scene.start_time = current_time
                scene.end_time = scene.start_time + scene.duration
                current_time += scene.duration
            
            print(f"Successfully parsed {len(scenes)} scenes from AI response")
            return scenes
            
        except Exception as e:
            print(f"Error parsing AI scenes: {str(e)}")
            return []
    
    def _generate_narrative_script(self, prompt: str) -> List[Scene]:
        """Generate script for narrative content (original method)."""
        # Split into segments (sentences/paragraphs)
        segments = self._split_into_segments(prompt)
        
        # Create scenes with estimated durations
        scenes = self._create_scenes(segments)
        
        # Adjust timing to fit within total duration limit
        scenes = self._adjust_timing(scenes)
        
        return scenes
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += '.'
            
        return text
    
    def _split_into_segments(self, text: str) -> List[str]:
        """Split text into logical segments for scenes."""
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Group sentences into segments (aim for 5-10 scenes total)
        target_scenes = 7  # Sweet spot for 1-3 minute video
        sentences_per_scene = max(1, len(sentences) // target_scenes)
        
        segments = []
        current_segment = []
        
        for i, sentence in enumerate(sentences):
            current_segment.append(sentence)
            
            # Create segment when we have enough sentences or reach the end
            if (len(current_segment) >= sentences_per_scene and 
                len(segments) < target_scenes - 1) or i == len(sentences) - 1:
                segment_text = ' '.join(current_segment)
                if segment_text.strip():
                    segments.append(segment_text.strip())
                current_segment = []
        
        # Ensure we have at least one segment
        if not segments:
            segments = [text]
            
        return segments
    
    def _create_scenes(self, segments: List[str]) -> List[Scene]:
        """Create Scene objects from text segments."""
        scenes = []
        current_time = 0.0
        
        for i, segment in enumerate(segments):
            # Estimate duration based on text length (roughly 150 words per minute)
            word_count = len(segment.split())
            estimated_duration = max(
                self.config.scene_duration_min,
                min(self.config.scene_duration_max, word_count / 2.5)  # ~150 WPM
            )
            
            scene = Scene(
                text=segment,
                duration=estimated_duration,
                scene_number=i + 1,
                start_time=current_time
            )
            
            scenes.append(scene)
            current_time += estimated_duration
            
        return scenes
    
    def _adjust_timing(self, scenes: List[Scene]) -> List[Scene]:
        """Adjust scene durations to fit within total duration limit."""
        total_duration = sum(scene.duration for scene in scenes)
        
        if total_duration <= self.config.total_duration_max:
            return scenes
        
        # Scale down durations proportionally
        scale_factor = self.config.total_duration_max / total_duration
        
        current_time = 0.0
        for scene in scenes:
            scene.duration *= scale_factor
            scene.start_time = current_time
            scene.end_time = scene.start_time + scene.duration
            current_time += scene.duration
            
        return scenes
    
    def get_script_summary(self, scenes: List[Scene]) -> Dict[str, Any]:
        """Get a summary of the generated script."""
        total_duration = sum(scene.duration for scene in scenes)
        total_words = sum(len(scene.text.split()) for scene in scenes)
        
        return {
            "total_scenes": len(scenes),
            "total_duration": total_duration,
            "total_words": total_words,
            "average_scene_duration": total_duration / len(scenes) if scenes else 0,
            "scenes": [
                {
                    "scene_number": scene.scene_number,
                    "text": scene.text,
                    "duration": scene.duration,
                    "start_time": scene.start_time,
                    "end_time": scene.end_time
                }
                for scene in scenes
            ]
        }

    def create_video_script(self, prompt: str) -> List[Scene]:
        try:
            print(prompt, 'adf')
            # Use AI to create video script
            video_script_prompt = f"""
                Your role is to generate a prompt for video generation. The input is a scene description. A 9.5 second video must be generated from the scene description. This requires a prompt for video generation. The video must be realistic; sudden appearances and disappearances of people or objects are not permitted. Surrealistic phenomena, such as people flying, are also not permitted. The video must have a transition effect that lasts 0.5 seconds.The number of people and objects must not change.
                input example: 'This is a high-quality scene of live film captured by camera not photo, not cartoon. Remember this. Everything of the scene (door, trees, people, etc.) is sharp and clear. This is the real scene. This is the most important thing. Like Real handsome men and beautiful women, Real Environment, Real scene. description: A close-up of a brightly lit carousel spinning, with kids waving and laughing as the ride turns. The scene feels joyful and energetic. Overlay text reads: 'Games & Rides for Everyone!
                output example: 'The entire scene is realistic, sharp, and natural. A close-up of a brightly lit carousel spinning with colorful lights. Children are waving and laughing with joy as the ride turns, creating a lively and energetic atmosphere. The environment looks like a real outdoor fun fair on a sunny day. Overlay text in bold, playful font reads: ‘Games & Rides for Everyone!’ above is for 9.5 seconds. A smooth cinematic transition effect of 0.5 seconds is used at the end of the video.'

                Now Try with this "{prompt[315:]}"
                """
            
            # Make OpenAI API call to generate the scenes
            from openai import OpenAI
            client = OpenAI(api_key=self.config.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": video_script_prompt}],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_response = "This is a high-quality cinematic scene captured by a professional camera, not a photo, not a cartoon. The motion is continuous and natural — no sudden appearances or disappearances of people or objects, no surreal effects. " + response.choices[0].message.content
            print("AI Generated video script:")
            
            return ai_response
            
        except Exception as e:
            print(f"Error generating ad script with AI: {str(e)}")
            return None