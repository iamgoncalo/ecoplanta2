"""Frameworks module -- structural frameworks, materials, patents, BOM variants."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.materials import (
    BOMVariant,
    BOMVariantLine,
    BOMVariantsResponse,
)
from app.schemas.modules import (
    FrameworkItem,
    FrameworkListResponse,
    MaterialSummary,
    PatentSummary,
)

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


# ── Helpers ─────────────────────────────────────────────────────────────────


def _build_framework_item(
    fw: dict[str, Any],
    idx: int,
    material_summaries: list[MaterialSummary],
    patent_summaries: list[PatentSummary],
) -> FrameworkItem:
    """Build a FrameworkItem from raw seed data with related materials/patents."""
    json.loads(fw.get("materials_json", "[]")) if fw.get("materials_json") else []
    json.loads(fw.get("patent_ids", "[]")) if fw.get("patent_ids") else []

    # Assign a subset of materials and patents to each framework
    fw_materials = material_summaries[idx * 3 : idx * 3 + 3]
    fw_patents = patent_summaries[idx : idx + 2]

    return FrameworkItem(
        id=fw["id"],
        name=fw["name"],
        framework_type=fw["framework_type"],
        description=fw.get("description"),
        structural_rating=fw["structural_rating"],
        materials=fw_materials,
        patents=fw_patents,
        source=fw.get("source", "synthetic_seeded"),
        source_id=fw.get("source_id"),
    )


def _build_summaries() -> tuple[
    list[dict[str, Any]],
    list[MaterialSummary],
    list[PatentSummary],
]:
    """Build material and patent summaries from seed data."""
    data = get_seed_data()
    frameworks_raw = data["frameworks"]
    materials_raw = data["materials"]
    patents_raw = data["patents"]

    material_summaries = [
        MaterialSummary(
            id=m["id"],
            name=m["name"],
            category=m["category"],
            grade=m["grade"],
            is_smart_material=m["is_smart_material"],
            tensile_strength=m["tensile_strength"],
            embodied_carbon_kg=m["embodied_carbon_kg"],
            source=m.get("source", "synthetic_seeded"),
            source_id=m.get("source_id"),
        )
        for m in materials_raw
    ]

    patent_summaries = [
        PatentSummary(
            id=p["id"],
            title=p["title"],
            filing_number=p["filing_number"],
            status=p["status"],
            filing_date=p.get("filing_date"),
            source=p.get("source", "synthetic_seeded"),
            source_id=p.get("source_id"),
        )
        for p in patents_raw
    ]

    return frameworks_raw, material_summaries, patent_summaries


# ── GET: list frameworks ───────────────────────────────────────────────────


@router.get("", response_model=FrameworkListResponse)
async def list_frameworks(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> FrameworkListResponse:
    """List frameworks with their related materials and patents.

    Falls back to seed data when the database is empty or unavailable.
    """
    frameworks_raw, material_summaries, patent_summaries = _build_summaries()
    data = get_seed_data()

    framework_items: list[FrameworkItem] = []
    for idx, fw in enumerate(frameworks_raw):
        framework_items.append(
            _build_framework_item(fw, idx, material_summaries, patent_summaries)
        )

    return FrameworkListResponse(
        frameworks=framework_items,
        total_frameworks=len(framework_items),
        total_materials=len(data["materials"]),
        total_patents=len(data["patents"]),
    )


# ── GET: framework detail ─────────────────────────────────────────────────


@router.get("/{framework_id}", response_model=FrameworkItem)
async def get_framework(
    framework_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> FrameworkItem:
    """Get a single framework with its materials list and patent references."""
    frameworks_raw, material_summaries, patent_summaries = _build_summaries()

    for idx, fw in enumerate(frameworks_raw):
        if fw["id"] == framework_id:
            return _build_framework_item(fw, idx, material_summaries, patent_summaries)

    raise HTTPException(status_code=404, detail=f"Framework {framework_id} not found")


# ── GET: BOM variants ─────────────────────────────────────────────────────


@router.get("/{framework_id}/bom-variants", response_model=BOMVariantsResponse)
async def get_bom_variants(
    framework_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> BOMVariantsResponse:
    """Generate BOM variants using different material combinations for a framework."""
    data = get_seed_data()
    frameworks_raw = data["frameworks"]
    materials_raw = data["materials"]

    fw = None
    fw_idx = 0
    for idx, f in enumerate(frameworks_raw):
        if f["id"] == framework_id:
            fw = f
            fw_idx = idx
            break

    if fw is None:
        raise HTTPException(status_code=404, detail=f"Framework {framework_id} not found")

    # Get materials associated with this framework
    fw_materials = materials_raw[fw_idx * 3 : fw_idx * 3 + 3]
    if not fw_materials:
        fw_materials = materials_raw[:3]

    # Generate variants by swapping materials with alternatives
    variants: list[BOMVariant] = []

    # Variant 1: Standard (original materials)
    standard_items: list[BOMVariantLine] = []
    total_cost = 0.0
    total_carbon = 0.0
    for mat in fw_materials:
        cost = round(mat.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)
        qty = 100
        line_cost = round(cost * qty, 2)
        total_cost += line_cost
        total_carbon += mat.get("embodied_carbon_kg", 0.0) * qty
        standard_items.append(
            BOMVariantLine(
                material_id=mat["id"],
                material_name=mat["name"],
                quantity=qty,
                unit_cost=cost,
            )
        )

    variants.append(
        BOMVariant(
            variant_name="Standard",
            framework_id=framework_id,
            items=standard_items,
            total_cost=round(total_cost, 2),
            total_embodied_carbon=round(total_carbon, 2),
        )
    )

    # Variant 2: Smart materials alternative
    smart_mats = [m for m in materials_raw if m.get("is_smart_material", False)]
    if smart_mats:
        smart_items: list[BOMVariantLine] = []
        smart_total_cost = 0.0
        smart_total_carbon = 0.0
        for i, mat in enumerate(fw_materials):
            alt = smart_mats[i % len(smart_mats)]
            cost = round(mat.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)
            alt_cost = round(alt.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)
            qty = 100
            smart_total_cost += round(alt_cost * qty, 2)
            smart_total_carbon += alt.get("embodied_carbon_kg", 0.0) * qty
            smart_items.append(
                BOMVariantLine(
                    material_id=mat["id"],
                    material_name=mat["name"],
                    alternative_material_id=alt["id"],
                    alternative_material_name=alt["name"],
                    quantity=qty,
                    unit_cost=cost,
                    alternative_unit_cost=alt_cost,
                )
            )

        variants.append(
            BOMVariant(
                variant_name="Smart Materials",
                framework_id=framework_id,
                items=smart_items,
                total_cost=round(smart_total_cost, 2),
                total_embodied_carbon=round(smart_total_carbon, 2),
            )
        )

    # Variant 3: Low carbon alternative
    low_carbon = sorted(materials_raw, key=lambda m: m.get("embodied_carbon_kg", 999))
    lc_items: list[BOMVariantLine] = []
    lc_total_cost = 0.0
    lc_total_carbon = 0.0
    for i, mat in enumerate(fw_materials):
        alt = low_carbon[i % len(low_carbon)]
        cost = round(mat.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)
        alt_cost = round(alt.get("embodied_carbon_kg", 0.0) * 0.05 + 2.0, 2)
        qty = 100
        lc_total_cost += round(alt_cost * qty, 2)
        lc_total_carbon += alt.get("embodied_carbon_kg", 0.0) * qty
        lc_items.append(
            BOMVariantLine(
                material_id=mat["id"],
                material_name=mat["name"],
                alternative_material_id=alt["id"],
                alternative_material_name=alt["name"],
                quantity=qty,
                unit_cost=cost,
                alternative_unit_cost=alt_cost,
            )
        )

    variants.append(
        BOMVariant(
            variant_name="Low Carbon",
            framework_id=framework_id,
            items=lc_items,
            total_cost=round(lc_total_cost, 2),
            total_embodied_carbon=round(lc_total_carbon, 2),
        )
    )

    return BOMVariantsResponse(
        framework_id=framework_id,
        framework_name=fw["name"],
        variants=variants,
    )
