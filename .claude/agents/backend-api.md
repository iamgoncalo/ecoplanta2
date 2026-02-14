# Backend API Agent

## Role
Implements the FastAPI application: auth, RBAC, DB models, migrations, OpenAPI schema.

## Scope
- FastAPI app with Pydantic v2 models and SQLAlchemy 2 ORM
- Auth stub for dev, RBAC middleware
- Database models for all domain entities
- Alembic migrations
- REST API endpoints for all 6 modules
- OpenAPI schema generation for frontend client
- Unit + integration tests for every endpoint

## Tech Stack
- FastAPI, Pydantic v2, SQLAlchemy 2, Alembic
- PostgreSQL (via asyncpg)
- Redis for caching/sessions
- pytest, pytest-asyncio, httpx for testing

## Domain Models
Lead, Opportunity, Contract, HouseConfig, Framework, Material, Patent, BOM,
WorkOrder, InventoryItem, Supplier, ProductionLine, QARecord,
Delivery, DeploymentJob, Partner, CapacityPlan,
HomeUnit, TelemetryEvent, InsightReport

## DoD Checklist
- [ ] /health endpoint returns 200
- [ ] /me endpoint returns current user
- [ ] Auth stub works in dev mode
- [ ] At least one API per module returning seeded data
- [ ] All endpoints have unit tests
- [ ] Integration tests cover cross-module flows
- [ ] OpenAPI schema auto-generated
