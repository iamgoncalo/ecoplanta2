# Architecture Overview

## System: EcoContainer Technologies OS + Planta Smart Homes Brain

### Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| 3D Rendering | three.js via @react-three/fiber |
| API | FastAPI, Pydantic v2, OpenAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Cache/Events | Redis 7 (Streams + Dramatiq) |
| Analytics | DuckDB + Polars |
| Observability | structlog (structured logging) |
| Testing | pytest, httpx, Playwright |

### Monorepo Layout

```
ecoplanta2/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, security, logging
│   │   ├── db/       # Database session, engine
│   │   ├── models/   # SQLAlchemy domain models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── seed/     # Deterministic data generator
│   │   └── services/ # Business logic
│   ├── alembic/      # Database migrations
│   └── tests/        # Unit + integration tests
├── frontend/         # React + Vite application
│   └── src/
│       ├── api/      # API client
│       ├── components/ # Reusable UI components
│       ├── hooks/    # React Query hooks
│       └── pages/    # Module pages (6 modules)
├── infra/            # Docker, CI configs
├── docs/             # Documentation
├── scripts/          # Dev and verification scripts
└── docker-compose.yml
```

### Module Architecture

Each of the 6 navbar modules follows the same pattern:
1. **Backend route** (`/api/{module}`) returns seeded/real data
2. **Pydantic schema** defines response shape
3. **Frontend page** fetches via React Query and renders
4. **Tests** cover the full path

### Security Model

- JWT-based auth with dev mode bypass
- RBAC roles: admin, manager, operator, viewer
- Audit logging on all state mutations
- CORS restricted to known origins
- Security headers (CSP, HSTS, X-Frame-Options)
