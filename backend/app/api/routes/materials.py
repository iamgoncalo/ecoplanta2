"""Materials module -- material search, comparison, smart materials, audit trail.

Explicitly excludes LSF and weak materials from all results.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_seed_data
from app.schemas.materials import (
    MaterialAuditTrail,
    MaterialAuditTrailResponse,
    MaterialComparison,
    MaterialDetail,
    MaterialSearchResult,
    MaterialSelectionRequest,
)

router = APIRouter(prefix="/api/materials", tags=["materials"])

# ── In-memory audit trail store ─────────────────────────────────────────────

_audit_trail: list[dict[str, Any]] = []

# ── LSF / weak material exclusion ───────────────────────────────────────────

_EXCLUDED_TERMS = frozenset(
    [
        "lsf",
        "light steel frame",
        "light gauge",
        "light steel framing",
    ]
)


def _is_excluded(material: dict[str, Any]) -> bool:
    """Check if a material should be excluded (LSF or weak)."""
    name_lower = material.get("name", "").lower()
    cat_lower = material.get("category", "").lower()
    return any(term in name_lower or term in cat_lower for term in _EXCLUDED_TERMS)


def _build_material_detail(
    mat: dict[str, Any], suppliers_by_id: dict[str, dict[str, Any]]
) -> MaterialDetail:
    """Build a MaterialDetail from raw seed data."""
    supplier = suppliers_by_id.get(mat.get("supplier_id", ""))
    supplier_name = supplier["name"] if supplier else None
    lead_time = supplier.get("lead_time_days", 14) if supplier else 14
    # Compute a cost_per_kg from density and embodied carbon as a proxy
    cost_per_kg = round(mat.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)

    return MaterialDetail(
        id=mat["id"],
        name=mat["name"],
        category=mat["category"],
        grade=mat["grade"],
        density=mat.get("density", 0.0),
        tensile_strength=mat.get("tensile_strength", 0.0),
        thermal_conductivity=mat.get("thermal_conductivity", 0.0),
        embodied_carbon_kg=mat.get("embodied_carbon_kg", 0.0),
        supplier_id=mat.get("supplier_id"),
        supplier_name=supplier_name,
        is_smart_material=mat.get("is_smart_material", False),
        compliance_certs=mat.get("compliance_certs", ""),
        lead_time_days=lead_time,
        cost_per_kg=cost_per_kg,
        source=mat.get("source", "synthetic_seeded"),
        source_id=mat.get("source_id"),
    )


def _get_filtered_materials() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Return materials (excluding LSF/weak) and suppliers index."""
    data = get_seed_data()
    suppliers_by_id = {s["id"]: s for s in data["suppliers"]}
    materials = [m for m in data["materials"] if not _is_excluded(m)]
    return materials, suppliers_by_id


# ── GET: list materials with filters ────────────────────────────────────────


