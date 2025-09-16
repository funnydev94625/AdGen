#!/usr/bin/env python3
"""
Django Web Server Startup Script for Video Generation Engine

This script starts the Django web server for the video generation application.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_environment():
    """Set up the Django environment."""
    # Add the parent directory to Python path to access video_engine
    parent_dir = os.path.join(os.path.dirname(__file__), '..')
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenServer.settings')
    
    # Setup Django
    django.setup()

def check_requirements():
    """Check if all required environment variables are set."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the server.")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr on Windows:")
        print("set OPENAI_API_KEY=your-api-key-here")
        return False
    
    return True

def main():
    """Main function to start the Django server."""
    print("🚀 Starting Video Generation Engine Web Server...")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the GenServer directory.")
        sys.exit(1)
    
    print("✅ Environment setup complete")
    print("✅ Required environment variables found")
    print("✅ Django configuration loaded")
    print()
    
    # Run Django development server
    print("🌐 Starting Django development server...")
    print("📱 Access the application at: http://127.0.0.1:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
