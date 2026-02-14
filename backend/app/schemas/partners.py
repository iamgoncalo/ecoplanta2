"""Partners network schemas -- partner profiles, allocation, optimization, quotes, compliance."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ── Compliance document ─────────────────────────────────────────────────────


class ComplianceDoc(BaseModel):
    """Compliance document reference for a partner."""

    name: str
    standard: str
    valid: bool = True
    expiry_date: str | None = None

    model_config = {"from_attributes": True}


# ── Partner capacity month ──────────────────────────────────────────────────


class PartnerCapacityMonth(BaseModel):
    """Monthly capacity plan for a partner."""

    month: str
    allocated_units: int = 0
    available_units: int = 0
    utilization_pct: float = 0.0

    model_config = {"from_attributes": True}


# ── Partner quote ───────────────────────────────────────────────────────────


class PartnerQuote(BaseModel):
    """Quote from a partner for a specific order."""

    id: str
    partner_id: str
    units: int = 0
    price_per_unit: float = 0.0
    total_price: float = 0.0
    lead_time_days: int = 0
    valid_until: date | None = None
    status: str = "active"

    model_config = {"from_attributes": True}


# ── Partner detail ──────────────────────────────────────────────────────────


class PartnerDetail(BaseSchema):
    """Full partner profile with capacity plans and compliance docs."""

    id: str
    name: str
    country: str
    region: str
    capacity_units_per_month: int = 0
    contact_email: str | None = None
    rating: float = 0.0
    lead_time_days: int = 30
    capacity_plans: list[PartnerCapacityMonth] = Field(default_factory=list)
    compliance_docs: list[ComplianceDoc] = Field(default_factory=list)
    quotes: list[PartnerQuote] = Field(default_factory=list)


# ── Capacity allocation ────────────────────────────────────────────────────


class AllocationRequest(BaseModel):
    """Request body for allocating an order to partners."""

    order_units: int
    preferred_country: str | None = None
    max_lead_time_days: int | None = None

    model_config = {"from_attributes": True}


class CapacityAllocation(BaseModel):
    """Order allocation to a partner."""

    partner_id: str
    partner_name: str
    country: str
    allocated_units: int = 0
    lead_time_days: int = 0
    estimated_cost: float = 0.0

    model_config = {"from_attributes": True}


class AllocationResponse(BaseModel):
    """Response for order allocation."""

    allocations: list[CapacityAllocation] = Field(default_factory=list)
    total_allocated: int = 0
    total_requested: int = 0
    fully_allocated: bool = False

    model_config = {"from_attributes": True}


# ── Allocation optimization ────────────────────────────────────────────────


class AllocationOptimization(BaseModel):
    """Result of optimization run across partners."""

    optimized_allocations: list[CapacityAllocation] = Field(default_factory=list)
    total_cost: float = 0.0
    avg_lead_time_days: float = 0.0
    total_units: int = 0
    optimization_score: float = 0.0

    model_config = {"from_attributes": True}


# ── Partner quotes response ─────────────────────────────────────────────────


class PartnerQuotesResponse(BaseModel):
    """Response containing quotes from a partner."""

    partner_id: str
    partner_name: str
    quotes: list[PartnerQuote] = Field(default_factory=list)
    total: int = 0

    model_config = {"from_attributes": True}


# ── Compliance overview ─────────────────────────────────────────────────────


class PartnerComplianceSummary(BaseModel):
    """Compliance summary for a single partner."""

    partner_id: str
    partner_name: str
    country: str
    docs: list[ComplianceDoc] = Field(default_factory=list)
    fully_compliant: bool = True

    model_config = {"from_attributes": True}


class ComplianceOverview(BaseModel):
    """EU compliance overview across all partners."""

    partners: list[PartnerComplianceSummary] = Field(default_factory=list)
    total_partners: int = 0
    fully_compliant_count: int = 0
    compliance_rate: float = 0.0

    model_config = {"from_attributes": True}
