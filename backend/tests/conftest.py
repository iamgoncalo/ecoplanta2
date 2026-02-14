"""Shared pytest fixtures for the EcoContainer backend test suite.

All tests work WITHOUT a running database -- they use either the
SeedGenerator directly or mock the database dependency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_seed_data
from app.core.config import settings
from app.seed.generator import SeedGenerator

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# ── Override settings for test environment ────────────────────────────────────


@pytest.fixture(autouse=True)
def _force_dev_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure dev mode is on so that auth is auto-resolved."""
    monkeypatch.setattr(settings, "DEV_MODE", True)


# ── Async HTTP client ────────────────────────────────────────────────────────


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an ``httpx.AsyncClient`` wired to the FastAPI app via ASGI transport."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ── Seed data fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def seed_generator() -> SeedGenerator:
    """Return a SeedGenerator with the default seed."""
    return SeedGenerator(seed=settings.SEED)


@pytest.fixture
def seed_data() -> dict[str, Any]:
    """Return the full seed data dict (cached)."""
    return get_seed_data()
