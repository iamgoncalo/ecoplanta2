# Static Data Generator Agent

## Role
Generates deterministic JSON payloads via Python for GitHub Pages preview mode.

## Scope
- Python script that calls the seed generator and outputs static JSON files
- JSON files placed in frontend/public/api/ for fallback mode
- All records include provenance tags (source, source_id, created_at, updated_at)
- Frontend API client falls back to static JSON when backend unreachable

## Tools Allowed
- Write, Edit, Bash (Python)

## DoD Checklist
- [ ] scripts/generate_static_api.py exists and runs
- [ ] Outputs JSON to frontend/public/api/*.json
- [ ] All provenance fields present
- [ ] Same seed produces identical JSON
- [ ] Frontend falls back gracefully to static data
