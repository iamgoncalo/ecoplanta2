#!/usr/bin/env bash
set -euo pipefail

# EcoContainer + Planta Smart Homes - Development Stack Launcher
# Usage: ./scripts/dev.sh [--docker | --local]

MODE="${1:---local}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} EcoContainer | Planta Smart Homes${NC}"
echo -e "${BLUE} Development Stack${NC}"
echo -e "${BLUE}========================================${NC}"

if [ "$MODE" = "--docker" ]; then
    echo -e "${GREEN}Starting with Docker Compose...${NC}"
    cd "$ROOT_DIR"
    docker compose up --build
elif [ "$MODE" = "--local" ]; then
    echo -e "${GREEN}Starting local development servers...${NC}"

    # Check for .env
    if [ ! -f "$ROOT_DIR/.env" ]; then
        echo -e "${YELLOW}No .env found. Copying from .env.example...${NC}"
        cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    fi

    # Export env vars
    set -a
    source "$ROOT_DIR/.env"
    set +a

    # Start backend
    echo -e "${GREEN}Starting backend (FastAPI)...${NC}"
    cd "$ROOT_DIR/backend"
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        .venv/bin/pip install -e ".[dev]"
    fi
    .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!

    # Start frontend
    echo -e "${GREEN}Starting frontend (Vite)...${NC}"
    cd "$ROOT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN} Backend:  http://localhost:8000${NC}"
    echo -e "${GREEN} Frontend: http://localhost:5173${NC}"
    echo -e "${GREEN} API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}========================================${NC}"

    # Trap cleanup
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
else
    echo "Usage: ./scripts/dev.sh [--docker | --local]"
    exit 1
fi
