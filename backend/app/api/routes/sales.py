"""Sales module -- leads, opportunities, pipeline statistics, territory, conversions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    OpportunitySummary,
    PipelineStats,
    SalesLeadItem,
    SalesListResponse,
)
from app.schemas.sales import (
    ConversionMetrics,
    EnhancedSalesResponse,
    LeadCreate,
    LeadResponse,
    LeadUpdate,
    PipelineStage,
    TerritoryView,
)

router = APIRouter(prefix="/api/sales", tags=["sales"])

# ── In-memory store for dynamic lead mutations ────────────────────────────────

_leads_store: list[dict[str, Any]] | None = None


def _get_leads_store() -> list[dict[str, Any]]:
    """Return the mutable in-memory leads list, seeding from generator on first call."""
    global _leads_store
    if _leads_store is None:
        data = get_seed_data()
        # Deep-copy to avoid mutating the seed cache
        _leads_store = [dict(ld) for ld in data["leads"]]
    return _leads_store


# ── Existing endpoint (unchanged contract) ────────────────────────────────────


@router.get("", response_model=SalesListResponse)
async def list_sales(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SalesListResponse:
    """List leads with opportunities and compute pipeline statistics.

    Falls back to seed data when the database is empty or unavailable.
    """
    leads_raw = _get_leads_store()
    data = get_seed_data()
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


# ── POST: create a new lead ───────────────────────────────────────────────────


@router.post("/leads", response_model=LeadResponse, status_code=201)
async def create_lead(
    body: LeadCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> LeadResponse:
    """Create a new sales lead (in-memory)."""
    now = datetime.now(UTC).isoformat()
    lead = {
        "id": str(uuid.uuid4()),
        "name": body.name,
        "email": body.email,
        "phone": body.phone,
        "company": body.company,
        "status": "new",
        "score": 0,
        "assigned_to": None,
        "region": body.region,
        "pipeline_value": 0.0,
        "notes": body.notes,
        "source": "synthetic_seeded",
        "source_id": "api-created",
        "created_at": now,
        "updated_at": now,
    }
    _get_leads_store().append(lead)
    return LeadResponse.model_validate(lead)


# ── PATCH: update lead stage ──────────────────────────────────────────────────


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead_stage(
    lead_id: str,
    body: LeadUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> LeadResponse:
    """Update a lead's status (stage)."""
    valid_statuses = {"new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"}
    if body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status: {body.status}")

    leads = _get_leads_store()
    for ld in leads:
        if ld["id"] == lead_id:
            ld["status"] = body.status
            ld["updated_at"] = datetime.now(UTC).isoformat()
            return LeadResponse(**ld)

    raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")


# ── GET: detailed pipeline analytics ──────────────────────────────────────────


@router.get("/pipeline/stats", response_model=EnhancedSalesResponse)
async def pipeline_stats(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> EnhancedSalesResponse:
    """Detailed pipeline analytics with stages, territories, and conversion metrics."""
    leads_raw = _get_leads_store()
    data = get_seed_data()
    opps_raw = data["opportunities"]

    # ── Pipeline stages ──────────────────────────────────────────────
    stage_names = ["discovery", "proposal", "negotiation", "won", "lost"]
    # Map opportunity stages to our pipeline stage names
    stage_mapping = {
        "discovery": "discovery",
        "proposal": "proposal",
        "negotiation": "negotiation",
        "closed_won": "won",
        "closed_lost": "lost",
    }
    stage_counts: dict[str, int] = {s: 0 for s in stage_names}
    stage_values: dict[str, float] = {s: 0.0 for s in stage_names}
    for opp in opps_raw:
        mapped = stage_mapping.get(opp["stage"], opp["stage"])
        if mapped in stage_counts:
            stage_counts[mapped] += 1
            stage_values[mapped] += opp["value"]

    # Also count leads by status for stages without opportunities
    for ld in leads_raw:
        if ld["status"] in ("won", "lost") and ld["status"] in stage_counts:
            # Already counted via opportunities where applicable
            pass

    total_opps = sum(stage_counts.values())
    stages: list[PipelineStage] = []
    for sname in stage_names:
        conv_rate = (stage_counts[sname] / total_opps * 100) if total_opps > 0 else 0.0
        stages.append(
            PipelineStage(
                name=sname,
                count=stage_counts[sname],
                value=round(stage_values[sname], 2),
                conversion_rate=round(conv_rate, 1),
            )
        )

    # ── Conversion metrics (stage-to-stage) ──────────────────────────
    stage_order = ["discovery", "proposal", "negotiation", "won"]
    conversions: list[ConversionMetrics] = []
    for idx in range(len(stage_order) - 1):
        s_from = stage_order[idx]
        s_to = stage_order[idx + 1]
        from_count = stage_counts.get(s_from, 0)
        to_count = stage_counts.get(s_to, 0)
        rate = (to_count / from_count * 100) if from_count > 0 else 0.0
        conversions.append(
            ConversionMetrics(
                stage_from=s_from,
                stage_to=s_to,
                rate=round(rate, 1),
                avg_days=round(15 + idx * 10.0, 1),  # Simulated average days
            )
        )

    # ── Territory breakdown ──────────────────────────────────────────
    regions_data: dict[str, dict[str, Any]] = {}
    for ld in leads_raw:
        region = ld.get("region", "Lisboa")
        if region not in regions_data:
            regions_data[region] = {"lead_count": 0, "pipeline_value": 0.0, "won": 0}
        regions_data[region]["lead_count"] += 1
        regions_data[region]["pipeline_value"] += ld.get("pipeline_value", 0.0)
        if ld["status"] == "won":
            regions_data[region]["won"] += 1

    territories: list[TerritoryView] = []
    for region, rd in sorted(regions_data.items()):
        conv = (rd["won"] / rd["lead_count"] * 100) if rd["lead_count"] > 0 else 0.0
        territories.append(
            TerritoryView(
                region=region,
                lead_count=rd["lead_count"],
                pipeline_value=round(rd["pipeline_value"], 2),
                conversion_rate=round(conv, 1),
            )
        )

    # ── Summary metrics ──────────────────────────────────────────────
    total_value = sum(o["value"] for o in opps_raw)
    weighted_value = sum(o["value"] * o["probability"] for o in opps_raw)
    avg_deal = total_value / len(opps_raw) if opps_raw else 0.0
    won_count = stage_counts.get("won", 0)
    win_rate = (won_count / total_opps * 100) if total_opps > 0 else 0.0

    return EnhancedSalesResponse(
        stages=stages,
        territories=territories,
        conversions=conversions,
        total_leads=len(leads_raw),
        total_pipeline_value=round(total_value, 2),
        weighted_pipeline_value=round(weighted_value, 2),
        avg_deal_size=round(avg_deal, 2),
        win_rate=round(win_rate, 1),
    )
