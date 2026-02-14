"""Pydantic response schemas for each front-end module endpoint."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ═══════════════════════════════════════════════════════════════════════════════
# Fabric (production lines, work orders)
# ═══════════════════════════════════════════════════════════════════════════════


class FabricItem(BaseSchema):
    id: str
    name: str
    location: str
    capacity_units_per_day: int = 0
    status: str = "idle"
    current_workorder_id: str | None = None
    # Nested work-order summary when relevant
    active_work_orders: int = 0
    total_work_orders: int = 0


class FabricListResponse(BaseModel):
    production_lines: list[FabricItem] = Field(default_factory=list)
    total_lines: int = 0
    lines_running: int = 0
    total_work_orders: int = 0

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Frameworks (structural frameworks, materials, patents)
# ═══════════════════════════════════════════════════════════════════════════════


class MaterialSummary(BaseSchema):
    id: str
    name: str
    category: str
    grade: str
    is_smart_material: bool = False
    tensile_strength: float = 0.0
    embodied_carbon_kg: float = 0.0


class PatentSummary(BaseSchema):
    id: str
    title: str
    filing_number: str
    status: str = "filed"
    filing_date: date | None = None


class FrameworkItem(BaseSchema):
    id: str
    name: str
    framework_type: str
    description: str | None = None
    structural_rating: str = "A"
    materials: list[MaterialSummary] = Field(default_factory=list)
    patents: list[PatentSummary] = Field(default_factory=list)


class FrameworkListResponse(BaseModel):
    frameworks: list[FrameworkItem] = Field(default_factory=list)
    total_frameworks: int = 0
    total_materials: int = 0
    total_patents: int = 0

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Sales (leads, opportunities, pipeline)
# ═══════════════════════════════════════════════════════════════════════════════


class OpportunitySummary(BaseSchema):
    id: str
    title: str
    value: float = 0.0
    stage: str = "discovery"
    probability: float = 0.0


class SalesLeadItem(BaseSchema):
    id: str
    name: str
    email: str
    company: str | None = None
    status: str = "new"
    score: int = 0
    opportunities: list[OpportunitySummary] = Field(default_factory=list)


class PipelineStats(BaseModel):
    total_leads: int = 0
    qualified_leads: int = 0
    total_pipeline_value: float = 0.0
    weighted_pipeline_value: float = 0.0
    avg_deal_size: float = 0.0

    model_config = {"from_attributes": True}


class SalesListResponse(BaseModel):
    leads: list[SalesLeadItem] = Field(default_factory=list)
    pipeline: PipelineStats = Field(default_factory=PipelineStats)

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Intelligence (insight reports, forecasts)
# ═══════════════════════════════════════════════════════════════════════════════


class IntelligenceInsight(BaseSchema):
    id: str
    title: str
    module: str
    report_type: str
    parameters: dict | None = None
    results: dict | None = None
    generated_at: datetime | None = None


class IntelligenceListResponse(BaseModel):
    insights: list[IntelligenceInsight] = Field(default_factory=list)
    total_insights: int = 0

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Deploy (deliveries, deployment jobs)
# ═══════════════════════════════════════════════════════════════════════════════


class DeploymentJobSummary(BaseSchema):
    id: str
    site_address: str
    status: str = "planned"
    commissioning_date: date | None = None
    crew_lead: str | None = None


class DeployItem(BaseSchema):
    id: str
    origin: str
    destination: str
    carrier: str
    status: str = "preparing"
    estimated_arrival: datetime | None = None
    actual_arrival: datetime | None = None
    deployment_jobs: list[DeploymentJobSummary] = Field(default_factory=list)


class DeployListResponse(BaseModel):
    deliveries: list[DeployItem] = Field(default_factory=list)
    total_deliveries: int = 0
    in_transit: int = 0
    delivered: int = 0

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Partners (partners, capacity plans)
# ═══════════════════════════════════════════════════════════════════════════════


class CapacityPlanSummary(BaseSchema):
    id: str
    month: str
    allocated_units: int = 0
    available_units: int = 0
    utilization_pct: float = 0.0


class PartnerItem(BaseSchema):
    id: str
    name: str
    country: str
    region: str
    capacity_units_per_month: int = 0
    contact_email: str | None = None
    rating: float = 0.0
    lead_time_days: int = 30
    capacity_plans: list[CapacityPlanSummary] = Field(default_factory=list)


class PartnerListResponse(BaseModel):
    partners: list[PartnerItem] = Field(default_factory=list)
    total_partners: int = 0
    total_capacity: int = 0
    avg_utilization: float = 0.0

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# 3D Scene objects (for factory / house visualisation)
# ═══════════════════════════════════════════════════════════════════════════════


class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    model_config = {"from_attributes": True}


class SceneObject(BaseModel):
    id: str
    name: str
    type: str  # "machine", "conveyor", "wall", "module", etc.
    position: Vec3 = Field(default_factory=Vec3)
    rotation: Vec3 = Field(default_factory=Vec3)
    scale: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=1))
    color: str = "#888888"
    metadata: dict | None = None

    model_config = {"from_attributes": True}


class CameraDefaults(BaseModel):
    position: Vec3 = Field(default_factory=lambda: Vec3(x=10, y=8, z=10))
    target: Vec3 = Field(default_factory=Vec3)
    fov: float = 60.0

    model_config = {"from_attributes": True}


class SceneResponse(BaseModel):
    objects: list[SceneObject] = Field(default_factory=list)
    camera: CameraDefaults = Field(default_factory=CameraDefaults)

    model_config = {"from_attributes": True}
