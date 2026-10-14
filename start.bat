@echo off
setlocal enabledelayedexpansion

title CivicPulse AI — Smart Civic Issue Platform Launcher
color 0B

echo =====================================================================
echo           CIVICPULSE AI — SMART CIVIC REPORTING PLATFORM
echo               College Academic Project & Review Edition
echo =====================================================================
echo.

:: 1. Check Python Installation
echo [1/5] Verifying Python runtime environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo   -- Found %PYTHON_VER%

:: 2. Check and Create Virtual Environment
echo.
echo [2/5] Checking Python Virtual Environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo   -- Virtual environment not detected. Creating fresh .venv...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   -- Virtual environment created successfully.
) else (
    echo   -- Existing virtual environment located.
)

:: Activate Virtual Environment
call .\.venv\Scripts\activate.bat

:: 3. Check and Install Dependencies
echo.
echo [3/5] Verifying required Python dependencies...
echo   -- Note: Active internet connection required for initial package download.
python -m pip install --default-timeout=120 --retries=5 -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARNING] Package installation encountered an issue.
    echo Retrying with user pip cache...
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Could not install packages. Check internet connection.
        pause
        exit /b 1
    )
)
echo   -- Dependencies verified and up to date.

:: 4. Environment Configuration
echo.
echo [4/5] Checking local environment configuration (.env)...
if not exist ".env" (
    if exist ".env.example" (
        echo   -- Generating local .env from .env.example template...
        copy .env.example .env >nul
    ) else (
        echo   -- Creating default .env configuration...
        (
            echo HOST=127.0.0.1
            echo PORT=8000
            echo DEBUG=True
            echo DATABASE_URL=sqlite:///./civicpulse.db
            echo ADMIN_USERNAME=admin
            echo ADMIN_PASSWORD=admin123
            echo JWT_SECRET_KEY=civicpulse-ai-secure-secret-key-change-in-production-2026
            echo JWT_ALGORITHM=HS256
            echo ACCESS_TOKEN_EXPIRE_MINUTES=480
            echo GEMINI_API_KEY=
            echo SEED_DEMO_DATA=True
        ) > .env
    )
    echo   -- Local .env configuration ready.
) else (
    echo   -- Existing .env configuration preserved.
)

:: 5. Initialize Database & Launch Application
echo.
echo [5/5] Launching CivicPulse AI Web Platform...
echo =====================================================================
echo   Application Dashboard: http://127.0.0.1:8000
echo   FastAPI Swagger Docs:  http://127.0.0.1:8000/docs
echo   Admin Default Login:   Username: admin  ^|  Password: admin123
echo =====================================================================
echo   Press CTRL+C anytime in this window to stop the server.
echo.

:: Automatically open default browser after a 2-second delay in background
start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: Start Uvicorn ASGI Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
