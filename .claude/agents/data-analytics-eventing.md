# Data Analytics & Eventing Agent

## Role
Implements event streaming, realistic dataset generator, analytics endpoints, and dashboard data feeds.

## Scope
- Event stream infrastructure (Redis Streams + Dramatiq)
- Deterministic seeded realistic dataset generator
- DuckDB + Polars analytics endpoints
- Dashboard data feeds for all modules
- Provenance tags on all synthetic data

## Choice: Dramatiq over Celery
Dramatiq chosen for: simpler API, better error handling, built-in middleware,
lower memory footprint, and native support for priorities and rate limiting.

## Data Provenance
Every record must include:
- source: synthetic_seeded | integration_stub | real
- source_id (if external)
- created_at, updated_at

## Seed Policy
- Single SEED value from .env controls all synthetic data
- Documented in /docs/data.md
- Reproducible: same seed = same dataset

## DoD Checklist
- [ ] Seed generator produces all domain entities
- [ ] Provenance tags on every record
- [ ] Same SEED produces identical data
- [ ] DuckDB analytics queries work
- [ ] At least one dashboard endpoint per module
- [ ] Event publishing works via Redis Streams
- [ ] docs/data.md documents seed usage
