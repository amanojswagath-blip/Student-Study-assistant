@echo off
echo Starting Student Study Assistant...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo .env file not found. Creating from template...
    copy .env.example .env
    echo.
    echo Please edit .env file and add your GROQ_API_KEY
    echo You can get a free API key from: https://console.groq.com/keys
    echo.
    pause
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    mkdir uploads
)

REM Start the server using venv python directly
echo Starting FastAPI server...
echo.
echo The application will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload