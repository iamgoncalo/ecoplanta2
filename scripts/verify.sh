#!/usr/bin/env bash
set -euo pipefail

# EcoContainer + Planta Smart Homes - Quality Gate Verification
# This script MUST pass before any phase transition.
# Exit code 0 = all gates pass. Non-zero = blocked.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

run_gate() {
    local name="$1"
    local cmd="$2"
    local dir="${3:-$ROOT_DIR}"

    echo -e "\n${BLUE}[GATE] $name${NC}"
    echo "  Command: $cmd"

    cd "$dir"
    if eval "$cmd" 2>&1; then
        echo -e "  ${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "  ${RED}FAIL${NC}"
        FAILED=$((FAILED + 1))
    fi
}

skip_gate() {
    local name="$1"
    local reason="$2"
    echo -e "\n${YELLOW}[SKIP] $name - $reason${NC}"
    SKIPPED=$((SKIPPED + 1))
}

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} Quality Gate Verification${NC}"
echo -e "${BLUE} EcoContainer | Planta Smart Homes${NC}"
echo -e "${BLUE}========================================${NC}"

# Gate 1: Python lint (ruff)
if [ -d "$ROOT_DIR/backend" ] && command -v ruff &>/dev/null || [ -f "$ROOT_DIR/backend/.venv/bin/ruff" ]; then
    RUFF_CMD="ruff"
    if [ -f "$ROOT_DIR/backend/.venv/bin/ruff" ]; then
        RUFF_CMD="$ROOT_DIR/backend/.venv/bin/ruff"
    fi
    run_gate "Python Lint (ruff check)" "$RUFF_CMD check ." "$ROOT_DIR/backend"
    run_gate "Python Format (ruff format --check)" "$RUFF_CMD format --check ." "$ROOT_DIR/backend"
else
    skip_gate "Python Lint (ruff)" "ruff not installed"
fi

# Gate 2: Python type check (mypy)
if command -v mypy &>/dev/null || [ -f "$ROOT_DIR/backend/.venv/bin/mypy" ]; then
    MYPY_CMD="mypy"
    if [ -f "$ROOT_DIR/backend/.venv/bin/mypy" ]; then
        MYPY_CMD="$ROOT_DIR/backend/.venv/bin/mypy"
    fi
    run_gate "Python Types (mypy)" "$MYPY_CMD app/ --ignore-missing-imports" "$ROOT_DIR/backend"
else
    skip_gate "Python Types (mypy)" "mypy not installed"
fi

# Gate 3: Frontend lint + typecheck
if [ -d "$ROOT_DIR/frontend/node_modules" ]; then
    if [ -f "$ROOT_DIR/frontend/node_modules/.bin/tsc" ]; then
        run_gate "TypeScript Check (tsc)" "npx tsc --noEmit" "$ROOT_DIR/frontend"
    else
        skip_gate "TypeScript Check" "tsc not available"
    fi
else
    skip_gate "Frontend Checks" "node_modules not installed"
fi

# Gate 4: Python unit tests
if [ -d "$ROOT_DIR/backend/tests" ]; then
    PYTEST_CMD="pytest"
    if [ -f "$ROOT_DIR/backend/.venv/bin/pytest" ]; then
        PYTEST_CMD="$ROOT_DIR/backend/.venv/bin/pytest"
    fi
    run_gate "Python Unit Tests" "$PYTEST_CMD tests/unit/ -v --tb=short" "$ROOT_DIR/backend"
fi

# Gate 5: Python integration tests
if [ -d "$ROOT_DIR/backend/tests/integration" ] && [ "$(ls -A "$ROOT_DIR/backend/tests/integration/")" ]; then
    PYTEST_CMD="pytest"
    if [ -f "$ROOT_DIR/backend/.venv/bin/pytest" ]; then
        PYTEST_CMD="$ROOT_DIR/backend/.venv/bin/pytest"
    fi
    run_gate "Python Integration Tests" "$PYTEST_CMD tests/integration/ -v --tb=short" "$ROOT_DIR/backend"
fi

# Gate 6: Frontend build
if [ -d "$ROOT_DIR/frontend/node_modules" ]; then
    run_gate "Frontend Build (vite)" "npx vite build" "$ROOT_DIR/frontend"
else
    skip_gate "Frontend Build" "node_modules not installed"
fi

# Gate 7: Static JSON presence (after build)
if [ -d "$ROOT_DIR/frontend/dist/api" ]; then
    MISSING_JSON=0
    for f in health.json fabric.json fabric-scene.json frameworks.json sales.json intelligence.json deploy.json partners.json; do
        if [ ! -f "$ROOT_DIR/frontend/dist/api/$f" ]; then
            MISSING_JSON=1
            echo "  MISSING: dist/api/$f"
        fi
    done
    if [ "$MISSING_JSON" -eq 0 ]; then
        echo -e "  ${GREEN}All 8 static JSON files present in dist/api/${NC}"
        run_gate "Static JSON Presence" "true"
    else
        run_gate "Static JSON Presence" "false"
    fi
else
    skip_gate "Static JSON Presence" "frontend/dist not built yet"
fi

# Gate 8: E2E smoke test (Playwright)
if [ -d "$ROOT_DIR/frontend/node_modules/.bin" ] && command -v npx &>/dev/null; then
    if [ -f "$ROOT_DIR/frontend/playwright.config.ts" ]; then
        run_gate "E2E Smoke Tests (Playwright)" "npx playwright test --reporter=list" "$ROOT_DIR/frontend"
    else
        skip_gate "E2E Tests" "playwright.config.ts not found"
    fi
else
    skip_gate "E2E Tests" "Playwright not installed"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE} Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  ${GREEN}Passed:  $PASSED${NC}"
echo -e "  ${RED}Failed:  $FAILED${NC}"
echo -e "  ${YELLOW}Skipped: $SKIPPED${NC}"

if [ "$FAILED" -gt 0 ]; then
    echo -e "\n${RED}BLOCKED: $FAILED gate(s) failed. Fix before proceeding.${NC}"
    exit 1
else
    echo -e "\n${GREEN}ALL GATES PASSED${NC}"
    exit 0
fi
