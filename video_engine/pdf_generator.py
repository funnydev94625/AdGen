"""
PDF generation module using reportlab for creating documents with text and images.
"""

import os
from typing import Optional, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import black, blue, darkblue
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class PDFGenerator:
    """Generates PDF documents with text content and images."""
    
    def __init__(self, config):
        self.config = config
        
    def generate_pdf(self, content: str, images: List[Optional[str]] = None, 
                    title: str = "Generated Document", filename: Optional[str] = None) -> Optional[str]:
        """
        Generate a PDF document from text content and optional images.
        
        Args:
            content: The main text content
            images: List of image file paths to include
            title: Document title
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated PDF file, or None if generation failed
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # Generate filename if not provided
            if not filename:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_document_{timestamp}"
            
            filepath = os.path.join(self.config.output_dir, f"{filename}.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=blue
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=12,
                alignment=TA_JUSTIFY,
                leftIndent=0,
                rightIndent=0
            )
            
            # Build content
            story = []
            
            # Add title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add content
            paragraphs = self._split_into_paragraphs(content)
            
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    # Add heading for each major section
                    if i == 0 or len(paragraph) > 100:  # First paragraph or long paragraphs
                        heading_text = f"Section {i+1}" if i > 0 else "Introduction"
                        story.append(Paragraph(heading_text, heading_style))
                    
                    # Add paragraph content
                    story.append(Paragraph(paragraph, body_style))
                    story.append(Spacer(1, 12))
                    
                    # Add image if available and it's a good spot
                    if images and i < len(images) and images[i] and os.path.exists(images[i]):
                        try:
                            # Add image
                            img = Image(images[i], width=5*inch, height=3*inch)
                            story.append(img)
                            story.append(Spacer(1, 20))
                        except Exception as e:
                            print(f"Warning: Could not add image {images[i]}: {str(e)}")
            
            # Add footer
            story.append(Spacer(1, 30))
            footer_text = f"Generated on {self._get_current_date()}"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            print(f"✅ PDF generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None
    
    def generate_pdf_from_scenes(self, scenes: List, images: List[Optional[str]] = None, 
                               title: str = "Video Script Document") -> Optional[str]:
        """
        Generate a PDF from video scenes with images.
        
        Args:
            scenes: List of Scene objects
            images: List of image file paths corresponding to scenes
            title: Document title
            
        Returns:
            Path to the generated PDF file, or None if generation failed
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.config.output_dir, exist_ok=True)
            
            # Generate filename
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_script_{timestamp}"
            filepath = os.path.join(self.config.output_dir, f"{filename}.pdf")
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=darkblue
            )
            
            scene_heading_style = ParagraphStyle(
                'SceneHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=15,
                textColor=blue
            )
            
            scene_text_style = ParagraphStyle(
                'SceneText',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=10,
                alignment=TA_JUSTIFY
            )
            
            scene_info_style = ParagraphStyle(
                'SceneInfo',
                parent=styles['Normal'],
                fontSize=9,
                spaceAfter=15,
                textColor=colors.grey
            )
            
            # Build content
            story = []
            
            # Add title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add summary
            total_duration = sum(scene.duration for scene in scenes)
            summary_text = f"This document contains {len(scenes)} scenes with a total duration of {total_duration:.1f} seconds."
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Add each scene
            for i, scene in enumerate(scenes):
                # Scene heading
                scene_heading = f"Scene {scene.scene_number}: {scene.start_time:.1f}s - {scene.end_time:.1f}s"
                story.append(Paragraph(scene_heading, scene_heading_style))
                
                # Scene text
                story.append(Paragraph(scene.text, scene_text_style))
                
                # Scene info
                info_text = f"Duration: {scene.duration:.1f} seconds | Word count: {len(scene.text.split())}"
                story.append(Paragraph(info_text, scene_info_style))
                
                # Add image if available
                if images and i < len(images) and images[i] and os.path.exists(images[i]):
                    try:
                        img = Image(images[i], width=4*inch, height=2.5*inch)
                        story.append(img)
                        story.append(Spacer(1, 15))
                    except Exception as e:
                        print(f"Warning: Could not add image for scene {i+1}: {str(e)}")
                
                # Add page break after every 3 scenes (except the last)
                if (i + 1) % 3 == 0 and i < len(scenes) - 1:
                    story.append(PageBreak())
                else:
                    story.append(Spacer(1, 15))
            
            # Add footer
            story.append(Spacer(1, 30))
            footer_text = f"Generated on {self._get_current_date()} | Total scenes: {len(scenes)}"
            story.append(Paragraph(footer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            print(f"✅ PDF generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return None
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into logical paragraphs."""
        # Split by double newlines or periods followed by space
        paragraphs = []
        
        # First try splitting by double newlines
        if '\n\n' in text:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        else:
            # Split by sentences and group them
            sentences = text.split('. ')
            current_paragraph = ""
            
            for sentence in sentences:
                if not sentence.endswith('.'):
                    sentence += '.'
                
                current_paragraph += sentence + " "
                
                # Create paragraph every 3-4 sentences or if it gets long
                if len(current_paragraph.split()) > 50 or len(current_paragraph.split('.')) > 3:
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
            
            # Add remaining text
            if current_paragraph.strip():
                paragraphs.append(current_paragraph.strip())
        
        return paragraphs
    
    def _get_current_date(self) -> str:
        """Get current date in a readable format."""
        import datetime
        return datetime.datetime.now().strftime("%B %d, %Y")
    
    def cleanup_pdfs(self, pdf_paths: List[Optional[str]]):
        """Clean up generated PDF files."""
        for pdf_path in pdf_paths:
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception as e:
                    print(f"Error cleaning up PDF {pdf_path}: {str(e)}")
