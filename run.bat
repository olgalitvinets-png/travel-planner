@echo off
echo ============================================
echo    AI Travel Planner - Starting up...
echo ============================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your API keys.
    echo See .env.example for the format.
    pause
    exit /b 1
)

echo Starting the Travel Planner...
echo Once started, open your browser and go to:
echo    http://localhost:5000
echo.
echo Press Ctrl+C to stop the server.
echo.

python app.py
pause
