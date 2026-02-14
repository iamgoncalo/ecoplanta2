"""Deploy module -- deliveries, deployment jobs, schedule, commissioning."""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from datetime import UTC, date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_seed_data
from app.schemas.deploy import (
    ChecklistItem,
    ChecklistUpdate,
    CommissioningOverview,
    DeliveryCreate,
    DeliveryResponse,
    DeliveryScheduleDelivery,
    DeliveryScheduleInstallation,
    DeliveryScheduleItem,
    DeliveryScheduleResponse,
    DeliveryStatusUpdate,
    DeploymentJobDetail,
    InstallationChecklist,
)
from app.schemas.modules import (
    DeployItem,
    DeployListResponse,
    DeploymentJobSummary,
)

router = APIRouter(prefix="/api/deploy", tags=["deploy"])

# ── In-memory stores ─────────────────────────────────────────────────────────

_deliveries_store: list[dict[str, Any]] | None = None
_jobs_store: list[dict[str, Any]] | None = None


def _get_deliveries_store() -> list[dict[str, Any]]:
    """Return the mutable in-memory deliveries list."""
    global _deliveries_store
    if _deliveries_store is None:
        data = get_seed_data()
        _deliveries_store = [dict(d) for d in data["deliveries"]]
    return _deliveries_store


def _get_jobs_store() -> list[dict[str, Any]]:
    """Return the mutable in-memory deployment jobs list."""
    global _jobs_store
    if _jobs_store is None:
        data = get_seed_data()
        _jobs_store = [dict(j) for j in data["deployment_jobs"]]
    return _jobs_store


# ── Checklist helpers ─────────────────────────────────────────────────────────

_CHECKLIST_LABELS = {
    "foundation_check": "Foundation Check",
    "utility_connections": "Utility Connections",
    "module_alignment": "Module Alignment",
    "smart_system_boot": "Smart System Boot",
    "final_inspection": "Final Inspection",
}


def _parse_checklist(job_raw: dict) -> InstallationChecklist:
    """Parse a deployment job's checklist JSON into structured form."""
    cl_json = job_raw.get("installation_checklist_json", "{}")
    cl_data = json.loads(cl_json) if isinstance(cl_json, str) else cl_json

    items = []
    for key, label in _CHECKLIST_LABELS.items():
        items.append(
            ChecklistItem(
                key=key,
                label=label,
                completed=cl_data.get(key, False),
            )
        )

    completed = sum(1 for i in items if i.completed)
    total = len(items)
    pct = round(completed / total * 100, 1) if total > 0 else 0.0

    return InstallationChecklist(
        job_id=job_raw["id"],
        items=items,
        completed_count=completed,
        total_count=total,
        completion_pct=pct,
    )


# ── GET: existing list endpoint (unchanged contract) ──────────────────────────


