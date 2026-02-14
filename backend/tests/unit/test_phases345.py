"""Unit tests for Phase 3 (Materials + Patents), Phase 4 (Partners), Phase 5 (Intelligence).

Tests each new endpoint returns expected status codes and data shapes,
all without a running database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.api.deps import get_seed_data

if TYPE_CHECKING:
    from httpx import AsyncClient


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Materials + Patents
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_materials_list(client: AsyncClient) -> None:
    """GET /api/materials should return 200 with materials."""
    resp = await client.get("/api/materials")
    assert resp.status_code == 200
    body = resp.json()
    assert "materials" in body
    assert body["total"] > 0
    assert len(body["materials"]) > 0
    mat = body["materials"][0]
    assert "name" in mat
    assert "category" in mat
    assert "tensile_strength" in mat
    assert "supplier_name" in mat
    assert "compliance_certs" in mat
    assert "cost_per_kg" in mat


@pytest.mark.asyncio
async def test_materials_filter_by_category(client: AsyncClient) -> None:
    """GET /api/materials?category=structural_steel should filter results."""
    resp = await client.get("/api/materials?category=structural_steel")
    assert resp.status_code == 200
    body = resp.json()
    for mat in body["materials"]:
        assert mat["category"] == "structural_steel"
    assert body["filters_applied"]["category"] == "structural_steel"


@pytest.mark.asyncio
async def test_materials_filter_by_min_strength(client: AsyncClient) -> None:
    """GET /api/materials?min_strength=200 should only return strong materials."""
    resp = await client.get("/api/materials?min_strength=200")
    assert resp.status_code == 200
    body = resp.json()
    for mat in body["materials"]:
        assert mat["tensile_strength"] >= 200


@pytest.mark.asyncio
async def test_smart_materials_endpoint(client: AsyncClient) -> None:
    """GET /api/materials/smart should return only smart materials."""
    resp = await client.get("/api/materials/smart")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    for mat in body["materials"]:
        assert mat["is_smart_material"] is True
    assert body["filters_applied"]["smart_only"] is True


@pytest.mark.asyncio
async def test_material_detail(client: AsyncClient) -> None:
    """GET /api/materials/{id} should return a single material."""
    data = get_seed_data()
    mat_id = data["materials"][0]["id"]
    resp = await client.get(f"/api/materials/{mat_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == mat_id
    assert "supplier_name" in body
    assert "compliance_certs" in body


@pytest.mark.asyncio
async def test_material_not_found(client: AsyncClient) -> None:
    """GET /api/materials/{bad_id} should return 404."""
    resp = await client.get("/api/materials/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_material_comparison(client: AsyncClient) -> None:
    """GET /api/materials/compare should compare 2+ materials."""
    data = get_seed_data()
    id1 = data["materials"][0]["id"]
    id2 = data["materials"][1]["id"]
    resp = await client.get(f"/api/materials/compare?ids={id1},{id2}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["materials"]) == 2
    assert len(body["comparison_fields"]) > 0
    assert len(body["best_by"]) > 0


@pytest.mark.asyncio
async def test_material_comparison_insufficient_ids(client: AsyncClient) -> None:
    """GET /api/materials/compare with 1 ID should return 422."""
    data = get_seed_data()
    id1 = data["materials"][0]["id"]
    resp = await client.get(f"/api/materials/compare?ids={id1}")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_material_audit_trail(client: AsyncClient) -> None:
    """Material selection and audit trail flow."""
    data = get_seed_data()
    mat_id = data["materials"][0]["id"]

    # Record a selection
    resp = await client.post(
        "/api/materials/select",
        json={
            "material_id": mat_id,
            "project_id": "test-project-001",
            "reason": "Best strength-to-weight ratio",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["material_id"] == mat_id
    assert body["reason"] == "Best strength-to-weight ratio"

    # Check audit trail
    resp = await client.get("/api/materials/audit-trail")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    assert any(e["material_id"] == mat_id for e in body["entries"])


@pytest.mark.asyncio
async def test_lsf_exclusion_in_materials(client: AsyncClient) -> None:
    """Material list should NOT contain LSF or weak materials."""
    resp = await client.get("/api/materials")
    body = resp.json()
    for mat in body["materials"]:
        name_lower = mat["name"].lower()
        assert "lsf" not in name_lower, f"LSF found: {mat['name']}"
        assert "light steel frame" not in name_lower, f"LSF found: {mat['name']}"
        assert "light gauge" not in name_lower, f"Weak material found: {mat['name']}"


@pytest.mark.asyncio
async def test_patents_list(client: AsyncClient) -> None:
    """GET /api/patents should return 200 with patents."""
    resp = await client.get("/api/patents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    assert len(body["patents"]) > 0
    patent = body["patents"][0]
    assert "title" in patent
    assert "filing_number" in patent
    assert "claims" in patent
    assert "inventors" in patent


@pytest.mark.asyncio
async def test_patents_filter_by_status(client: AsyncClient) -> None:
    """GET /api/patents?status=granted should filter by status."""
    resp = await client.get("/api/patents?status=granted")
    assert resp.status_code == 200
    body = resp.json()
    for p in body["patents"]:
        assert p["status"] == "granted"


@pytest.mark.asyncio
async def test_patent_detail(client: AsyncClient) -> None:
    """GET /api/patents/{id} should return patent with claims and experiments."""
    data = get_seed_data()
    patent_id = data["patents"][0]["id"]
    resp = await client.get(f"/api/patents/{patent_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == patent_id
    assert "claims" in body
    assert "experiment_results" in body
    assert "novelty_notes" in body


@pytest.mark.asyncio
async def test_patent_add_experiment(client: AsyncClient) -> None:
    """POST /api/patents/{id}/experiments should add experiment result."""
    data = get_seed_data()
    patent_id = data["patents"][0]["id"]
    resp = await client.post(
        f"/api/patents/{patent_id}/experiments",
        json={
            "description": "Thermal cycling test at -20C to +60C",
            "result": "Passed 500 cycles with no degradation",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == patent_id
    assert len(body["additional_experiments"]) > 0


@pytest.mark.asyncio
async def test_framework_detail(client: AsyncClient) -> None:
    """GET /api/frameworks/{id} should return framework with materials and patents."""
    data = get_seed_data()
    fw_id = data["frameworks"][0]["id"]
    resp = await client.get(f"/api/frameworks/{fw_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == fw_id
    assert "materials" in body
    assert "patents" in body


@pytest.mark.asyncio
async def test_framework_bom_variants(client: AsyncClient) -> None:
    """GET /api/frameworks/{id}/bom-variants should return BOM variants."""
    data = get_seed_data()
    fw_id = data["frameworks"][0]["id"]
    resp = await client.get(f"/api/frameworks/{fw_id}/bom-variants")
    assert resp.status_code == 200
    body = resp.json()
    assert body["framework_id"] == fw_id
    assert len(body["variants"]) >= 2  # At least Standard + one alternative
    for variant in body["variants"]:
        assert "variant_name" in variant
        assert "total_cost" in variant
        assert len(variant["items"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: Partners Network (EU)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_partner_detail(client: AsyncClient) -> None:
    """GET /api/partners/{id} should return partner with capacity and compliance."""
    data = get_seed_data()
    partner_id = data["partners"][0]["id"]
    resp = await client.get(f"/api/partners/{partner_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == partner_id
    assert "capacity_plans" in body
    assert "compliance_docs" in body
    assert len(body["compliance_docs"]) > 0


@pytest.mark.asyncio
async def test_partner_not_found(client: AsyncClient) -> None:
    """GET /api/partners/{bad_id} should return 404."""
    resp = await client.get("/api/partners/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_partner_allocation(client: AsyncClient) -> None:
    """POST /api/partners/allocate should allocate order to partners."""
    resp = await client.post(
        "/api/partners/allocate",
        json={"order_units": 10},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "allocations" in body
    assert body["total_requested"] == 10
    assert body["total_allocated"] > 0
    for alloc in body["allocations"]:
        assert "partner_name" in alloc
        assert "allocated_units" in alloc
        assert alloc["allocated_units"] > 0


@pytest.mark.asyncio
async def test_partner_allocation_with_country(client: AsyncClient) -> None:
    """POST /api/partners/allocate with country preference."""
    resp = await client.post(
        "/api/partners/allocate",
        json={"order_units": 5, "preferred_country": "Germany"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_allocated"] > 0


@pytest.mark.asyncio
async def test_partner_optimization(client: AsyncClient) -> None:
    """GET /api/partners/optimize should return optimization result."""
    resp = await client.get("/api/partners/optimize")
    assert resp.status_code == 200
    body = resp.json()
    assert "optimized_allocations" in body
    assert body["total_units"] > 0
    assert body["optimization_score"] > 0
    assert body["avg_lead_time_days"] > 0


@pytest.mark.asyncio
async def test_partner_optimization_reproducibility(client: AsyncClient) -> None:
    """GET /api/partners/optimize should return same results with same seed."""
    resp1 = await client.get("/api/partners/optimize")
    resp2 = await client.get("/api/partners/optimize")
    body1 = resp1.json()
    body2 = resp2.json()
    assert body1["total_units"] == body2["total_units"]
    assert body1["optimization_score"] == body2["optimization_score"]


@pytest.mark.asyncio
async def test_partner_quotes(client: AsyncClient) -> None:
    """GET /api/partners/{id}/quotes should return quotes."""
    data = get_seed_data()
    partner_id = data["partners"][0]["id"]
    resp = await client.get(f"/api/partners/{partner_id}/quotes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["partner_id"] == partner_id
    assert "quotes" in body


@pytest.mark.asyncio
async def test_partner_compliance(client: AsyncClient) -> None:
    """GET /api/partners/compliance should return EU compliance overview."""
    resp = await client.get("/api/partners/compliance")
    assert resp.status_code == 200
    body = resp.json()
    assert "partners" in body
    assert body["total_partners"] > 0
    assert "compliance_rate" in body
    for p in body["partners"]:
        assert "docs" in p
        assert len(p["docs"]) > 0


@pytest.mark.asyncio
async def test_eu_partner_countries(client: AsyncClient) -> None:
    """Partners should include EU countries."""
    resp = await client.get("/api/partners")
    body = resp.json()
    countries = {p["country"] for p in body["partners"]}
    # At least some EU countries from the spec
    eu_countries = {
        "Portugal",
        "Spain",
        "Germany",
        "Netherlands",
        "France",
        "Italy",
        "Poland",
        "Austria",
    }
    assert len(countries & eu_countries) >= 4, f"Missing EU countries. Found: {countries}"


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: Intelligence Layer
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_model_listing(client: AsyncClient) -> None:
    """GET /api/intelligence/models should return available ML models."""
    resp = await client.get("/api/intelligence/models")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    assert len(body["models"]) > 0
    model = body["models"][0]
    assert "model_id" in model
    assert "model_name" in model
    assert "metrics" in model
    assert "status" in model


@pytest.mark.asyncio
async def test_model_detail(client: AsyncClient) -> None:
    """GET /api/intelligence/models/{id} should return model details."""
    resp = await client.get("/api/intelligence/models/lead-time-forecast-v1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["model_id"] == "lead-time-forecast-v1"
    assert "metrics" in body
    assert body["status"] == "ready"


@pytest.mark.asyncio
async def test_model_not_found(client: AsyncClient) -> None:
    """GET /api/intelligence/models/{bad_id} should return 404."""
    resp = await client.get("/api/intelligence/models/nonexistent-model")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_forecast_endpoint(client: AsyncClient) -> None:
    """POST /api/intelligence/forecast should return predictions."""
    resp = await client.post(
        "/api/intelligence/forecast",
        json={"horizon_periods": 6, "confidence_level": 0.95},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["model_id"] == "lead-time-forecast-v1"
    assert body["metric_name"] == "lead_time_days"
    assert len(body["forecast"]) == 6
    assert body["historical_mean"] > 0
    assert body["historical_std"] > 0
    for point in body["forecast"]:
        assert "period" in point
        assert "value" in point
        assert "lower_bound" in point
        assert "upper_bound" in point
        assert point["lower_bound"] <= point["value"] <= point["upper_bound"]


@pytest.mark.asyncio
async def test_anomaly_detection(client: AsyncClient) -> None:
    """POST /api/intelligence/anomaly-detect should return anomaly results."""
    resp = await client.post(
        "/api/intelligence/anomaly-detect",
        json={"threshold": 2.0},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["model_id"] == "qa-anomaly-detector-v1"
    assert body["total_records"] > 0
    assert "mean" in body
    assert "std" in body
    assert "points" in body
    for point in body["points"]:
        assert "record_id" in point
        assert "z_score" in point
        assert "is_anomaly" in point


@pytest.mark.asyncio
async def test_feature_store(client: AsyncClient) -> None:
    """GET /api/intelligence/feature-store should return features."""
    resp = await client.get("/api/intelligence/feature-store")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    feature = body["features"][0]
    assert "name" in feature
    assert "dtype" in feature
    assert "description" in feature


@pytest.mark.asyncio
async def test_training_job_submission(client: AsyncClient) -> None:
    """POST /api/intelligence/train should submit and return a training job."""
    resp = await client.post(
        "/api/intelligence/train",
        json={
            "model_name": "test-model",
            "features": ["scheduled_duration_days", "priority"],
            "target": "lead_time_days",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "job_id" in body
    assert body["model_name"] == "test-model"
    assert body["status"] == "completed"

    # Verify we can retrieve the job
    job_id = body["job_id"]
    resp2 = await client.get(f"/api/intelligence/train/{job_id}")
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["job_id"] == job_id


@pytest.mark.asyncio
async def test_training_job_not_found(client: AsyncClient) -> None:
    """GET /api/intelligence/train/{bad_id} should return 404."""
    resp = await client.get("/api/intelligence/train/nonexistent-job")
    assert resp.status_code == 404
