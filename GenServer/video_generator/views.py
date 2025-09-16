import os
import sys
import json
import uuid
import threading
import time
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

# Add the parent directory to the Python path to import video_engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from video_engine import VideoEngine, Config

logger = logging.getLogger(__name__)

# In-memory storage for task status (since we're not using a database)
task_status_storage = {}

# Example prompts (static data)
EXAMPLE_PROMPTS = [
    {
        'id': 1,
        'title': 'Summer Fun Fair',
        'description': 'Create a vibrant flyer for the Summer Fun Fair',
        'prompt': "Create a vibrant flyer for the 'Summer Fun Fair' happening on July 20, 2025, from 10 AM to 4 PM at Maplewood Park. Include a headline that says 'Join Us for a Day of Family Fun!' and a short description mentioning games, food stalls, a petting zoo, and live music. Add images of a carousel, kids playing games, and a food stall."
    },
    {
        'id': 2,
        'title': 'Café Menu',
        'description': 'Design a café menu for The Cozy Corner Café',
        'prompt': "Design a café menu for 'The Cozy Corner Café.' Include the following sections and items: Appetizers - 'Garlic Bread Bites' (£3.50), 'Bruschetta' (£4.00); Main Courses - 'Classic Beef Lasagna' (£9.95), 'Vegetarian Quiche' (£8.50); Desserts - 'Chocolate Fudge Cake' (£4.50), 'Lemon Tart' (£4.00); Beverages - 'Cappuccino' (£2.80), 'Fresh Lemonade' (£2.50). Add a small image of the lasagna and the lemon tart."
    },
    {
        'id': 3,
        'title': 'Grand Opening Sale',
        'description': 'Generate an image-based flyer for a Grand Opening Sale',
        'prompt': "Generate an image-based flyer for a 'Grand Opening Sale' at 'Bella Boutique' on August 5, 2025. The flyer should have a big bold headline that says '50% Off All Items!' and include images of clothing racks and accessories. Add text boxes for the store address and contact number."
    }
]

def home(request):
    """Home page view."""
    context = {
        'title': 'Video Generation Engine',
        'examples': EXAMPLE_PROMPTS[:3],  # Show first 3 examples
    }
    return render(request, 'video_generator/home.html', context)

def examples(request):
    """Examples page view."""
    context = {
        'title': 'Example Prompts',
        'examples': EXAMPLE_PROMPTS,
    }
    return render(request, 'video_generator/examples.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def generate_video(request):
    """Generate video from text prompt."""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            return JsonResponse({
                'success': False,
                'error': 'OpenAI API key not found. Please set OPENAI_API_KEY environment variable.'
            }, status=500)
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_status_storage[task_id] = {
            'status': 'pending',
            'progress': 0,
            'message': 'Initializing video generation...',
            'video_path': None,
            'error': None,
            'created_at': time.time()
        }
        
        # Start video generation in background thread
        thread = threading.Thread(
            target=_generate_video_background,
            args=(task_id, prompt)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'message': 'Video generation started'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in generate_video: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

def _generate_video_background(task_id, prompt):
    """Background task for video generation."""
    try:
        # Update status
        # task_status_storage[task_id].update({
        #     'status': 'running',
        #     'progress': 10,
        #     'message': 'Initializing video engine...'
        # })
        
        # Initialize video engine
        engine = VideoEngine()
        
        # Update status
        # task_status_storage[task_id].update({
        #     'progress': 20,
        #     'message': 'Validating setup...'
        # })
        
        # Validate setup
        if not engine.validate_setup():
            task_status_storage[task_id].update({
                'status': 'failed',
                'error': 'Setup validation failed. Please check your configuration.'
            })
            return
        
        # Update status
        # task_status_storage[task_id].update({
        #     'progress': 30,
        #     'message': 'Generating video content...'
        # })
        
        # Generate video
        video_path = engine.generate_video(prompt, cleanup=True)
        
        if video_path:
            # Update status
            task_status_storage[task_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Video generation completed successfully!',
                'video_path': video_path
            })
        else:
            task_status_storage[task_id].update({
                'status': 'failed',
                'error': 'Video generation failed. Please check the error messages.'
            })
            
    except Exception as e:
        logger.error(f"Error in background video generation: {str(e)}")
        task_status_storage[task_id].update({
            'status': 'failed',
            'error': f'Video generation error: {str(e)}'
        })

def task_status(request, task_id):
    print('task_status', task_id)
    print('task_status_storage', task_status_storage)
    """Get status of a video generation task."""
    if task_id not in task_status_storage:
        return JsonResponse({
            'success': False,
            'error': 'Task not found'
        }, status=404)
    
    task_data = task_status_storage[task_id]
    
    return JsonResponse({
        'success': True,
        'task_id': task_id,
        'status': task_data['status'],
        'progress': task_data['progress'],
        'message': task_data['message'],
        'video_path': task_data.get('video_path').split('\\')[-1] if task_data.get('video_path') else task_data.get('video_path'),
        'error': task_data.get('error'),
        'created_at': task_data['created_at']
    })

def download_file(request, filename):
    """Download generated video file."""
    try:
        # Security check - only allow specific file types
        if not filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise Http404("File type not allowed")
        
        # Check if file exists in output directory
        print('filename', filename)
        file_path = os.path.join(settings.VIDEO_OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            raise Http404("File not found")
        
        # Read file and return as response
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='video/mp4')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        raise Http404("File not found")

def get_generation_stats(request):
    """Get video generation statistics."""
    try:
        # Initialize engine to get stats
        engine = VideoEngine()
        stats = engine.get_generation_stats()
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting generation stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error getting stats: {str(e)}'
        }, status=500)
