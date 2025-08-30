#!/bin/bash

# Simple startup script for the paper search application
echo "🚀 Starting AI Research Assistant with Paper Search..."

# Create data directory if it doesn't exist
mkdir -p /home/bharath/Documents/DBMS/data

# Function to start backend
start_backend() {
    echo "📡 Starting backend server..."
    cd /home/bharath/Documents/DBMS/Ai-Research-Assistant-local/backend
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting frontend server..."
    cd /home/bharath/Documents/DBMS/Ai-Research-Assistant-local/frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
}

# Kill any existing processes on ports 8000 and 3000
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
sleep 2

# Start both services
start_backend
sleep 5
start_frontend

echo ""
echo "🎉 Application started!"
echo "📡 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs" 
echo "🎨 Frontend: http://localhost:3000"
echo "📄 Paper Search: http://localhost:3000/papers"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait
