"""Tests for module endpoints -- all work without a running database."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

# ── Fabric ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fabric_list(client: AsyncClient) -> None:
    """GET /api/fabric should return 200 with production line data."""
    resp = await client.get("/api/fabric")
    assert resp.status_code == 200
    body = resp.json()
    assert "production_lines" in body
    assert body["total_lines"] > 0
    assert len(body["production_lines"]) > 0


@pytest.mark.asyncio
async def test_fabric_scene(client: AsyncClient) -> None:
    """GET /api/fabric/scene should return 200 with 3D scene objects."""
    resp = await client.get("/api/fabric/scene")
    assert resp.status_code == 200
    body = resp.json()
    assert "objects" in body
    assert "camera" in body
    assert len(body["objects"]) > 0
    # Check first object has required fields
    obj = body["objects"][0]
    assert "id" in obj
    assert "name" in obj
    assert "type" in obj
    assert "position" in obj


# ── Frameworks ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_frameworks_list(client: AsyncClient) -> None:
    """GET /api/frameworks should return 200 with frameworks, materials, patents."""
    resp = await client.get("/api/frameworks")
    assert resp.status_code == 200
    body = resp.json()
    assert "frameworks" in body
    assert body["total_frameworks"] > 0
    assert body["total_materials"] > 0
    assert body["total_patents"] > 0

    # Each framework should have materials and patents attached
    fw = body["frameworks"][0]
    assert "materials" in fw
    assert "patents" in fw


# ── Sales ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sales_list(client: AsyncClient) -> None:
    """GET /api/sales should return 200 with leads and pipeline stats."""
    resp = await client.get("/api/sales")
    assert resp.status_code == 200
    body = resp.json()
    assert "leads" in body
    assert "pipeline" in body
    assert len(body["leads"]) > 0
    assert body["pipeline"]["total_leads"] > 0
    assert body["pipeline"]["total_pipeline_value"] > 0


# ── Intelligence ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_intelligence_list(client: AsyncClient) -> None:
    """GET /api/intelligence should return 200 with insight reports."""
    resp = await client.get("/api/intelligence")
    assert resp.status_code == 200
    body = resp.json()
    assert "insights" in body
    assert body["total_insights"] > 0
    assert len(body["insights"]) > 0

    insight = body["insights"][0]
    assert "title" in insight
    assert "module" in insight
    assert "report_type" in insight


# ── Deploy ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deploy_list(client: AsyncClient) -> None:
    """GET /api/deploy should return 200 with deliveries."""
    resp = await client.get("/api/deploy")
    assert resp.status_code == 200
    body = resp.json()
    assert "deliveries" in body
    assert "total_deliveries" in body
    # We should have at least one delivery from completed work orders
    assert body["total_deliveries"] >= 0


# ── Partners ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_partners_list(client: AsyncClient) -> None:
    """GET /api/partners should return 200 with partner data."""
    resp = await client.get("/api/partners")
    assert resp.status_code == 200
    body = resp.json()
    assert "partners" in body
    assert body["total_partners"] > 0
    assert body["total_capacity"] > 0
    assert len(body["partners"]) > 0

    partner = body["partners"][0]
    assert "name" in partner
    assert "country" in partner
    assert "capacity_plans" in partner


# ── Auth ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_me_dev_mode(client: AsyncClient) -> None:
    """GET /me should return dev admin user in dev mode."""
    resp = await client.get("/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@ecoplanta.dev"
    assert body["role"] == "admin"


@pytest.mark.asyncio
async def test_auth_token(client: AsyncClient) -> None:
    """POST /auth/token should issue a JWT token."""
    resp = await client.post(
        "/auth/token",
        json={"email": "test@ecoplanta.dev", "name": "Test User", "role": "viewer"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


# ── Security headers ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_security_headers(client: AsyncClient) -> None:
    """All responses should include security headers."""
    resp = await client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"


# ── Source provenance in API responses ────────────────────────────────────────


@pytest.mark.asyncio
async def test_fabric_source_provenance(client: AsyncClient) -> None:
    """All fabric items should carry source='synthetic_seeded'."""
    resp = await client.get("/api/fabric")
    body = resp.json()
    for item in body["production_lines"]:
        assert item["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_sales_source_provenance(client: AsyncClient) -> None:
    """All sales lead items should carry source='synthetic_seeded'."""
    resp = await client.get("/api/sales")
    body = resp.json()
    for lead in body["leads"]:
        assert lead["source"] == "synthetic_seeded"
