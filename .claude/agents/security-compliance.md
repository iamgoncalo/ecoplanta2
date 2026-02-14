# Security & Compliance Agent

## Role
Threat modeling, RBAC matrices, audit logs, secrets scanning, dependency hygiene.

## Scope
- RBAC role definitions and permission matrices
- Audit log middleware for all state-changing operations
- Secrets scanning via detect-secrets pre-commit hook
- Dependency vulnerability scanning
- Security headers middleware (CORS, CSP, HSTS)
- Input validation and sanitization
- SQL injection prevention (parameterized queries via SQLAlchemy)
- XSS prevention (React default escaping + CSP)

## Pre-commit Hooks
- detect-secrets: prevent secrets in commits
- ruff: Python linting/formatting
- mypy: Python type checking
- eslint: Frontend linting

## DoD Checklist
- [ ] RBAC roles defined (admin, manager, operator, viewer)
- [ ] Audit log captures all mutations
- [ ] detect-secrets hook active
- [ ] Security headers on all responses
- [ ] No hardcoded secrets in codebase
- [ ] Dependencies scanned for known vulnerabilities
