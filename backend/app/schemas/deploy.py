"""Enhanced deploy schemas -- delivery schedule, checklists, commissioning."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ── Delivery schedule ────────────────────────────────────────────────────────


class DeliveryScheduleDelivery(BaseModel):
    """A delivery entry within a schedule day."""

    id: str
    destination: str
    status: str
    carrier: str

    model_config = {"from_attributes": True}


class DeliveryScheduleInstallation(BaseModel):
    """An installation entry within a schedule day."""

    id: str
    site_address: str
    status: str
    crew_lead: str | None = None

    model_config = {"from_attributes": True}


class DeliveryScheduleItem(BaseModel):
    """A single day in the delivery schedule calendar."""

    date: date
    deliveries: list[DeliveryScheduleDelivery] = Field(default_factory=list)
    installations: list[DeliveryScheduleInstallation] = Field(default_factory=list)
    delivery_count: int = 0
    installation_count: int = 0

    model_config = {"from_attributes": True}


class DeliveryScheduleResponse(BaseModel):
    """Calendar-style delivery schedule response."""

    schedule: list[DeliveryScheduleItem] = Field(default_factory=list)
    total_days: int = 0
    total_deliveries: int = 0
    total_installations: int = 0

    model_config = {"from_attributes": True}


# ── Installation checklist ───────────────────────────────────────────────────


class ChecklistItem(BaseModel):
    """A single checklist item with completion status."""

    key: str
    label: str
    completed: bool = False

    model_config = {"from_attributes": True}


class InstallationChecklist(BaseModel):
    """Full installation checklist for a deployment job."""

    job_id: str
    items: list[ChecklistItem] = Field(default_factory=list)
    completed_count: int = 0
    total_count: int = 0
    completion_pct: float = 0.0

    model_config = {"from_attributes": True}


# ── Commissioning overview ───────────────────────────────────────────────────


class CommissioningOverview(BaseModel):
    """Commissioning status summary across all deployment jobs."""

    total: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    issues: int = 0

    model_config = {"from_attributes": True}


# ── Delivery CRUD request schemas ────────────────────────────────────────────


class DeliveryCreate(BaseModel):
    """Request body for creating a delivery."""

    work_order_id: str
    destination: str
    carrier: str | None = None
    estimated_arrival: str | None = None

    model_config = {"from_attributes": True}


class DeliveryStatusUpdate(BaseModel):
    """Request body for updating a delivery status."""

    status: str

    model_config = {"from_attributes": True}


# ── Checklist update ─────────────────────────────────────────────────────────


class ChecklistUpdate(BaseModel):
    """Request body for updating checklist items."""

    items: dict[str, bool] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── Deployment job detail ────────────────────────────────────────────────────


class DeploymentJobDetail(BaseSchema):
    """Full deployment job detail with checklist."""

    id: str
    delivery_id: str
    site_address: str
    status: str = "planned"
    commissioning_date: date | None = None
    crew_lead: str | None = None
    checklist: InstallationChecklist | None = None


# ── Delivery response (for POST/PATCH) ──────────────────────────────────────


class DeliveryResponse(BaseSchema):
    """Single delivery returned by create / update endpoints."""

    id: str
    work_order_id: str
    origin: str
    destination: str
    carrier: str
    status: str = "preparing"
    estimated_arrival: str | None = None
    actual_arrival: str | None = None
