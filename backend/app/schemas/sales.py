"""Enhanced sales schemas -- pipeline stages, territories, conversion metrics."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ── Pipeline stages ──────────────────────────────────────────────────────────


class PipelineStage(BaseModel):
    """Counts and value for a single pipeline stage."""

    name: str
    count: int = 0
    value: float = 0.0
    conversion_rate: float = 0.0

    model_config = {"from_attributes": True}


# ── Territory view ───────────────────────────────────────────────────────────


class TerritoryView(BaseModel):
    """Pipeline breakdown by Portugal region."""

    region: str
    lead_count: int = 0
    pipeline_value: float = 0.0
    conversion_rate: float = 0.0

    model_config = {"from_attributes": True}


# ── Conversion metrics ───────────────────────────────────────────────────────


class ConversionMetrics(BaseModel):
    """Stage-to-stage conversion rate."""

    stage_from: str
    stage_to: str
    rate: float = 0.0
    avg_days: float = 0.0

    model_config = {"from_attributes": True}


# ── Lead CRUD request schemas ────────────────────────────────────────────────


class LeadCreate(BaseModel):
    """Request body for creating a new lead."""

    name: str
    email: str
    phone: str | None = None
    company: str | None = None
    region: str = "Lisboa"
    notes: str | None = None

    model_config = {"from_attributes": True}


class LeadUpdate(BaseModel):
    """Request body for updating a lead's stage."""

    status: str

    model_config = {"from_attributes": True}


# ── Enhanced response ────────────────────────────────────────────────────────


class EnhancedSalesResponse(BaseModel):
    """Full pipeline analytics response."""

    stages: list[PipelineStage] = Field(default_factory=list)
    territories: list[TerritoryView] = Field(default_factory=list)
    conversions: list[ConversionMetrics] = Field(default_factory=list)
    total_leads: int = 0
    total_pipeline_value: float = 0.0
    weighted_pipeline_value: float = 0.0
    avg_deal_size: float = 0.0
    win_rate: float = 0.0

    model_config = {"from_attributes": True}


# ── Lead response (for POST/PATCH) ──────────────────────────────────────────


class LeadResponse(BaseSchema):
    """Single lead returned by create / update endpoints."""

    id: str
    name: str
    email: str
    phone: str | None = None
    company: str | None = None
    status: str = "new"
    score: int = 0
    region: str = "Lisboa"
    assigned_to: str | None = None
    notes: str | None = None
