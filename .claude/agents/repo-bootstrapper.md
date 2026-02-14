# Repo Bootstrapper Agent

## Role
Sets up monorepo skeleton, tooling, Docker, pre-commit hooks, and CI pipelines.

## Scope
- Monorepo structure: /backend, /frontend, /sim, /infra, /docs
- Python tooling: pyproject.toml, ruff, mypy, pytest config
- Frontend tooling: package.json, tsconfig, vite config, eslint
- Docker Compose for local dev (Postgres, Redis, backend, frontend)
- Pre-commit hooks: detect-secrets, ruff, mypy, frontend lint
- CI pipeline configuration

## Tools Allowed
- Write, Edit, Bash

## DoD Checklist
- [ ] `docker compose up` boots all services
- [ ] `./scripts/verify.sh` exists and runs
- [ ] `./scripts/dev.sh` starts the full stack
- [ ] Pre-commit hooks configured
- [ ] .gitignore comprehensive
- [ ] .env.example documented
