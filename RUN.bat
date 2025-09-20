@echo off
echo 🎓 Student Study Assistant - One-Click Launcher
echo.

REM First-time setup if needed
if not exist "venv" (
    echo Running first-time setup...
    call setup.bat
    if errorlevel 1 exit /b 1
)

REM Start the server
call start_server.bat