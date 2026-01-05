@echo off
REM BundleWWW - Windows Startup Script
REM Starts both backend and frontend

echo Starting BundleWWW...
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv is not installed. Please install it first:
    echo   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed. Please install Node.js first:
    echo   https://nodejs.org/
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found. Please create it with your OpenRouter API key:
    echo   OPENROUTERAPIKEY=your_key_here
    exit /b 1
)

REM Install backend dependencies if needed
if not exist .venv (
    echo Installing backend dependencies...
    call uv venv
    call uv pip install -e .
    echo.
)

REM Install frontend dependencies if needed
if not exist frontend\node_modules (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo.
)

REM Start backend and frontend
echo Starting backend on http://localhost:8000
echo Starting frontend on http://localhost:3000
echo.
echo ============================================
echo BundleWWW is running!
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.

REM Start both processes
start "BundleWWW Backend" cmd /k "uv run uvicorn backend.app.main:app --reload --port 8000"
timeout /t 2 /nobreak >nul
start "BundleWWW Frontend" cmd /k "cd frontend && npm run dev"

echo Both services started in separate windows.
echo Close those windows to stop the services.
