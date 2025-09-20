@echo off
echo Setting up Student Study Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

@echo off
echo Setting up Student Study Assistant...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Install dependencies using venv python directly (to avoid PowerShell execution policy issues)
echo Installing core dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install fastapi==0.104.1
venv\Scripts\python.exe -m pip install uvicorn[standard]==0.24.0
venv\Scripts\python.exe -m pip install python-multipart==0.0.6
venv\Scripts\python.exe -m pip install python-dotenv==1.0.0
venv\Scripts\python.exe -m pip install aiofiles==23.2.1

REM Install document processing dependencies
echo Installing document processing libraries...
venv\Scripts\python.exe -m pip install pymupdf==1.23.14 || echo Warning: PyMuPDF installation failed - PDF processing will be limited
venv\Scripts\python.exe -m pip install python-docx==1.1.0 || echo Warning: python-docx installation failed - DOCX processing will be limited

REM Install AI dependencies
echo Installing AI libraries...
venv\Scripts\python.exe -m pip install groq==0.4.1 || echo Warning: Groq installation failed - AI features will be limited
venv\Scripts\python.exe -m pip install sentence-transformers==2.2.2 || echo Warning: sentence-transformers installation failed - will use basic search
venv\Scripts\python.exe -m pip install scikit-learn==1.3.2 || echo Warning: scikit-learn installation failed
venv\Scripts\python.exe -m pip install numpy==1.26.2 || echo Warning: numpy installation failed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your GROQ_API_KEY
    echo You can get a free API key from: https://console.groq.com/keys
    echo.
)

REM Create uploads directory
if not exist "uploads" (
    mkdir uploads
    echo Created uploads directory
)

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Edit .env file and add your GROQ_API_KEY
echo 2. Run: start_server.bat
echo.
pause