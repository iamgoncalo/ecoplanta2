"""Deploy module -- deliveries and deployment jobs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    DeployItem,
    DeployListResponse,
    DeploymentJobSummary,
)

router = APIRouter(prefix="/api/deploy", tags=["deploy"])


@router.get("", response_model=DeployListResponse)
async def list_deploy(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> DeployListResponse:
    """List deliveries with their deployment jobs.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    deliveries_raw = data["deliveries"]
    jobs_raw = data["deployment_jobs"]

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
