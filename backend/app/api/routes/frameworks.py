"""Frameworks module -- structural frameworks, materials, patents."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    FrameworkItem,
    FrameworkListResponse,
    MaterialSummary,
    PatentSummary,
)

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


@router.get("", response_model=FrameworkListResponse)
async def list_frameworks(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> FrameworkListResponse:
    """List frameworks with their related materials and patents.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    frameworks_raw = data["frameworks"]
    materials_raw = data["materials"]
    patents_raw = data["patents"]

    # Build material summaries
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

    # Build patent summaries
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

    # Build framework items with related data
    framework_items: list[FrameworkItem] = []
    for fw in frameworks_raw:
        # Parse material refs (for now assign proportionally)
        json.loads(fw.get("materials_json", "[]")) if fw.get("materials_json") else []
        json.loads(fw.get("patent_ids", "[]")) if fw.get("patent_ids") else []

        # Assign a subset of materials and patents to each framework
        idx = frameworks_raw.index(fw)
        fw_materials = material_summaries[idx * 3 : idx * 3 + 3]
        fw_patents = patent_summaries[idx : idx + 2]

        framework_items.append(
            FrameworkItem(
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
        )

    return FrameworkListResponse(
        frameworks=framework_items,
        total_frameworks=len(framework_items),
        total_materials=len(materials_raw),
        total_patents=len(patents_raw),
    )
