"""Common FastAPI dependencies shared across all route modules."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.security import get_current_user as _get_current_user
from app.db.session import get_db as _get_db
from app.seed.generator import SeedGenerator

# Re-export the core dependencies so that routes only import from here.

get_db = _get_db
get_current_user = _get_current_user

# ── Seed data cache (singleton) ──────────────────────────────────────────────

_seed_cache: dict[str, Any] | None = None


def get_seed_data() -> dict[str, Any]:
    """Return the deterministic seed data, cached on first call."""
    global _seed_cache
    if _seed_cache is None:
        gen = SeedGenerator(seed=settings.SEED)
        _seed_cache = gen.generate_all()
    return _seed_cache
