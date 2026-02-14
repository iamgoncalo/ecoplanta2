"""Partners module -- partners, capacity plans, allocation, optimization, quotes, compliance."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    CapacityPlanSummary,
    PartnerItem,
    PartnerListResponse,
)
from app.schemas.partners import (
    AllocationOptimization,
    AllocationRequest,
    AllocationResponse,
    CapacityAllocation,
    ComplianceDoc,
    ComplianceOverview,
    PartnerCapacityMonth,
    PartnerComplianceSummary,
    PartnerDetail,
    PartnerQuote,
    PartnerQuotesResponse,
)

router = APIRouter(prefix="/api/partners", tags=["partners"])

# ── Helpers ─────────────────────────────────────────────────────────────────

# Standard EU compliance documents
_EU_COMPLIANCE_STANDARDS = [
    ("CE Marking", "CE Mark"),
    ("ISO 9001 Quality Management", "ISO 9001"),
    ("ISO 14001 Environmental Management", "ISO 14001"),
    ("EN 1090 Structural Steel/Aluminium", "EN 1090"),
]


def _parse_compliance_docs(partner: dict[str, Any]) -> list[ComplianceDoc]:
    """Parse compliance docs from partner's JSON field."""
    raw = partner.get("compliance_docs_json", "{}")
    docs_data = json.loads(raw) if isinstance(raw, str) else raw

    docs: list[ComplianceDoc] = []
    for name, standard in _EU_COMPLIANCE_STANDARDS:
        # Check if the partner has this standard
        key = standard.lower().replace(" ", "_")
        has_it = docs_data.get(key, docs_data.get("ce_mark", False))
        docs.append(
            ComplianceDoc(
                name=name,
                standard=standard,
                valid=has_it if isinstance(has_it, bool) else True,
            )
        )
    return docs


def _build_partner_detail(
    p: dict[str, Any],
    plans: list[dict[str, Any]],
    quotes: list[dict[str, Any]],
) -> PartnerDetail:
    """Build a PartnerDetail from raw seed data."""
    cap_months = [
        PartnerCapacityMonth(
            month=cp["month"],
            allocated_units=cp["allocated_units"],
            available_units=cp["available_units"],
            utilization_pct=cp["utilization_pct"],
        )
        for cp in plans
    ]

    compliance_docs = _parse_compliance_docs(p)

    partner_quotes = [
        PartnerQuote(
            id=q["id"],
            partner_id=q["partner_id"],
            units=q["units"],
            price_per_unit=q["price_per_unit"],
            total_price=q["total_price"],
            lead_time_days=q["lead_time_days"],
            valid_until=q.get("valid_until"),
            status=q.get("status", "active"),
        )
        for q in quotes
    ]

    return PartnerDetail(
        id=p["id"],
        name=p["name"],
        country=p["country"],
        region=p["region"],
        capacity_units_per_month=p["capacity_units_per_month"],
        contact_email=p.get("contact_email"),
        rating=p["rating"],
        lead_time_days=p["lead_time_days"],
        capacity_plans=cap_months,
        compliance_docs=compliance_docs,
        quotes=partner_quotes,
        source=p.get("source", "synthetic_seeded"),
        source_id=p.get("source_id"),
    )


