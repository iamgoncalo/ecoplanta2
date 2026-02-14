"""Unit tests for Phase 2 enterprise endpoints.

Tests each new endpoint returns 200, work order creation, lead stage updates,
and delivery scheduling -- all without a running database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.api.deps import get_seed_data

if TYPE_CHECKING:
    from httpx import AsyncClient


# ═══════════════════════════════════════════════════════════════════════════════
# Sales Pipeline Enhancement
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_sales_pipeline_stats(client: AsyncClient) -> None:
    """GET /api/sales/pipeline/stats should return 200 with stage analytics."""
    resp = await client.get("/api/sales/pipeline/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "stages" in body
    assert "territories" in body
    assert "conversions" in body
    assert body["total_leads"] > 0
    assert body["total_pipeline_value"] >= 0
    # Check stages include the expected pipeline stages
    stage_names = [s["name"] for s in body["stages"]]
    assert "discovery" in stage_names
    assert "proposal" in stage_names
    assert "negotiation" in stage_names
    assert "won" in stage_names
    assert "lost" in stage_names


@pytest.mark.asyncio
async def test_sales_pipeline_territories(client: AsyncClient) -> None:
    """Pipeline stats should include Portuguese territory breakdown."""
    resp = await client.get("/api/sales/pipeline/stats")
    body = resp.json()
    territories = body["territories"]
    assert len(territories) > 0
    region_names = [t["region"] for t in territories]
    # At least some Portuguese regions should be present
    assert any(
        r in region_names for r in ["Lisboa", "Porto", "Algarve", "Centro", "Norte", "Alentejo"]
    )


@pytest.mark.asyncio
async def test_sales_pipeline_conversions(client: AsyncClient) -> None:
    """Pipeline stats should include stage-to-stage conversion metrics."""
    resp = await client.get("/api/sales/pipeline/stats")
    body = resp.json()
    conversions = body["conversions"]
    assert len(conversions) > 0
    for conv in conversions:
        assert "stage_from" in conv
        assert "stage_to" in conv
        assert "rate" in conv
        assert "avg_days" in conv


@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient) -> None:
    """POST /api/sales/leads should create a new lead and return 201."""
    resp = await client.post(
        "/api/sales/leads",
        json={
            "name": "Test Lead",
            "email": "test@example.pt",
            "company": "Test Corp",
            "region": "Porto",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Test Lead"
    assert body["email"] == "test@example.pt"
    assert body["status"] == "new"
    assert body["region"] == "Porto"
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_update_lead_stage(client: AsyncClient) -> None:
    """PATCH /api/sales/leads/{id} should update a lead's status."""
    data = get_seed_data()
    lead_id = data["leads"][0]["id"]
    resp = await client.patch(
        f"/api/sales/leads/{lead_id}",
        json={"status": "qualified"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "qualified"
    assert body["id"] == lead_id


@pytest.mark.asyncio
async def test_update_lead_stage_invalid(client: AsyncClient) -> None:
    """PATCH with invalid status should return 422."""
    data = get_seed_data()
    lead_id = data["leads"][0]["id"]
    resp = await client.patch(
        f"/api/sales/leads/{lead_id}",
        json={"status": "invalid_status"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_lead_not_found(client: AsyncClient) -> None:
    """PATCH with non-existent lead_id should return 404."""
    resp = await client.patch(
        "/api/sales/leads/nonexistent-id",
        json={"status": "won"},
    )
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Factory Execution
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_factory_workorders_list(client: AsyncClient) -> None:
    """GET /api/factory/workorders should return 200 with work orders."""
    resp = await client.get("/api/factory/workorders")
    assert resp.status_code == 200
    body = resp.json()
    assert "work_orders" in body
    assert body["total"] > 0
    assert "by_status" in body
    # Check work orders have BOM details
    wo = body["work_orders"][0]
    assert "bom" in wo
    assert "qa_records" in wo
    assert "status_history" in wo


@pytest.mark.asyncio
async def test_factory_workorder_detail(client: AsyncClient) -> None:
    """GET /api/factory/workorders/{id} should return 200 with full detail."""
    data = get_seed_data()
    wo_id = data["work_orders"][0]["id"]
    resp = await client.get(f"/api/factory/workorders/{wo_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == wo_id
    assert "bom" in body
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_factory_workorder_not_found(client: AsyncClient) -> None:
    """GET /api/factory/workorders/{bad_id} should return 404."""
    resp = await client.get("/api/factory/workorders/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_factory_create_workorder(client: AsyncClient) -> None:
    """POST /api/factory/workorders should create a work order and return 201."""
    data = get_seed_data()
    bom_id = data["boms"][0]["id"]
    resp = await client.post(
        "/api/factory/workorders",
        json={"bom_id": bom_id, "priority": 2},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["bom_id"] == bom_id
    assert body["status"] == "planned"
    assert body["priority"] == 2
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_factory_create_workorder_bad_bom(client: AsyncClient) -> None:
    """POST with non-existent BOM should return 404."""
    resp = await client.post(
        "/api/factory/workorders",
        json={"bom_id": "nonexistent-bom-id"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_factory_update_workorder_status(client: AsyncClient) -> None:
    """PATCH /api/factory/workorders/{id}/status should update status."""
    data = get_seed_data()
    wo_id = data["work_orders"][0]["id"]
    resp = await client.patch(
        f"/api/factory/workorders/{wo_id}/status",
        json={"status": "in_progress"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_progress"


@pytest.mark.asyncio
async def test_factory_inventory(client: AsyncClient) -> None:
    """GET /api/factory/inventory should return 200 with stock data."""
    resp = await client.get("/api/factory/inventory")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert body["total"] > 0
    assert "alerts" in body
    # Check items have material names
    item = body["items"][0]
    assert "material_name" in item
    assert "reorder_needed" in item
    assert item["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_factory_qa(client: AsyncClient) -> None:
    """GET /api/factory/qa should return 200 with QA records and summary."""
    resp = await client.get("/api/factory/qa")
    assert resp.status_code == 200
    body = resp.json()
    assert "records" in body
    assert "summary" in body
    summary = body["summary"]
    assert "total_inspections" in summary
    assert "pass_rate" in summary
    assert summary["total_inspections"] > 0


@pytest.mark.asyncio
async def test_factory_bom_detail(client: AsyncClient) -> None:
    """GET /api/factory/bom/{id} should return 200 with BOM details."""
    data = get_seed_data()
    bom_id = data["boms"][0]["id"]
    resp = await client.get(f"/api/factory/bom/{bom_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == bom_id
    assert "items" in body
    assert len(body["items"]) > 0
    assert body["total_cost"] > 0
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_factory_bom_not_found(client: AsyncClient) -> None:
    """GET /api/factory/bom/{bad_id} should return 404."""
    resp = await client.get("/api/factory/bom/nonexistent-bom-id")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Deploy Enhancement
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_deploy_schedule(client: AsyncClient) -> None:
    """GET /api/deploy/schedule should return 200 with calendar data."""
    resp = await client.get("/api/deploy/schedule")
    assert resp.status_code == 200
    body = resp.json()
    assert "schedule" in body
    assert body["total_days"] >= 0
    assert "total_deliveries" in body
    assert "total_installations" in body


@pytest.mark.asyncio
async def test_deploy_create_delivery(client: AsyncClient) -> None:
    """POST /api/deploy/deliveries should create a delivery and return 201."""
    data = get_seed_data()
    wo_id = data["work_orders"][0]["id"]
    resp = await client.post(
        "/api/deploy/deliveries",
        json={
            "work_order_id": wo_id,
            "destination": "Lisboa, Portugal",
            "carrier": "EcoFreight Iberia",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["destination"] == "Lisboa, Portugal"
    assert body["carrier"] == "EcoFreight Iberia"
    assert body["status"] == "preparing"
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_deploy_update_delivery_status(client: AsyncClient) -> None:
    """PATCH /api/deploy/deliveries/{id}/status should update status."""
    data = get_seed_data()
    dlv_id = data["deliveries"][0]["id"]
    resp = await client.patch(
        f"/api/deploy/deliveries/{dlv_id}/status",
        json={"status": "in_transit"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "in_transit"


@pytest.mark.asyncio
async def test_deploy_delivery_not_found(client: AsyncClient) -> None:
    """PATCH with non-existent delivery should return 404."""
    resp = await client.patch(
        "/api/deploy/deliveries/nonexistent-id/status",
        json={"status": "in_transit"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_deploy_job_detail(client: AsyncClient) -> None:
    """GET /api/deploy/jobs/{id} should return 200 with checklist."""
    data = get_seed_data()
    job_id = data["deployment_jobs"][0]["id"]
    resp = await client.get(f"/api/deploy/jobs/{job_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == job_id
    assert "checklist" in body
    checklist = body["checklist"]
    assert "items" in checklist
    assert checklist["total_count"] == 5  # 5 checklist items
    assert body["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_deploy_update_checklist(client: AsyncClient) -> None:
    """PATCH /api/deploy/jobs/{id}/checklist should update checklist items."""
    data = get_seed_data()
    job_id = data["deployment_jobs"][0]["id"]
    resp = await client.patch(
        f"/api/deploy/jobs/{job_id}/checklist",
        json={"items": {"foundation_check": True, "final_inspection": True}},
    )
    assert resp.status_code == 200
    body = resp.json()
    checklist = body["checklist"]
    # Verify the items were updated
    items_by_key = {i["key"]: i for i in checklist["items"]}
    assert items_by_key["foundation_check"]["completed"] is True
    assert items_by_key["final_inspection"]["completed"] is True


@pytest.mark.asyncio
async def test_deploy_commissioning(client: AsyncClient) -> None:
    """GET /api/deploy/commissioning should return 200 with overview."""
    resp = await client.get("/api/deploy/commissioning")
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "pending" in body
    assert "in_progress" in body
    assert "completed" in body
    assert "issues" in body
    assert body["total"] > 0


@pytest.mark.asyncio
async def test_deploy_job_not_found(client: AsyncClient) -> None:
    """GET /api/deploy/jobs/{bad_id} should return 404."""
    resp = await client.get("/api/deploy/jobs/nonexistent-id")
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Provenance checks on new endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_factory_provenance(client: AsyncClient) -> None:
    """Factory work orders should carry source='synthetic_seeded'."""
    resp = await client.get("/api/factory/workorders")
    body = resp.json()
    for wo in body["work_orders"]:
        assert wo["source"] == "synthetic_seeded"


@pytest.mark.asyncio
async def test_factory_inventory_provenance(client: AsyncClient) -> None:
    """Factory inventory items should carry source='synthetic_seeded'."""
    resp = await client.get("/api/factory/inventory")
    body = resp.json()
    for item in body["items"]:
        assert item["source"] == "synthetic_seeded"
