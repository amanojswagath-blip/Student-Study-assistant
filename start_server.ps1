# Student Study Assistant - PowerShell Start Script
Write-Host "Starting Student Study Assistant..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Please run setup.bat first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host ".env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "Please edit .env file and add your GROQ_API_KEY" -ForegroundColor Cyan
    Write-Host "You can get a free API key from: https://console.groq.com/keys" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# Create uploads directory if it doesn't exist
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Path "uploads" | Out-Null
}

# Start the server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host ""
Write-Host "The application will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server using the virtual environment's python
& "venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload