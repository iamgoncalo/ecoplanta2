"""Factory execution module -- work orders, BOM, inventory, QA."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.factory import (
    BOMDetail,
    BOMLineItem,
    InventoryAlert,
    InventoryItem,
    InventoryListResponse,
    QAListResponse,
    QARecordDetail,
    QASummary,
    StatusHistoryEntry,
    WorkOrderCreate,
    WorkOrderDetail,
    WorkOrderListResponse,
    WorkOrderStatusUpdate,
)

router = APIRouter(prefix="/api/factory", tags=["factory"])

# ── In-memory store for dynamic work order mutations ──────────────────────────

_work_orders_store: list[dict[str, Any]] | None = None


def _get_work_orders_store() -> list[dict[str, Any]]:
    """Return the mutable in-memory work orders list."""
    global _work_orders_store
    if _work_orders_store is None:
        data = get_seed_data()
        _work_orders_store = [dict(wo) for wo in data["work_orders"]]
    return _work_orders_store


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_bom_detail(bom_raw: dict, house_configs: list[dict]) -> BOMDetail:
    """Build a BOMDetail schema from raw seed data."""
    items_json = bom_raw.get("items_json", "[]")
    bom_items_raw = json.loads(items_json) if isinstance(items_json, str) else items_json
    bom_items = [BOMLineItem(**item) for item in bom_items_raw]

    hc_name = None
    for hc in house_configs:
        if hc["id"] == bom_raw.get("house_config_id"):
            hc_name = hc["name"]
            break

    return BOMDetail(
        id=bom_raw["id"],
        house_config_id=bom_raw["house_config_id"],
        house_config_name=hc_name,
        version=bom_raw.get("version", 1),
        items=bom_items,
        total_cost=bom_raw.get("total_cost", 0.0),
        status=bom_raw.get("status", "draft"),
        source=bom_raw.get("source", "synthetic_seeded"),
        source_id=bom_raw.get("source_id"),
    )


def _build_qa_detail(qa_raw: dict) -> QARecordDetail:
    """Build a QARecordDetail from raw seed data."""
    defects_json = qa_raw.get("defects_json", "[]")
    defects = json.loads(defects_json) if isinstance(defects_json, str) else defects_json

    return QARecordDetail(
        id=qa_raw["id"],
        work_order_id=qa_raw["work_order_id"],
        inspector=qa_raw["inspector"],
        result=qa_raw["result"],
        defects=defects,
        notes=qa_raw.get("notes"),
        inspected_at=qa_raw.get("inspected_at"),
        source=qa_raw.get("source", "synthetic_seeded"),
        source_id=qa_raw.get("source_id"),
    )


def _build_work_order_detail(
    wo_raw: dict,
    boms_by_id: dict[str, dict],
    qa_by_wo: dict[str, list[dict]],
    pl_by_id: dict[str, dict],
    house_configs: list[dict],
) -> WorkOrderDetail:
    """Build a full WorkOrderDetail from raw seed data."""
    bom_raw = boms_by_id.get(wo_raw["bom_id"])
    bom_detail = _build_bom_detail(bom_raw, house_configs) if bom_raw else None

    qa_recs = qa_by_wo.get(wo_raw["id"], [])
    qa_details = [_build_qa_detail(qa) for qa in qa_recs]

    pl_raw = pl_by_id.get(wo_raw.get("production_line_id", ""))
    pl_name = pl_raw["name"] if pl_raw else None

    # Build a synthetic status history
    now_iso = datetime.now(UTC).isoformat()
    status_history = [
        StatusHistoryEntry(
            status="planned",
            timestamp=wo_raw.get("created_at") or now_iso,
            note="Work order created",
        )
    ]
    if wo_raw["status"] in ("scheduled", "in_progress", "completed"):
        status_history.append(
            StatusHistoryEntry(
                status="scheduled",
                timestamp=wo_raw.get("scheduled_start") or now_iso,
                note="Scheduled for production",
            )
        )
    if wo_raw["status"] in ("in_progress", "completed"):
        status_history.append(
            StatusHistoryEntry(
                status="in_progress",
                timestamp=wo_raw.get("actual_start") or now_iso,
                note="Production started",
            )
        )
    if wo_raw["status"] == "completed":
        status_history.append(
            StatusHistoryEntry(
                status="completed",
                timestamp=wo_raw.get("actual_end") or now_iso,
                note="Production completed",
            )
        )

    return WorkOrderDetail(
        id=wo_raw["id"],
        bom_id=wo_raw["bom_id"],
        production_line_id=wo_raw.get("production_line_id"),
        production_line_name=pl_name,
        status=wo_raw["status"],
        priority=wo_raw.get("priority", 3),
        scheduled_start=wo_raw.get("scheduled_start"),
        scheduled_end=wo_raw.get("scheduled_end"),
        actual_start=wo_raw.get("actual_start"),
        actual_end=wo_raw.get("actual_end"),
        bom=bom_detail,
        qa_records=qa_details,
        status_history=status_history,
        source=wo_raw.get("source", "synthetic_seeded"),
        source_id=wo_raw.get("source_id"),
    )


def _prepare_indexes() -> tuple[
    dict[str, dict], dict[str, list[dict]], dict[str, dict], list[dict]
]:
    """Prepare lookup indexes from seed data."""
    data = get_seed_data()
    boms_by_id = {b["id"]: b for b in data["boms"]}
    qa_by_wo: dict[str, list[dict]] = {}
    for qa in data["qa_records"]:
        qa_by_wo.setdefault(qa["work_order_id"], []).append(qa)
    pl_by_id = {pl["id"]: pl for pl in data["production_lines"]}
    house_configs = data["house_configs"]
    return boms_by_id, qa_by_wo, pl_by_id, house_configs


# ── GET: list work orders ─────────────────────────────────────────────────────


@router.get("/workorders", response_model=WorkOrderListResponse)
async def list_work_orders(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkOrderListResponse:
    """List all work orders with BOM and QA data."""
    wo_list = _get_work_orders_store()
    boms_by_id, qa_by_wo, pl_by_id, house_configs = _prepare_indexes()

    details = [
        _build_work_order_detail(wo, boms_by_id, qa_by_wo, pl_by_id, house_configs)
        for wo in wo_list
    ]

    by_status: dict[str, int] = {}
    for wo in wo_list:
        by_status[wo["status"]] = by_status.get(wo["status"], 0) + 1

    return WorkOrderListResponse(
        work_orders=details,
        total=len(details),
        by_status=by_status,
    )


# ── GET: single work order detail ─────────────────────────────────────────────


@router.get("/workorders/{work_order_id}", response_model=WorkOrderDetail)
async def get_work_order(
    work_order_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkOrderDetail:
    """Get a single work order with full BOM breakdown and QA records."""
    wo_list = _get_work_orders_store()
    wo_raw = None
    for wo in wo_list:
        if wo["id"] == work_order_id:
            wo_raw = wo
            break

    if wo_raw is None:
        raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")

    boms_by_id, qa_by_wo, pl_by_id, house_configs = _prepare_indexes()
    return _build_work_order_detail(wo_raw, boms_by_id, qa_by_wo, pl_by_id, house_configs)


# ── POST: create work order ──────────────────────────────────────────────────


@router.post("/workorders", response_model=WorkOrderDetail, status_code=201)
async def create_work_order(
    body: WorkOrderCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkOrderDetail:
    """Create a new work order from a BOM."""
    data = get_seed_data()
    boms_by_id = {b["id"]: b for b in data["boms"]}

    if body.bom_id not in boms_by_id:
        raise HTTPException(status_code=404, detail=f"BOM {body.bom_id} not found")

    now = datetime.now(UTC).isoformat()
    wo = {
        "id": str(uuid.uuid4()),
        "bom_id": body.bom_id,
        "production_line_id": body.production_line_id,
        "status": "planned",
        "priority": body.priority,
        "scheduled_start": body.scheduled_start,
        "scheduled_end": body.scheduled_end,
        "actual_start": None,
        "actual_end": None,
        "source": "synthetic_seeded",
        "source_id": "api-created",
        "created_at": now,
        "updated_at": now,
    }
    _get_work_orders_store().append(wo)

    boms_by_id_full, qa_by_wo, pl_by_id, house_configs = _prepare_indexes()
    return _build_work_order_detail(wo, boms_by_id_full, qa_by_wo, pl_by_id, house_configs)


# ── PATCH: update work order status ──────────────────────────────────────────


@router.patch("/workorders/{work_order_id}/status", response_model=WorkOrderDetail)
async def update_work_order_status(
    work_order_id: str,
    body: WorkOrderStatusUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> WorkOrderDetail:
    """Update a work order's status."""
    valid_statuses = {
        "planned",
        "scheduled",
        "in_progress",
        "quality_check",
        "completed",
        "on_hold",
    }
    if body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status: {body.status}")

    wo_list = _get_work_orders_store()
    for wo in wo_list:
        if wo["id"] == work_order_id:
            wo["status"] = body.status
            wo["updated_at"] = datetime.now(UTC).isoformat()
            if body.status == "in_progress" and wo.get("actual_start") is None:
                wo["actual_start"] = datetime.now(UTC).isoformat()
            if body.status == "completed":
                wo["actual_end"] = datetime.now(UTC).isoformat()

            boms_by_id, qa_by_wo, pl_by_id, house_configs = _prepare_indexes()
            return _build_work_order_detail(wo, boms_by_id, qa_by_wo, pl_by_id, house_configs)

    raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")


