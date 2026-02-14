"""Partners module -- partners and capacity plans."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    CapacityPlanSummary,
    PartnerItem,
    PartnerListResponse,
)

router = APIRouter(prefix="/api/partners", tags=["partners"])


@router.get("", response_model=PartnerListResponse)
async def list_partners(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PartnerListResponse:
    """List partners with capacity plans and utilisation stats.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    partners_raw = data["partners"]
    plans_raw = data["capacity_plans"]

    # Index capacity plans by partner_id
    plans_by_partner: dict[str, list[dict]] = {}
    for plan in plans_raw:
        plans_by_partner.setdefault(plan["partner_id"], []).append(plan)

    partner_items: list[PartnerItem] = []
    for p in partners_raw:
        p_plans = plans_by_partner.get(p["id"], [])
        plan_summaries = [
            CapacityPlanSummary(
                id=cp["id"],
                month=cp["month"],
                allocated_units=cp["allocated_units"],
                available_units=cp["available_units"],
                utilization_pct=cp["utilization_pct"],
                source=cp.get("source", "synthetic_seeded"),
                source_id=cp.get("source_id"),
            )
            for cp in p_plans
        ]
        partner_items.append(
            PartnerItem(
                id=p["id"],
                name=p["name"],
                country=p["country"],
                region=p["region"],
                capacity_units_per_month=p["capacity_units_per_month"],
                contact_email=p.get("contact_email"),
                rating=p["rating"],
                lead_time_days=p["lead_time_days"],
                capacity_plans=plan_summaries,
                source=p.get("source", "synthetic_seeded"),
                source_id=p.get("source_id"),
            )
        )

    total_cap = sum(p.capacity_units_per_month for p in partner_items)
    all_util = [cp["utilization_pct"] for cp in plans_raw]
    avg_util = round(sum(all_util) / len(all_util), 1) if all_util else 0.0

    return PartnerListResponse(
        partners=partner_items,
        total_partners=len(partner_items),
        total_capacity=total_cap,
        avg_utilization=avg_util,
    )
