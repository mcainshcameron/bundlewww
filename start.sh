#!/bin/bash

# BundleWWW - Development Startup Script
# Starts both backend and frontend in parallel

set -e

echo "Starting BundleWWW..."
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install Node.js first:"
    echo "  https://nodejs.org/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it with your OpenRouter API key:"
    echo "  OPENROUTERAPIKEY=your_key_here"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Install backend dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Installing backend dependencies..."
    uv venv
    uv pip install -e .
    echo ""
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

# Start backend
echo "Starting backend on http://localhost:8000"
uv run uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend
echo "Starting frontend on http://localhost:3000"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================"
echo "BundleWWW is running!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "============================================"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