@router.get("", response_model=DeployListResponse)
async def list_deploy(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeployListResponse:
    """List deliveries with their deployment jobs.

    Falls back to seed data when the database is empty or unavailable.
    """
    deliveries_raw = _get_deliveries_store()
    jobs_raw = _get_jobs_store()

    # Index deployment jobs by delivery_id
    jobs_by_delivery: dict[str, list[dict]] = {}
    for job in jobs_raw:
        jobs_by_delivery.setdefault(job["delivery_id"], []).append(job)

    deploy_items: list[DeployItem] = []
    for dlv in deliveries_raw:
        dlv_jobs = jobs_by_delivery.get(dlv["id"], [])
        job_summaries = [
            DeploymentJobSummary(
                id=j["id"],
                site_address=j["site_address"],
                status=j["status"],
                commissioning_date=j.get("commissioning_date"),
                crew_lead=j.get("crew_lead"),
                source=j.get("source", "synthetic_seeded"),
                source_id=j.get("source_id"),
            )
            for j in dlv_jobs
        ]
        deploy_items.append(
            DeployItem(
                id=dlv["id"],
                origin=dlv["origin"],
                destination=dlv["destination"],
                carrier=dlv["carrier"],
                status=dlv["status"],
                estimated_arrival=dlv.get("estimated_arrival"),
                actual_arrival=dlv.get("actual_arrival"),
                deployment_jobs=job_summaries,
                source=dlv.get("source", "synthetic_seeded"),
                source_id=dlv.get("source_id"),
            )
        )

    in_transit = sum(1 for d in deploy_items if d.status == "in_transit")
    delivered = sum(1 for d in deploy_items if d.status == "delivered")

    return DeployListResponse(
        deliveries=deploy_items,
        total_deliveries=len(deploy_items),
        in_transit=in_transit,
        delivered=delivered,
    )


# ── GET: delivery schedule (calendar view) ────────────────────────────────────


@router.get("/schedule", response_model=DeliveryScheduleResponse)
async def delivery_schedule(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeliveryScheduleResponse:
    """Delivery schedule calendar view grouped by date."""
    deliveries_raw = _get_deliveries_store()
    jobs_raw = _get_jobs_store()

    # Group deliveries by estimated arrival date
    deliveries_by_date: dict[date, list[dict]] = defaultdict(list)
    for dlv in deliveries_raw:
        est = dlv.get("estimated_arrival")
        if est:
            try:
                dt = datetime.fromisoformat(est) if isinstance(est, str) else est
                d = dt.date() if isinstance(dt, datetime) else dt
                deliveries_by_date[d].append(dlv)
            except (ValueError, AttributeError):
                pass

    # Group jobs by commissioning date
    jobs_by_date: dict[date, list[dict]] = defaultdict(list)
    for job in jobs_raw:
        cd = job.get("commissioning_date")
        if cd:
            try:
                d = date.fromisoformat(cd) if isinstance(cd, str) else cd
                jobs_by_date[d].append(job)
            except (ValueError, AttributeError):
                pass

    all_dates = sorted(set(list(deliveries_by_date.keys()) + list(jobs_by_date.keys())))

    schedule_items: list[DeliveryScheduleItem] = []
    total_deliveries = 0
    total_installations = 0

    for d in all_dates:
        day_deliveries = [
            DeliveryScheduleDelivery(
                id=dlv["id"],
                destination=dlv["destination"],
                status=dlv["status"],
                carrier=dlv["carrier"],
            )
            for dlv in deliveries_by_date.get(d, [])
        ]
        day_installations = [
            DeliveryScheduleInstallation(
                id=job["id"],
                site_address=job["site_address"],
                status=job["status"],
                crew_lead=job.get("crew_lead"),
            )
            for job in jobs_by_date.get(d, [])
        ]
        total_deliveries += len(day_deliveries)
        total_installations += len(day_installations)

        schedule_items.append(
            DeliveryScheduleItem(
                date=d,
                deliveries=day_deliveries,
                installations=day_installations,
                delivery_count=len(day_deliveries),
                installation_count=len(day_installations),
            )
        )

    return DeliveryScheduleResponse(
        schedule=schedule_items,
        total_days=len(schedule_items),
        total_deliveries=total_deliveries,
        total_installations=total_installations,
    )


# ── POST: create delivery ────────────────────────────────────────────────────


@router.post("/deliveries", response_model=DeliveryResponse, status_code=201)
async def create_delivery(
    body: DeliveryCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeliveryResponse:
    """Create a new delivery for a completed work order."""
    now = datetime.now(UTC).isoformat()
    delivery = {
        "id": str(uuid.uuid4()),
        "work_order_id": body.work_order_id,
        "origin": "Figueira da Foz, Portugal",
        "destination": body.destination,
        "carrier": body.carrier or "Transporte Modular EU",
        "status": "preparing",
        "estimated_arrival": body.estimated_arrival,
        "actual_arrival": None,
        "source": "synthetic_seeded",
        "source_id": "api-created",
        "created_at": now,
        "updated_at": now,
    }
    _get_deliveries_store().append(delivery)
    return DeliveryResponse.model_validate(delivery)


# ── PATCH: update delivery status ─────────────────────────────────────────────


@router.patch("/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
async def update_delivery_status(
    delivery_id: str,
    body: DeliveryStatusUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeliveryResponse:
    """Update a delivery's status."""
    valid = {"preparing", "in_transit", "delivered", "delayed"}
    if body.status not in valid:
        raise HTTPException(status_code=422, detail=f"Invalid status: {body.status}")

    deliveries = _get_deliveries_store()
    for dlv in deliveries:
        if dlv["id"] == delivery_id:
            dlv["status"] = body.status
            dlv["updated_at"] = datetime.now(UTC).isoformat()
            if body.status == "delivered" and dlv.get("actual_arrival") is None:
                dlv["actual_arrival"] = datetime.now(UTC).isoformat()
            return DeliveryResponse(**dlv)

    raise HTTPException(status_code=404, detail=f"Delivery {delivery_id} not found")


# ── GET: deployment job detail ────────────────────────────────────────────────


@router.get("/jobs/{job_id}", response_model=DeploymentJobDetail)
async def get_deployment_job(
    job_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeploymentJobDetail:
    """Get deployment job details with installation checklist."""
    jobs = _get_jobs_store()
    for job in jobs:
        if job["id"] == job_id:
            checklist = _parse_checklist(job)
            return DeploymentJobDetail(
                id=job["id"],
                delivery_id=job["delivery_id"],
                site_address=job["site_address"],
                status=job["status"],
                commissioning_date=job.get("commissioning_date"),
                crew_lead=job.get("crew_lead"),
                checklist=checklist,
                source=job.get("source", "synthetic_seeded"),
                source_id=job.get("source_id"),
            )

    raise HTTPException(status_code=404, detail=f"Deployment job {job_id} not found")


# ── PATCH: update checklist items ─────────────────────────────────────────────


@router.patch("/jobs/{job_id}/checklist", response_model=DeploymentJobDetail)
async def update_checklist(
    job_id: str,
    body: ChecklistUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeploymentJobDetail:
    """Update installation checklist items for a deployment job."""
    jobs = _get_jobs_store()
    for job in jobs:
        if job["id"] == job_id:
            cl_json = job.get("installation_checklist_json", "{}")
            cl_data = json.loads(cl_json) if isinstance(cl_json, str) else cl_json

            for key, value in body.items.items():
                if key in _CHECKLIST_LABELS:
                    cl_data[key] = value

            job["installation_checklist_json"] = json.dumps(cl_data)
            job["updated_at"] = datetime.now(UTC).isoformat()

            checklist = _parse_checklist(job)
            return DeploymentJobDetail(
                id=job["id"],
                delivery_id=job["delivery_id"],
                site_address=job["site_address"],
                status=job["status"],
                commissioning_date=job.get("commissioning_date"),
                crew_lead=job.get("crew_lead"),
                checklist=checklist,
                source=job.get("source", "synthetic_seeded"),
                source_id=job.get("source_id"),
            )

    raise HTTPException(status_code=404, detail=f"Deployment job {job_id} not found")


# ── GET: commissioning overview ───────────────────────────────────────────────


@router.get("/commissioning", response_model=CommissioningOverview)
async def commissioning_overview(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CommissioningOverview:
    """Commissioning status overview across all deployment jobs."""
    jobs = _get_jobs_store()

    total = len(jobs)
    completed = sum(1 for j in jobs if j["status"] == "completed")
    in_progress = sum(1 for j in jobs if j["status"] in ("installing", "commissioning"))
    pending = sum(1 for j in jobs if j["status"] in ("planned", "site_prep"))
    issues = sum(1 for j in jobs if j["status"] == "on_hold")

    return CommissioningOverview(
        total=total,
        pending=pending,
        in_progress=in_progress,
        completed=completed,
        issues=issues,
    )
