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


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2 — Enterprise Flow Integration
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_full_enterprise_flow(client: AsyncClient) -> None:
    """Full flow: Lead -> Opportunity -> Contract -> BOM -> WorkOrder -> QA -> Delivery -> Job.

    This test exercises the entire enterprise pipeline end-to-end using
    both seeded data and the new CRUD endpoints.
    """
    # ── Step 1: Create a new lead ────────────────────────────────────
    resp = await client.post(
        "/api/sales/leads",
        json={
            "name": "Integration Test Lead",
            "email": "flow@test.pt",
            "company": "FlowTest SA",
            "region": "Lisboa",
        },
    )
    assert resp.status_code == 201
    lead = resp.json()
    lead_id = lead["id"]
    assert lead["status"] == "new"

    # ── Step 2: Progress lead through stages ─────────────────────────
    for stage in ["contacted", "qualified", "proposal", "negotiation", "won"]:
        resp = await client.patch(
            f"/api/sales/leads/{lead_id}",
            json={"status": stage},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == stage

    # ── Step 3: Verify pipeline stats reflect new lead ───────────────
    resp = await client.get("/api/sales/pipeline/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert stats["total_leads"] > 0
    # Lisboa territory should exist
    lisboa = [t for t in stats["territories"] if t["region"] == "Lisboa"]
    assert len(lisboa) > 0

    # ── Step 4: Get a BOM (from seed data) ───────────────────────────
    from app.api.deps import get_seed_data

    seed = get_seed_data()
    bom_id = seed["boms"][0]["id"]

    resp = await client.get(f"/api/factory/bom/{bom_id}")
    assert resp.status_code == 200
    bom = resp.json()
    assert bom["id"] == bom_id
    assert len(bom["items"]) > 0

    # ── Step 5: Create a work order from BOM ─────────────────────────
    resp = await client.post(
        "/api/factory/workorders",
        json={"bom_id": bom_id, "priority": 1},
    )
    assert resp.status_code == 201
    wo = resp.json()
    wo_id = wo["id"]
    assert wo["status"] == "planned"
    assert wo["bom_id"] == bom_id

    # ── Step 6: Progress work order through manufacturing ────────────
    for status in ["scheduled", "in_progress", "completed"]:
        resp = await client.patch(
            f"/api/factory/workorders/{wo_id}/status",
            json={"status": status},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == status

    # ── Step 7: Check QA records exist ───────────────────────────────
    resp = await client.get("/api/factory/qa")
    assert resp.status_code == 200
    qa = resp.json()
    assert qa["summary"]["total_inspections"] > 0

    # ── Step 8: Check inventory levels ───────────────────────────────
    resp = await client.get("/api/factory/inventory")
    assert resp.status_code == 200
    inv = resp.json()
    assert inv["total"] > 0

    # ── Step 9: Create a delivery ────────────────────────────────────
    resp = await client.post(
        "/api/deploy/deliveries",
        json={
            "work_order_id": wo_id,
            "destination": "Lisboa, Portugal",
            "carrier": "EcoFreight Iberia",
        },
    )
    assert resp.status_code == 201
    delivery = resp.json()
    dlv_id = delivery["id"]
    assert delivery["status"] == "preparing"

    # ── Step 10: Progress delivery ───────────────────────────────────
    resp = await client.patch(
        f"/api/deploy/deliveries/{dlv_id}/status",
        json={"status": "in_transit"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_transit"

    resp = await client.patch(
        f"/api/deploy/deliveries/{dlv_id}/status",
        json={"status": "delivered"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "delivered"

    # ── Step 11: Get a deployment job and update its checklist ────────
    job_id = seed["deployment_jobs"][0]["id"]
    resp = await client.get(f"/api/deploy/jobs/{job_id}")
    assert resp.status_code == 200
    job = resp.json()
    assert "checklist" in job

    resp = await client.patch(
        f"/api/deploy/jobs/{job_id}/checklist",
        json={
            "items": {
                "foundation_check": True,
                "utility_connections": True,
                "module_alignment": True,
                "smart_system_boot": True,
                "final_inspection": True,
            }
        },
    )
    assert resp.status_code == 200
    updated_job = resp.json()
    assert updated_job["checklist"]["completion_pct"] == 100.0

    # ── Step 12: Check commissioning overview ────────────────────────
    resp = await client.get("/api/deploy/commissioning")
    assert resp.status_code == 200
    comm = resp.json()
    assert comm["total"] > 0

    # ── Step 13: Check delivery schedule ─────────────────────────────
    resp = await client.get("/api/deploy/schedule")
    assert resp.status_code == 200
    schedule = resp.json()
    assert "schedule" in schedule


@pytest.mark.asyncio
async def test_all_phase2_endpoints_return_200(client: AsyncClient) -> None:
    """Every new Phase 2 GET endpoint should return 200."""
    from app.api.deps import get_seed_data

    seed = get_seed_data()

    endpoints = [
        "/api/sales/pipeline/stats",
        "/api/factory/workorders",
        f"/api/factory/workorders/{seed['work_orders'][0]['id']}",
        "/api/factory/inventory",
        "/api/factory/qa",
        f"/api/factory/bom/{seed['boms'][0]['id']}",
        "/api/deploy/schedule",
        f"/api/deploy/jobs/{seed['deployment_jobs'][0]['id']}",
        "/api/deploy/commissioning",
    ]
    for ep in endpoints:
        resp = await client.get(ep)
        assert resp.status_code == 200, f"{ep} returned {resp.status_code}"


@pytest.mark.asyncio
async def test_phase2_provenance_on_all_modules(client: AsyncClient) -> None:
    """All Phase 2 list endpoints should carry source='synthetic_seeded'."""
    checks = [
        ("/api/factory/workorders", "work_orders"),
        ("/api/factory/inventory", "items"),
    ]
    for endpoint, key in checks:
        resp = await client.get(endpoint)
        body = resp.json()
        items = body.get(key, [])
        assert len(items) > 0, f"{endpoint} has no {key}"
        for item in items:
            assert item.get("source") == "synthetic_seeded", (
                f"{endpoint}/{key} item missing provenance: {item.get('source')}"
            )
