"""SQLAlchemy 2.0 ORM models for all EcoContainer + Planta Smart Homes domain entities."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

# ── Enums ─────────────────────────────────────────────────────────────────────


class DataSource(enum.StrEnum):
    """Provenance tag for every record."""

    synthetic_seeded = "synthetic_seeded"
    integration_stub = "integration_stub"
    real = "real"


class LeadStatus(enum.StrEnum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    proposal = "proposal"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"


class OpportunityStage(enum.StrEnum):
    discovery = "discovery"
    proposal = "proposal"
    negotiation = "negotiation"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


class ContractStatus(enum.StrEnum):
    draft = "draft"
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class PatentStatus(enum.StrEnum):
    filed = "filed"
    pending = "pending"
    granted = "granted"
    rejected = "rejected"


class BOMStatus(enum.StrEnum):
    draft = "draft"
    approved = "approved"
    in_production = "in_production"
    completed = "completed"


class WorkOrderStatus(enum.StrEnum):
    planned = "planned"
    scheduled = "scheduled"
    in_progress = "in_progress"
    quality_check = "quality_check"
    completed = "completed"
    on_hold = "on_hold"


class ProductionLineStatus(enum.StrEnum):
    idle = "idle"
    running = "running"
    maintenance = "maintenance"
    offline = "offline"


class DeliveryStatus(enum.StrEnum):
    preparing = "preparing"
    in_transit = "in_transit"
    delivered = "delivered"
    delayed = "delayed"


class DeploymentStatus(enum.StrEnum):
    planned = "planned"
    site_prep = "site_prep"
    installing = "installing"
    commissioning = "commissioning"
    completed = "completed"


class HomeUnitStatus(enum.StrEnum):
    manufacturing = "manufacturing"
    shipped = "shipped"
    installed = "installed"
    active = "active"
    maintenance = "maintenance"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Mixin ─────────────────────────────────────────────────────────────────────
# Every domain model inherits common audit and provenance columns.


class AuditMixin:
    """Provides created_at, updated_at, source, and source_id."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    source: Mapped[DataSource] = mapped_column(
        Enum(DataSource, name="data_source_enum"),
        default=DataSource.synthetic_seeded,
        nullable=False,
    )
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


# ── Domain models ─────────────────────────────────────────────────────────────


class Lead(AuditMixin, Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status_enum"), default=LeadStatus.new
    )
    score: Mapped[int] = mapped_column(Integer, default=0)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    opportunities: Mapped[list[Opportunity]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class Opportunity(AuditMixin, Base):
    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    lead_id: Mapped[str] = mapped_column(String(36), ForeignKey("leads.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    stage: Mapped[OpportunityStage] = mapped_column(
        Enum(OpportunityStage, name="opportunity_stage_enum"),
        default=OpportunityStage.discovery,
    )
    probability: Mapped[float] = mapped_column(Float, default=0.0)
    expected_close: Mapped[date | None] = mapped_column(Date, nullable=True)

    lead: Mapped[Lead] = relationship(back_populates="opportunities")
    contracts: Mapped[list[Contract]] = relationship(
        back_populates="opportunity", cascade="all, delete-orphan"
    )


class Contract(AuditMixin, Base):
    __tablename__ = "contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    opportunity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("opportunities.id"), nullable=False
    )
    number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="contract_status_enum"),
        default=ContractStatus.draft,
    )
    signed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    terms: Mapped[str | None] = mapped_column(Text, nullable=True)

    opportunity: Mapped[Opportunity] = relationship(back_populates="contracts")


class Supplier(AuditMixin, Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=14)
    certifications: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    materials: Mapped[list[Material]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class Material(AuditMixin, Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    density: Mapped[float] = mapped_column(Float, default=0.0)
    tensile_strength: Mapped[float] = mapped_column(Float, default=0.0)
    thermal_conductivity: Mapped[float] = mapped_column(Float, default=0.0)
    embodied_carbon_kg: Mapped[float] = mapped_column(Float, default=0.0)
    supplier_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("suppliers.id"), nullable=True
    )
    is_smart_material: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_certs: Mapped[str | None] = mapped_column(Text, nullable=True)

    supplier: Mapped[Supplier | None] = relationship(back_populates="materials")
    inventory_items: Mapped[list[InventoryItem]] = relationship(
        back_populates="material", cascade="all, delete-orphan"
    )


class HouseConfig(AuditMixin, Base):
    __tablename__ = "house_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    num_modules: Mapped[int] = mapped_column(Integer, default=1)
    floor_area_m2: Mapped[float] = mapped_column(Float, default=0.0)
    num_floors: Mapped[int] = mapped_column(Integer, default=1)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    boms: Mapped[list[BOM]] = relationship(
        back_populates="house_config", cascade="all, delete-orphan"
    )
    home_units: Mapped[list[HomeUnit]] = relationship(
        back_populates="house_config", cascade="all, delete-orphan"
    )


class Framework(AuditMixin, Base):
    __tablename__ = "frameworks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    framework_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    structural_rating: Mapped[str] = mapped_column(String(10), default="A")
    materials_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    patent_ids: Mapped[str | None] = mapped_column(Text, nullable=True)


class Patent(AuditMixin, Base):
    __tablename__ = "patents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    filing_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    status: Mapped[PatentStatus] = mapped_column(
        Enum(PatentStatus, name="patent_status_enum"), default=PatentStatus.filed
    )
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    claims_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    experiment_results_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    inventors: Mapped[str | None] = mapped_column(Text, nullable=True)
    novelty_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class BOM(AuditMixin, Base):
    __tablename__ = "boms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    house_config_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("house_configs.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    items_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[BOMStatus] = mapped_column(
        Enum(BOMStatus, name="bom_status_enum"), default=BOMStatus.draft
    )

    house_config: Mapped[HouseConfig] = relationship(back_populates="boms")
    work_orders: Mapped[list[WorkOrder]] = relationship(
        back_populates="bom", cascade="all, delete-orphan"
    )