def _get_partner_indexes() -> tuple[
    list[dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    """Return partners, plans by partner, and quotes by partner."""
    data = get_seed_data()
    partners_raw = data["partners"]
    plans_raw = data["capacity_plans"]
    quotes_raw = data.get("partner_quotes", [])

    plans_by_partner: dict[str, list[dict[str, Any]]] = {}
    for plan in plans_raw:
        plans_by_partner.setdefault(plan["partner_id"], []).append(plan)

    quotes_by_partner: dict[str, list[dict[str, Any]]] = {}
    for q in quotes_raw:
        quotes_by_partner.setdefault(q["partner_id"], []).append(q)

    return partners_raw, plans_by_partner, quotes_by_partner


# ── GET: list partners (existing endpoint, unchanged contract) ──────────────


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
    plans_by_partner: dict[str, list[dict[str, Any]]] = {}
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


# ── GET: partner detail ───────────────────────────────────────────────────


@router.get("/compliance", response_model=ComplianceOverview)
async def compliance_overview(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ComplianceOverview:
    """EU compliance overview across all partners."""
    partners_raw, plans_by_partner, quotes_by_partner = _get_partner_indexes()

    summaries: list[PartnerComplianceSummary] = []
    fully_compliant = 0

    for p in partners_raw:
        docs = _parse_compliance_docs(p)
        all_valid = all(d.valid for d in docs)
        if all_valid:
            fully_compliant += 1

        summaries.append(
            PartnerComplianceSummary(
                partner_id=p["id"],
                partner_name=p["name"],
                country=p["country"],
                docs=docs,
                fully_compliant=all_valid,
            )
        )

    total = len(summaries)
    rate = round(fully_compliant / total * 100, 1) if total > 0 else 0.0

    return ComplianceOverview(
        partners=summaries,
        total_partners=total,
        fully_compliant_count=fully_compliant,
        compliance_rate=rate,
    )


# ── GET: optimize allocation ──────────────────────────────────────────────


@router.get("/optimize", response_model=AllocationOptimization)
async def optimize_allocation(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AllocationOptimization:
    """Run optimization simulation for current orders across partners.

    Uses a greedy algorithm: sort partners by cost-efficiency (rating / lead_time),
    then allocate available capacity.
    """
    data = get_seed_data()
    partners_raw = data["partners"]
    plans_raw = data["capacity_plans"]

    # Get current month available capacity
    plans_by_partner: dict[str, list[dict[str, Any]]] = {}
    for plan in plans_raw:
        plans_by_partner.setdefault(plan["partner_id"], []).append(plan)

    allocations: list[CapacityAllocation] = []
    total_cost = 0.0
    total_units = 0
    total_lead_time = 0.0

    # Sort partners by efficiency: higher rating and lower lead time is better
    sorted_partners = sorted(
        partners_raw,
        key=lambda p: p["rating"] / max(p["lead_time_days"], 1),
        reverse=True,
    )

    for p in sorted_partners:
        p_plans = plans_by_partner.get(p["id"], [])
        available = sum(cp["available_units"] for cp in p_plans) // max(len(p_plans), 1)

        if available > 0:
            cost_per_unit = round(5000.0 / p["rating"], 2)
            est_cost = round(available * cost_per_unit, 2)
            total_cost += est_cost
            total_units += available
            total_lead_time += p["lead_time_days"]

            allocations.append(
                CapacityAllocation(
                    partner_id=p["id"],
                    partner_name=p["name"],
                    country=p["country"],
                    allocated_units=available,
                    lead_time_days=p["lead_time_days"],
                    estimated_cost=est_cost,
                )
            )

    avg_lead = round(total_lead_time / len(allocations), 1) if allocations else 0.0
    # Score: higher is better (more units, lower cost, lower lead time)
    score = round((total_units / max(total_cost, 1) * 10000) / max(avg_lead, 1) * 100, 2)

    return AllocationOptimization(
        optimized_allocations=allocations,
        total_cost=round(total_cost, 2),
        avg_lead_time_days=avg_lead,
        total_units=total_units,
        optimization_score=score,
    )


# ── POST: allocate order ─────────────────────────────────────────────────


@router.post("/allocate", response_model=AllocationResponse)
async def allocate_order(
    body: AllocationRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> AllocationResponse:
    """Allocate an order to optimal partner(s) based on capacity, lead time, cost."""
    data = get_seed_data()
    partners_raw = data["partners"]
    plans_raw = data["capacity_plans"]

    # Filter by preferred country if specified
    candidates = partners_raw
    if body.preferred_country:
        candidates = [
            p for p in partners_raw if p["country"].lower() == body.preferred_country.lower()
        ]
        if not candidates:
            candidates = partners_raw

    # Filter by max lead time if specified
    if body.max_lead_time_days:
        candidates = [p for p in candidates if p["lead_time_days"] <= body.max_lead_time_days]
        if not candidates:
            candidates = partners_raw

    # Get available capacity for each partner
    plans_by_partner: dict[str, list[dict[str, Any]]] = {}
    for plan in plans_raw:
        plans_by_partner.setdefault(plan["partner_id"], []).append(plan)

    # Sort by rating (descending) then lead_time (ascending)
    candidates = sorted(
        candidates,
        key=lambda p: (-p["rating"], p["lead_time_days"]),
    )

    allocations: list[CapacityAllocation] = []
    remaining = body.order_units

    for p in candidates:
        if remaining <= 0:
            break

        p_plans = plans_by_partner.get(p["id"], [])
        # Use average available capacity across months
        available = sum(cp["available_units"] for cp in p_plans) // max(len(p_plans), 1)

        if available > 0:
            to_allocate = min(remaining, available)
            cost_per_unit = round(5000.0 / p["rating"], 2)
            est_cost = round(to_allocate * cost_per_unit, 2)

            allocations.append(
                CapacityAllocation(
                    partner_id=p["id"],
                    partner_name=p["name"],
                    country=p["country"],
                    allocated_units=to_allocate,
                    lead_time_days=p["lead_time_days"],
                    estimated_cost=est_cost,
                )
            )
            remaining -= to_allocate

    total_allocated = sum(a.allocated_units for a in allocations)

    return AllocationResponse(
        allocations=allocations,
        total_allocated=total_allocated,
        total_requested=body.order_units,
        fully_allocated=remaining <= 0,
    )


# ── GET: partner quotes ──────────────────────────────────────────────────


@router.get("/{partner_id}/quotes", response_model=PartnerQuotesResponse)
async def get_partner_quotes(
    partner_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PartnerQuotesResponse:
    """Get quotes from a specific partner."""
    data = get_seed_data()
    partners_raw = data["partners"]
    quotes_raw = data.get("partner_quotes", [])

    partner = None
    for p in partners_raw:
        if p["id"] == partner_id:
            partner = p
            break

    if partner is None:
        raise HTTPException(status_code=404, detail=f"Partner {partner_id} not found")

    partner_quotes = [
        PartnerQuote(
            id=q["id"],
            partner_id=q["partner_id"],
            units=q["units"],
            price_per_unit=q["price_per_unit"],
            total_price=q["total_price"],
            lead_time_days=q["lead_time_days"],
            valid_until=q.get("valid_until"),
            status=q.get("status", "active"),
        )
        for q in quotes_raw
        if q["partner_id"] == partner_id
    ]

    return PartnerQuotesResponse(
        partner_id=partner_id,
        partner_name=partner["name"],
        quotes=partner_quotes,
        total=len(partner_quotes),
    )


# ── GET: partner detail ──────────────────────────────────────────────────


@router.get("/{partner_id}", response_model=PartnerDetail)
async def get_partner(
    partner_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> PartnerDetail:
    """Get partner detail with capacity plans and compliance docs."""
    partners_raw, plans_by_partner, quotes_by_partner = _get_partner_indexes()

    for p in partners_raw:
        if p["id"] == partner_id:
            plans = plans_by_partner.get(p["id"], [])
            quotes = quotes_by_partner.get(p["id"], [])
            return _build_partner_detail(p, plans, quotes)

    raise HTTPException(status_code=404, detail=f"Partner {partner_id} not found")
