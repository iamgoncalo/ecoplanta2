"""Factory execution schemas -- work orders, BOM details, inventory, QA."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema

# ── BOM detail ───────────────────────────────────────────────────────────────


class BOMLineItem(BaseModel):
    """Single material line within a BOM."""

    material_id: str
    material_name: str
    quantity: int = 0
    unit: str = "units"
    unit_cost: float = 0.0
    line_cost: float = 0.0

    model_config = {"from_attributes": True}


class BOMDetail(BaseSchema):
    """Bill of Materials with full item breakdown."""

    id: str
    house_config_id: str
    house_config_name: str | None = None
    version: int = 1
    items: list[BOMLineItem] = Field(default_factory=list)
    total_cost: float = 0.0
    status: str = "draft"


# ── QA detail ────────────────────────────────────────────────────────────────


class QARecordDetail(BaseSchema):
    """Single QA inspection record."""

    id: str
    work_order_id: str
    inspector: str
    result: str
    defects: list[dict] = Field(default_factory=list)
    notes: str | None = None
    inspected_at: datetime | None = None


class QASummary(BaseModel):
    """Aggregated QA statistics."""

    total_inspections: int = 0
    pass_rate: float = 0.0
    fail_rate: float = 0.0
    common_defects: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Work order detail ────────────────────────────────────────────────────────


class StatusHistoryEntry(BaseModel):
    """A single status change event."""

    status: str
    timestamp: str | None = None
    note: str | None = None

    model_config = {"from_attributes": True}


class WorkOrderDetail(BaseSchema):
    """Work order with nested BOM and QA records."""

    id: str
    bom_id: str
    production_line_id: str | None = None
    production_line_name: str | None = None
    status: str = "planned"
    priority: int = 3
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    bom: BOMDetail | None = None
    qa_records: list[QARecordDetail] = Field(default_factory=list)
    status_history: list[StatusHistoryEntry] = Field(default_factory=list)


class WorkOrderListResponse(BaseModel):
    """Response for listing work orders."""

    work_orders: list[WorkOrderDetail] = Field(default_factory=list)
    total: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── Work order create / update ───────────────────────────────────────────────


class WorkOrderCreate(BaseModel):
    """Request body for creating a work order from a BOM."""

    bom_id: str
    production_line_id: str | None = None
    priority: int = 3
    scheduled_start: str | None = None
    scheduled_end: str | None = None

    model_config = {"from_attributes": True}


class WorkOrderStatusUpdate(BaseModel):
    """Request body for updating a work order status."""

    status: str
    note: str | None = None

    model_config = {"from_attributes": True}


# ── Inventory ────────────────────────────────────────────────────────────────


class InventoryItem(BaseSchema):
    """Inventory record with stock level and alert info."""

    id: str
    material_id: str
    material_name: str | None = None
    warehouse: str
    quantity: float = 0.0
    unit: str = "kg"
    min_stock: float = 0.0
    max_stock: float = 0.0
    reorder_needed: bool = False


class InventoryAlert(BaseModel):
    """Materials below minimum stock threshold."""

    material: str
    material_id: str
    current_stock: float = 0.0
    min_stock: float = 0.0
    reorder_needed: bool = True

    model_config = {"from_attributes": True}


class InventoryListResponse(BaseModel):
    """Response for inventory listing."""

    items: list[InventoryItem] = Field(default_factory=list)
    total: int = 0
    alerts: list[InventoryAlert] = Field(default_factory=list)
    total_alerts: int = 0

    model_config = {"from_attributes": True}


# ── QA list response ────────────────────────────────────────────────────────


class QAListResponse(BaseModel):
    """Response for QA records listing."""

    records: list[QARecordDetail] = Field(default_factory=list)
    summary: QASummary = Field(default_factory=QASummary)

    model_config = {"from_attributes": True}