class ProductionLine(AuditMixin, Base):
    __tablename__ = "production_lines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity_units_per_day: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[ProductionLineStatus] = mapped_column(
        Enum(ProductionLineStatus, name="production_line_status_enum"),
        default=ProductionLineStatus.idle,
    )
    current_workorder_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class WorkOrder(AuditMixin, Base):
    __tablename__ = "work_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    bom_id: Mapped[str] = mapped_column(String(36), ForeignKey("boms.id"), nullable=False)
    production_line_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("production_lines.id"), nullable=True
    )
    status: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus, name="work_order_status_enum"),
        default=WorkOrderStatus.planned,
    )
    priority: Mapped[int] = mapped_column(Integer, default=3)
    scheduled_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    bom: Mapped[BOM] = relationship(back_populates="work_orders")
    production_line: Mapped[ProductionLine | None] = relationship()
    qa_records: Mapped[list[QARecord]] = relationship(
        back_populates="work_order", cascade="all, delete-orphan"
    )
    deliveries: Mapped[list[Delivery]] = relationship(
        back_populates="work_order", cascade="all, delete-orphan"
    )


class InventoryItem(AuditMixin, Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    material_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("materials.id"), nullable=False
    )
    warehouse: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    min_stock: Mapped[float] = mapped_column(Float, default=0.0)
    max_stock: Mapped[float] = mapped_column(Float, default=0.0)

    material: Mapped[Material] = relationship(back_populates="inventory_items")


class QARecord(AuditMixin, Base):
    __tablename__ = "qa_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    work_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_orders.id"), nullable=False
    )
    inspector: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(String(50), nullable=False)
    defects_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    inspected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    work_order: Mapped[WorkOrder] = relationship(back_populates="qa_records")


class Delivery(AuditMixin, Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    work_order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("work_orders.id"), nullable=False
    )
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    carrier: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status_enum"),
        default=DeliveryStatus.preparing,
    )
    estimated_arrival: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    work_order: Mapped[WorkOrder] = relationship(back_populates="deliveries")
    deployment_jobs: Mapped[list[DeploymentJob]] = relationship(
        back_populates="delivery", cascade="all, delete-orphan"
    )


class DeploymentJob(AuditMixin, Base):
    __tablename__ = "deployment_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    delivery_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("deliveries.id"), nullable=False
    )
    site_address: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DeploymentStatus] = mapped_column(
        Enum(DeploymentStatus, name="deployment_status_enum"),
        default=DeploymentStatus.planned,
    )
    installation_checklist_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    commissioning_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    crew_lead: Mapped[str | None] = mapped_column(String(255), nullable=True)

    delivery: Mapped[Delivery] = relationship(back_populates="deployment_jobs")


class Partner(AuditMixin, Base):
    __tablename__ = "partners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity_units_per_month: Mapped[int] = mapped_column(Integer, default=0)
    compliance_docs_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=30)

    capacity_plans: Mapped[list[CapacityPlan]] = relationship(
        back_populates="partner", cascade="all, delete-orphan"
    )


class CapacityPlan(AuditMixin, Base):
    __tablename__ = "capacity_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    partner_id: Mapped[str] = mapped_column(String(36), ForeignKey("partners.id"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # "2025-03"
    allocated_units: Mapped[int] = mapped_column(Integer, default=0)
    available_units: Mapped[int] = mapped_column(Integer, default=0)
    utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)

    partner: Mapped[Partner] = relationship(back_populates="capacity_plans")


class HomeUnit(AuditMixin, Base):
    __tablename__ = "home_units"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    house_config_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("house_configs.id"), nullable=False
    )
    serial_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    installation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[HomeUnitStatus] = mapped_column(
        Enum(HomeUnitStatus, name="home_unit_status_enum"),
        default=HomeUnitStatus.manufacturing,
    )

    house_config: Mapped[HouseConfig] = relationship(back_populates="home_units")
    telemetry_events: Mapped[list[TelemetryEvent]] = relationship(
        back_populates="home_unit", cascade="all, delete-orphan"
    )


class TelemetryEvent(AuditMixin, Base):
    __tablename__ = "telemetry_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    home_unit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("home_units.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    home_unit: Mapped[HomeUnit] = relationship(back_populates="telemetry_events")


class InsightReport(AuditMixin, Base):
    __tablename__ = "insight_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    report_type: Mapped[str] = mapped_column(String(100), nullable=False)
    parameters_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    results_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
