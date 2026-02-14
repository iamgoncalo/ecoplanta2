"""Tests for the /health endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient) -> None:
    """GET /health should return 200 with status 'ok'."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "db_connected" in body
    assert "redis_connected" in body


@pytest.mark.asyncio
async def test_health_version_matches_config(client: AsyncClient) -> None:
    """The version in /health should match the configured APP_VERSION."""
    from app.core.config import settings

    resp = await client.get("/health")
    body = resp.json()
    assert body["version"] == settings.APP_VERSION