@router.get("", response_model=MaterialSearchResult)
async def list_materials(
    category: str | None = None,
    grade: str | None = None,
    smart_only: bool = False,
    min_strength: float | None = None,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialSearchResult:
    """List all materials with optional filters. Excludes LSF/weak materials."""
    materials, suppliers_by_id = _get_filtered_materials()

    filters_applied: dict[str, str | bool | float] = {}

    if category:
        materials = [m for m in materials if m["category"] == category]
        filters_applied["category"] = category

    if grade:
        materials = [m for m in materials if m["grade"] == grade]
        filters_applied["grade"] = grade

    if smart_only:
        materials = [m for m in materials if m.get("is_smart_material", False)]
        filters_applied["smart_only"] = True

    if min_strength is not None:
        materials = [m for m in materials if m.get("tensile_strength", 0) >= min_strength]
        filters_applied["min_strength"] = min_strength

    details = [_build_material_detail(m, suppliers_by_id) for m in materials]

    return MaterialSearchResult(
        materials=details,
        total=len(details),
        filters_applied=filters_applied,
    )


# ── GET: smart materials only ──────────────────────────────────────────────


@router.get("/smart", response_model=MaterialSearchResult)
async def list_smart_materials(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialSearchResult:
    """List only smart materials. Excludes LSF/weak materials."""
    materials, suppliers_by_id = _get_filtered_materials()
    smart = [m for m in materials if m.get("is_smart_material", False)]
    details = [_build_material_detail(m, suppliers_by_id) for m in smart]

    return MaterialSearchResult(
        materials=details,
        total=len(details),
        filters_applied={"smart_only": True},
    )


# ── GET: compare materials ─────────────────────────────────────────────────


@router.get("/compare", response_model=MaterialComparison)
async def compare_materials(
    ids: str = Query(..., description="Comma-separated material IDs to compare"),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialComparison:
    """Compare 2+ materials side by side."""
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if len(id_list) < 2:
        raise HTTPException(
            status_code=422,
            detail="At least 2 material IDs required for comparison",
        )

    materials, suppliers_by_id = _get_filtered_materials()
    materials_by_id = {m["id"]: m for m in materials}

    selected: list[MaterialDetail] = []
    for mid in id_list:
        mat = materials_by_id.get(mid)
        if mat is None:
            raise HTTPException(status_code=404, detail=f"Material {mid} not found")
        selected.append(_build_material_detail(mat, suppliers_by_id))

    comparison_fields = [
        "density",
        "tensile_strength",
        "thermal_conductivity",
        "embodied_carbon_kg",
        "cost_per_kg",
        "lead_time_days",
    ]

    # Determine best material for each field
    best_by: dict[str, str] = {}
    # Higher is better: tensile_strength
    higher_better = {"tensile_strength"}

    for field in comparison_fields:
        vals = [(getattr(m, field, 0.0), m.id) for m in selected]
        if field in higher_better:
            best_id = max(vals, key=lambda x: x[0])[1]
        else:
            best_id = min(vals, key=lambda x: x[0])[1]
        best_by[field] = best_id

    return MaterialComparison(
        materials=selected,
        comparison_fields=comparison_fields,
        best_by=best_by,
    )


# ── GET: audit trail ───────────────────────────────────────────────────────
# NOTE: must be registered BEFORE /{material_id} to avoid path param capture


@router.get("/audit-trail", response_model=MaterialAuditTrailResponse)
async def get_audit_trail(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialAuditTrailResponse:
    """Get the material selection audit trail."""
    entries = [MaterialAuditTrail(**e) for e in _audit_trail]
    return MaterialAuditTrailResponse(entries=entries, total=len(entries))


# ── POST: record material selection ────────────────────────────────────────


@router.post("/select", response_model=MaterialAuditTrail, status_code=201)
async def select_material(
    body: MaterialSelectionRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialAuditTrail:
    """Record a material selection decision (audit trail).

    Rejects LSF and weak materials.
    """
    materials, _suppliers = _get_filtered_materials()
    materials_by_id = {m["id"]: m for m in materials}

    mat = materials_by_id.get(body.material_id)
    if mat is None:
        # Check if it exists but is excluded
        data = get_seed_data()
        all_mats = {m["id"]: m for m in data["materials"]}
        if body.material_id in all_mats:
            raise HTTPException(
                status_code=422,
                detail="Material rejected: LSF and weak materials are not permitted",
            )
        raise HTTPException(status_code=404, detail=f"Material {body.material_id} not found")

    entry = {
        "id": str(uuid.uuid4()),
        "material_id": mat["id"],
        "material_name": mat["name"],
        "project_id": body.project_id,
        "reason": body.reason,
        "selected_by": body.selected_by or current_user.get("name", ""),
        "decision_date": datetime.now(UTC).isoformat(),
    }
    _audit_trail.append(entry)

    return MaterialAuditTrail(**entry)


# ── GET: material by ID ───────────────────────────────────────────────────
# NOTE: must be last to avoid capturing /smart, /compare, /audit-trail


@router.get("/{material_id}", response_model=MaterialDetail)
async def get_material(
    material_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> MaterialDetail:
    """Get a single material detail with supplier info and compliance."""
    materials, suppliers_by_id = _get_filtered_materials()

    for mat in materials:
        if mat["id"] == material_id:
            return _build_material_detail(mat, suppliers_by_id)

    raise HTTPException(status_code=404, detail=f"Material {material_id} not found")
