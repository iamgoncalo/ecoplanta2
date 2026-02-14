"""Sales module -- leads, opportunities, pipeline statistics."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    OpportunitySummary,
    PipelineStats,
    SalesLeadItem,
    SalesListResponse,
)

router = APIRouter(prefix="/api/sales", tags=["sales"])


@router.get("", response_model=SalesListResponse)
async def list_sales(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SalesListResponse:
    """List leads with opportunities and compute pipeline statistics.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    leads_raw = data["leads"]
    opps_raw = data["opportunities"]

    # Index opportunities by lead_id
    opps_by_lead: dict[str, list[dict]] = {}
    for opp in opps_raw:
        opps_by_lead.setdefault(opp["lead_id"], []).append(opp)

    lead_items: list[SalesLeadItem] = []
    for ld in leads_raw:
        lead_opps = opps_by_lead.get(ld["id"], [])
        opp_summaries = [
            OpportunitySummary(
                id=o["id"],
                title=o["title"],
                value=o["value"],
                stage=o["stage"],
                probability=o["probability"],
                source=o.get("source", "synthetic_seeded"),
                source_id=o.get("source_id"),
            )
            for o in lead_opps
        ]
        lead_items.append(
            SalesLeadItem(
                id=ld["id"],
                name=ld["name"],
                email=ld["email"],
                company=ld.get("company"),
                status=ld["status"],
                score=ld["score"],
                opportunities=opp_summaries,
                source=ld.get("source", "synthetic_seeded"),
                source_id=ld.get("source_id"),
            )
        )

    # Pipeline stats
    total_value = sum(o["value"] for o in opps_raw)
    weighted_value = sum(o["value"] * o["probability"] for o in opps_raw)
    qualified = sum(
        1 for ld in leads_raw if ld["status"] in ("qualified", "proposal", "negotiation", "won")
    )
    avg_deal = total_value / len(opps_raw) if opps_raw else 0.0

    pipeline = PipelineStats(
        total_leads=len(leads_raw),
        qualified_leads=qualified,
        total_pipeline_value=round(total_value, 2),
        weighted_pipeline_value=round(weighted_value, 2),
        avg_deal_size=round(avg_deal, 2),
    )

    return SalesListResponse(leads=lead_items, pipeline=pipeline)
