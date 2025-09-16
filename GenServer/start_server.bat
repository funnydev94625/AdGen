@echo off
echo ========================================
echo Video Generation Engine - Web Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ERROR: manage.py not found
    echo Please run this script from the GenServer directory
    pause
    exit /b 1
)

REM Check for OpenAI API key
if "%OPENAI_API_KEY%"=="" (
    echo WARNING: OPENAI_API_KEY environment variable not set
    echo Please set your OpenAI API key:
    echo set OPENAI_API_KEY=your-api-key-here
    echo.
    set /p OPENAI_API_KEY="Enter your OpenAI API key: "
    if "%OPENAI_API_KEY%"=="" (
        echo ERROR: OpenAI API key is required
        pause
        exit /b 1
    )
)

echo Starting Django web server...
echo.
echo Access the application at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python run_server.py

pause
