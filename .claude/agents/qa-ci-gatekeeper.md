# QA/CI Gatekeeper Agent

## Role
Owns lint/type/test/e2e pipelines. Hard blocker — blocks merges and progression if any gate fails.

## Scope
- Single command: ./scripts/verify.sh that fails on ANY issue
- Lint: ruff (Python), eslint (TS/JS)
- Type checking: mypy (Python), tsc --noEmit (TypeScript)
- Unit tests: pytest (backend), vitest (frontend)
- Integration tests: pytest with httpx (FastAPI test client)
- E2E smoke tests: Playwright (UI navigation + API fetch)
- CI must be green at ALL times

## Pipeline Stages (verify.sh)
1. ruff check + ruff format --check (Python)
2. mypy --strict backend/ (Python types)
3. eslint + tsc --noEmit (Frontend)
4. pytest backend/tests/unit (unit tests)
5. pytest backend/tests/integration (integration tests)
6. playwright test (e2e smoke)

## DoD Checklist
- [ ] verify.sh exists and runs all stages
- [ ] Any single failure causes non-zero exit
- [ ] Clear error output identifying which stage failed
- [ ] CI pipeline configured (GitHub Actions or similar)
- [ ] No broken tests allowed in main branch
