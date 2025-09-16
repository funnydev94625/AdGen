#!/bin/bash
# Build script for Render.com deployment

echo "🚀 Starting build process..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check requirements
echo "🔍 Checking requirements..."
python check_requirements.py

# Run Django setup
echo "⚙️ Setting up Django..."
python manage.py migrate
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"