# ── GET: inventory ───────────────────────────────────────────────────────────


@router.get("/inventory", response_model=InventoryListResponse)
async def list_inventory(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> InventoryListResponse:
    """Current inventory with stock levels and reorder alerts."""
    data = get_seed_data()
    inv_raw = data["inventory_items"]
    materials_by_id = {m["id"]: m for m in data["materials"]}

    items: list[InventoryItem] = []
    alerts: list[InventoryAlert] = []

    for inv in inv_raw:
        mat = materials_by_id.get(inv["material_id"])
        mat_name = mat["name"] if mat else "Unknown"
        reorder = inv["quantity"] < inv["min_stock"]

        items.append(
            InventoryItem(
                id=inv["id"],
                material_id=inv["material_id"],
                material_name=mat_name,
                warehouse=inv["warehouse"],
                quantity=inv["quantity"],
                unit=inv["unit"],
                min_stock=inv["min_stock"],
                max_stock=inv["max_stock"],
                reorder_needed=reorder,
                source=inv.get("source", "synthetic_seeded"),
                source_id=inv.get("source_id"),
            )
        )

        if reorder:
            alerts.append(
                InventoryAlert(
                    material=mat_name,
                    material_id=inv["material_id"],
                    current_stock=inv["quantity"],
                    min_stock=inv["min_stock"],
                    reorder_needed=True,
                )
            )

    return InventoryListResponse(
        items=items,
        total=len(items),
        alerts=alerts,
        total_alerts=len(alerts),
    )


# ── GET: QA records ──────────────────────────────────────────────────────────


@router.get("/qa", response_model=QAListResponse)
async def list_qa_records(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> QAListResponse:
    """QA records with pass/fail rates and defect summary."""
    data = get_seed_data()
    qa_raw = data["qa_records"]

    records = [_build_qa_detail(qa) for qa in qa_raw]

    total = len(records)
    pass_count = sum(1 for r in records if r.result == "pass")
    fail_count = total - pass_count

    # Collect common defect types
    defect_types: dict[str, int] = {}
    for r in records:
        for d in r.defects:
            dtype = d.get("type", "unknown")
            defect_types[dtype] = defect_types.get(dtype, 0) + 1
    common_defects = sorted(defect_types.keys(), key=lambda k: defect_types[k], reverse=True)

    summary = QASummary(
        total_inspections=total,
        pass_rate=round(pass_count / total * 100, 1) if total > 0 else 0.0,
        fail_rate=round(fail_count / total * 100, 1) if total > 0 else 0.0,
        common_defects=common_defects[:5],
    )

    return QAListResponse(records=records, summary=summary)


# ── GET: BOM detail ──────────────────────────────────────────────────────────


@router.get("/bom/{bom_id}", response_model=BOMDetail)
async def get_bom_detail(
    bom_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> BOMDetail:
    """BOM details with materials, costs, and lead times."""
    data = get_seed_data()
    house_configs = data["house_configs"]

    for bom in data["boms"]:
        if bom["id"] == bom_id:
            return _build_bom_detail(bom, house_configs)

    raise HTTPException(status_code=404, detail=f"BOM {bom_id} not found")
