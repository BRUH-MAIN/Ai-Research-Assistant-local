#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI Research Assistant Development Environment${NC}"
echo -e "${YELLOW}=========================================${NC}"

# Ensure correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Run this script from the project root (where backend/ and frontend/ exist)${NC}"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        return 0
    else
        return 1
    fi
}

# Check port availability
if check_port 8000; then
    echo -e "${YELLOW}Warning: Port 8000 is already in use. Please stop any existing FastAPI server.${NC}"
fi
if check_port 3000; then
    echo -e "${YELLOW}Warning: Port 3000 is already in use. Please stop any existing Next.js server.${NC}"
fi

# Create .venv in root if not exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating .venv using uv in project root...${NC}"
    uv venv .venv
fi

# Activate virtual environment from root
echo -e "${YELLOW}Activating Python environment...${NC}"
source .venv/bin/activate

# Sync dependencies from root
echo -e "${YELLOW}Syncing backend dependencies using uv...${NC}"
uv sync

# Start backend
echo -e "${GREEN}Starting Backend (FastAPI)...${NC}"
cd backend
echo -e "${GREEN}Launching FastAPI server on http://localhost:8000${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend
sleep 3

# Start frontend
cd ../frontend
echo -e "${GREEN}Starting Frontend (Next.js)...${NC}"
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install

echo -e "${GREEN}Launching Next.js server on http://localhost:3000${NC}"
npm run dev &
FRONTEND_PID=$!

# Cleanup on Ctrl+C
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

trap cleanup INT TERM

echo -e "\n${GREEN}=== Development Environment Started ===${NC}"
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}Docs:     http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}"

wait
