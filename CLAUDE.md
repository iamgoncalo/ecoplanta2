# EcoContainer Technologies OS + Planta Smart Homes Brain

## Quick Start

### Run the full stack (Docker)
```bash
./scripts/dev.sh --docker
```

### Run locally (no Docker)
```bash
./scripts/dev.sh --local
```

### Run backend only
```bash
cd backend
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Run frontend only
```bash
cd frontend
npm install
npm run dev
```

### Endpoints
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

## Verify (Quality Gates)
```bash
./scripts/verify.sh
```

This runs ALL quality gates in order:
1. `ruff check` + `ruff format --check` (Python lint)
2. `mypy` (Python type check)
3. `tsc --noEmit` (TypeScript check)
4. `pytest tests/unit/` (Python unit tests)
5. `pytest tests/integration/` (Python integration tests)
6. `playwright test` (E2E smoke tests)

**Any failure blocks progress.** Fix before proceeding.

## Repo Structure
```
/backend          FastAPI + SQLAlchemy + Pydantic
/frontend         React + TypeScript + Vite + Tailwind + three.js
/sim              (future) Panda3D/Ursina Python client
/infra            Docker, scripts, CI
/docs             Handbook, architecture, runbooks
/scripts          dev.sh, verify.sh
/.claude/agents   Subagent definitions
```

## Conventions

### Python
- Python 3.11+, async everywhere
- Pydantic v2 for schemas
- SQLAlchemy 2.0 mapped_column style
- ruff for linting/formatting
- mypy for type checking
- structlog for logging

### Frontend
- React 18 + TypeScript strict
- Tailwind CSS + shadcn/ui components
- React Query for data fetching
- three.js via @react-three/fiber for 3D

### Data Provenance
Every record must include:
- `source`: `synthetic_seeded` | `integration_stub` | `real`
- `source_id`: external ID if applicable
- `created_at`, `updated_at`: timestamps

Seed controlled by `SEED` env var (default: 42). Same seed = same data.

### Truth Constraints
- "Planta Smart Homes" (NOT "Planta Home OS")
- EcoContainer uses HIGH-QUALITY materials only
- NO LSF (Light Steel Frame) - excluded explicitly
- NO weak materials
- Patent-ready R&D on smart materials

### Modules
1. Fabric (2D/3D factory)
2. Frameworks (structures + patents + smart materials)
3. Sales (CRM pipeline)
4. Intelligence (LBM physical AI layer)
5. Deploy (delivery + installation)
6. Partners (EU network)
