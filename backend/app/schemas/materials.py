"""Materials & Patents schemas -- material specs, comparisons, audit trails, BOM variants."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ── Material detail ─────────────────────────────────────────────────────────


class MaterialDetail(BaseSchema):
    """Full material specification with supplier info and compliance."""

    id: str
    name: str
    category: str
    grade: str
    density: float = 0.0
    tensile_strength: float = 0.0
    thermal_conductivity: float = 0.0
    embodied_carbon_kg: float = 0.0
    supplier_id: str | None = None
    supplier_name: str | None = None
    is_smart_material: bool = False
    compliance_certs: str = ""
    lead_time_days: int = 14
    cost_per_kg: float = 0.0


# ── Material search result ──────────────────────────────────────────────────


class MaterialSearchResult(BaseModel):
    """Search response with filters applied."""

    materials: list[MaterialDetail] = Field(default_factory=list)
    total: int = 0
    filters_applied: dict[str, str | bool | float] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── Material comparison ─────────────────────────────────────────────────────


class MaterialComparison(BaseModel):
    """Side-by-side comparison of 2+ materials."""

    materials: list[MaterialDetail] = Field(default_factory=list)
    comparison_fields: list[str] = Field(default_factory=list)
    best_by: dict[str, str] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── Patent detail ───────────────────────────────────────────────────────────


class PatentExperimentResult(BaseModel):
    """A single experiment result for a patent."""

    description: str
    result: str
    date: str | None = None

    model_config = {"from_attributes": True}


class PatentDetail(BaseSchema):
    """Full patent information with claims and experiments."""

    id: str
    title: str
    filing_number: str
    status: str = "filed"
    filing_date: str | None = None
    claims: dict | None = None
    experiment_results: dict | None = None
    inventors: str = ""
    novelty_notes: str = ""
    additional_experiments: list[PatentExperimentResult] = Field(default_factory=list)


# ── BOM variant ─────────────────────────────────────────────────────────────


class BOMVariantLine(BaseModel):
    """Single line item in a BOM variant with alternative material."""

    material_id: str
    material_name: str
    alternative_material_id: str | None = None
    alternative_material_name: str | None = None
    quantity: int = 0
    unit_cost: float = 0.0
    alternative_unit_cost: float | None = None

    model_config = {"from_attributes": True}


class BOMVariant(BaseModel):
    """BOM with material alternatives."""

    variant_name: str
    framework_id: str
    items: list[BOMVariantLine] = Field(default_factory=list)
    total_cost: float = 0.0
    total_embodied_carbon: float = 0.0

    model_config = {"from_attributes": True}


class BOMVariantsResponse(BaseModel):
    """Response containing multiple BOM variants."""

    framework_id: str
    framework_name: str
    variants: list[BOMVariant] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Material audit trail ────────────────────────────────────────────────────


class MaterialSelectionRequest(BaseModel):
    """Request body for recording a material selection decision."""

    material_id: str
    project_id: str | None = None
    reason: str = ""
    selected_by: str = ""

    model_config = {"from_attributes": True}


class MaterialAuditTrail(BaseModel):
    """Record of a material selection decision."""

    id: str
    material_id: str
    material_name: str
    project_id: str | None = None
    reason: str = ""
    selected_by: str = ""
    decision_date: datetime | None = None

    model_config = {"from_attributes": True}


class MaterialAuditTrailResponse(BaseModel):
    """Response containing the audit trail of material selections."""

    entries: list[MaterialAuditTrail] = Field(default_factory=list)
    total: int = 0

    model_config = {"from_attributes": True}


# ── Patent list response ────────────────────────────────────────────────────


class PatentListResponse(BaseModel):
    """Response for listing patents."""

    patents: list[PatentDetail] = Field(default_factory=list)
    total: int = 0

    model_config = {"from_attributes": True}
