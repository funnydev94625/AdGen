# Video Generation Engine - Web Server

A Django-based web interface for the Video Generation Engine that allows users to create videos from text prompts using AI-powered content generation.

## Features

- 🎥 **Video Generation**: Create professional videos from text descriptions
- 🖼️ **AI Image Generation**: Generate high-quality images using DALL-E
- 🎤 **Text-to-Speech**: Convert text to natural-sounding voice narration
- 🎬 **Video Assembly**: Combine images, audio, and transitions into videos
- 🌐 **Web Interface**: User-friendly web interface with real-time progress tracking
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- ⚡ **Real-time Updates**: Live progress updates during video generation

## Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- FFmpeg installed on your system

### Installation

1. **Navigate to the GenServer directory:**
   ```bash
   cd GenServer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # On Windows
   set OPENAI_API_KEY=your-api-key-here
   
   # On Linux/Mac
   export OPENAI_API_KEY=your-api-key-here
   ```

4. **Run the server:**
   ```bash
   python run_server.py
   ```

5. **Access the application:**
   Open your browser and go to: http://127.0.0.1:8000

## Usage

### Basic Usage

1. **Enter a prompt**: Describe what you want to create in your video
2. **Click Generate**: The system will start creating your video
3. **Monitor progress**: Watch the real-time progress updates
4. **Download**: Once complete, download your generated video

### Example Prompts

- **Event Flyer**: "Create a vibrant flyer for the 'Summer Fun Fair' happening on July 20, 2025, from 10 AM to 4 PM at Maplewood Park. Include a headline that says 'Join Us for a Day of Family Fun!' and a short description mentioning games, food stalls, a petting zoo, and live music."

- **Café Menu**: "Design a café menu for 'The Cozy Corner Café.' Include the following sections and items: Appetizers - 'Garlic Bread Bites' (£3.50), 'Bruschetta' (£4.00); Main Courses - 'Classic Beef Lasagna' (£9.95), 'Vegetarian Quiche' (£8.50); Desserts - 'Chocolate Fudge Cake' (£4.50), 'Lemon Tart' (£4.00)."

- **Sale Promotion**: "Generate an image-based flyer for a 'Grand Opening Sale' at 'Bella Boutique' on August 5, 2025. The flyer should have a big bold headline that says '50% Off All Items!' and include images of clothing racks and accessories."

## API Endpoints

### Generate Video
- **URL**: `/generate/`
- **Method**: POST
- **Body**: `{"prompt": "Your video description"}`
- **Response**: `{"success": true, "task_id": "uuid", "message": "Video generation started"}`

### Check Status
- **URL**: `/status/<task_id>/`
- **Method**: GET
- **Response**: `{"success": true, "status": "running", "progress": 50, "message": "Generating images..."}`

### Download Video
- **URL**: `/download/<filename>/`
- **Method**: GET
- **Response**: Video file download

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `RUNWAY_API_KEY`: Your RunwayML API key (optional, for advanced video generation)

### Django Settings

The server uses the following key settings:

- **Debug Mode**: Enabled by default for development
- **Static Files**: Served from `/static/` directory
- **Media Files**: Served from `/media/` directory
- **Output Directory**: Videos saved to `/output/` directory
- **Temp Directory**: Temporary files stored in `/temp/` directory

## File Structure

```
GenServer/
├── GenServer/              # Django project settings
│   ├── __init__.py
│   ├── settings.py         # Django configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── video_generator/       # Django app
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py            # App URL routing
│   └── views.py           # View functions
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   └── video_generator/   # App-specific templates
├── static/                # Static files (CSS, JS)
│   ├── css/
│   └── js/
├── media/                 # User uploads
├── output/                # Generated videos
├── temp/                  # Temporary files
├── logs/                  # Application logs
├── manage.py              # Django management script
├── run_server.py          # Custom startup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

### Running in Development Mode

```bash
python manage.py runserver
```

### Running with Custom Settings

```bash
python manage.py runserver --settings=GenServer.settings
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn GenServer.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "GenServer.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Found**
   - Ensure the `OPENAI_API_KEY` environment variable is set
   - Check that the API key is valid and has sufficient credits

2. **FFmpeg Not Found**
   - Install FFmpeg on your system
   - Ensure it's available in your system PATH

3. **Permission Errors**
   - Check that the application has write permissions to output and temp directories
   - Ensure the user running the server has appropriate file system access

4. **Memory Issues**
   - Video generation can be memory-intensive
   - Consider running on a system with at least 4GB RAM
   - Monitor system resources during generation

### Logs

Check the application logs in the `logs/` directory for detailed error information:

```bash
tail -f logs/django.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Check the troubleshooting section above
- Review the application logs
- Open an issue on the project repository

## Changelog

### Version 1.0.0
- Initial release
- Django web interface
- Real-time progress tracking
- Video generation from text prompts
- Responsive design
- Example prompts and tips
