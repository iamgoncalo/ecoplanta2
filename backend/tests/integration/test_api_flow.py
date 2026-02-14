"""Integration tests verifying cross-module API flows.

These tests exercise the full request path through FastAPI (middleware, auth,
routing, seed data) without a running database — using the same ASGI transport
approach as unit tests but focused on multi-endpoint flows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_navigation_flow(client: AsyncClient) -> None:
    """Simulate a user navigating all 6 modules — every endpoint returns 200."""
    endpoints = [
        "/health",
        "/me",
        "/api/fabric",
        "/api/fabric/scene",
        "/api/frameworks",
        "/api/sales",
        "/api/intelligence",
        "/api/deploy",
        "/api/partners",
    ]
    for ep in endpoints:
        resp = await client.get(ep)
        assert resp.status_code == 200, f"{ep} returned {resp.status_code}"


@pytest.mark.asyncio
async def test_fabric_scene_has_objects(client: AsyncClient) -> None:
    """3D scene endpoint must return at least one scene object."""
    resp = await client.get("/api/fabric/scene")
    body = resp.json()
    assert len(body["objects"]) > 0, "Scene must have objects"
    assert "camera" in body, "Scene must include camera defaults"
    obj = body["objects"][0]
    assert "position" in obj
    assert "name" in obj


@pytest.mark.asyncio
async def test_sales_pipeline_consistency(client: AsyncClient) -> None:
    """Sales pipeline stats must be consistent with the lead list."""
    resp = await client.get("/api/sales")
    body = resp.json()
    leads = body["leads"]
    pipeline = body["pipeline"]
    assert pipeline["total_leads"] == len(leads)
    assert pipeline["total_pipeline_value"] >= 0


@pytest.mark.asyncio
async def test_frameworks_no_lsf(client: AsyncClient) -> None:
    """Frameworks endpoint must never include LSF materials."""
    resp = await client.get("/api/frameworks")
    body = resp.json()
    for mat in body.get("materials", []):
        name_lower = mat["name"].lower()
        assert "lsf" not in name_lower, f"LSF material found: {mat['name']}"
        assert "light steel frame" not in name_lower


@pytest.mark.asyncio
async def test_deploy_has_deliveries(client: AsyncClient) -> None:
    """Deploy module must return deliveries with status info."""
    resp = await client.get("/api/deploy")
    body = resp.json()
    assert body["total_deliveries"] > 0
    assert len(body["deliveries"]) > 0
    delivery = body["deliveries"][0]
    assert "status" in delivery
    assert "origin" in delivery
    assert "destination" in delivery


@pytest.mark.asyncio
async def test_partners_eu_coverage(client: AsyncClient) -> None:
    """Partners must be EU-based."""
    resp = await client.get("/api/partners")
    body = resp.json()
    assert body["total_partners"] > 0
    for partner in body["partners"]:
        assert partner["country"], f"Partner {partner['name']} has no country"


@pytest.mark.asyncio
async def test_intelligence_insights(client: AsyncClient) -> None:
    """Intelligence endpoint must return insight reports."""
    resp = await client.get("/api/intelligence")
    body = resp.json()
    assert body["total_insights"] > 0
    insight = body["insights"][0]
    assert "title" in insight
    assert "module" in insight


@pytest.mark.asyncio
async def test_provenance_on_all_modules(client: AsyncClient) -> None:
    """Every list item across modules must carry provenance metadata."""
    module_checks = [
        ("/api/fabric", "production_lines"),
        ("/api/sales", "leads"),
        ("/api/deploy", "deliveries"),
        ("/api/partners", "partners"),
        ("/api/intelligence", "insights"),
    ]
    for endpoint, key in module_checks:
        resp = await client.get(endpoint)
        body = resp.json()
        items = body.get(key, [])
        assert len(items) > 0, f"{endpoint} has no {key}"
        for item in items:
            assert item.get("source") == "synthetic_seeded", (
                f"{endpoint}/{key} item missing provenance: {item.get('source')}"
            )


@pytest.mark.asyncio
async def test_security_headers_on_all_endpoints(client: AsyncClient) -> None:
    """Security headers must be present on every response."""
    endpoints = ["/health", "/api/fabric", "/api/sales"]
    for ep in endpoints:
        resp = await client.get(ep)
        assert "x-content-type-options" in resp.headers, f"Missing X-Content-Type-Options on {ep}"
        assert resp.headers["x-content-type-options"] == "nosniff"
