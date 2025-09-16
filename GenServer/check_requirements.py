#!/usr/bin/env python3
"""
Requirements check script for deployment troubleshooting.
"""

import sys
import os

def check_requirements():
    """Check if all required packages are installed."""
    print("🔍 Checking requirements...")
    print("=" * 50)
    
    required_packages = [
        'django',
        'moviepy',
        'imageio',
        'imageio_ffmpeg',
        'pillow',
        'numpy',
        'requests',
        'openai',
        'gtts',
        'pydub',
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'imageio_ffmpeg':
                import imageio_ffmpeg
                print(f"✅ {package}: {imageio_ffmpeg.__version__}")
            elif package == 'pillow':
                import PIL
                print(f"✅ {package}: {PIL.__version__}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package}: {version}")
        except ImportError as e:
            print(f"❌ {package}: Not installed ({e})")
            missing_packages.append(package)
    
    print("=" * 50)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages:")
        print("pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required packages are installed!")
        return True

def check_moviepy_imports():
    """Check MoviePy specific imports."""
    print("\n🎬 Checking MoviePy imports...")
    print("=" * 50)
    
    moviepy_imports = [
        'moviepy.editor',
        'moviepy.video.compositing.concatenate',
        'moviepy.video.fx.resize',
        'moviepy.video.fx.fadein',
        'moviepy.video.fx.fadeout',
        'moviepy.audio.fx.volumex'
    ]
    
    for import_name in moviepy_imports:
        try:
            __import__(import_name)
            print(f"✅ {import_name}")
        except ImportError as e:
            print(f"❌ {import_name}: {e}")
    
    print("=" * 50)

def check_environment():
    """Check environment variables."""
    print("\n🌍 Checking environment variables...")
    print("=" * 50)
    
    env_vars = ['OPENAI_API_KEY', 'SECRET_KEY', 'DEBUG']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'OPENAI_API_KEY':
                # Don't print the actual key
                print(f"✅ {var}: Set (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    print("=" * 50)

if __name__ == '__main__':
    print("🚀 Video Generation Engine - Requirements Check")
    print("=" * 50)
    
    # Check basic requirements
    requirements_ok = check_requirements()
    
    # Check MoviePy imports
    check_moviepy_imports()
    
    # Check environment
    check_environment()
    
    print("\n📋 Summary:")
    if requirements_ok:
        print("✅ All basic requirements are met!")
    else:
        print("❌ Some requirements are missing!")
        sys.exit(1)
