"""Fabric module -- production lines, work orders, 3D factory scene."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_seed_data
from app.schemas.modules import (
    CameraDefaults,
    FabricItem,
    FabricListResponse,
    SceneObject,
    SceneResponse,
    Vec3,
)

router = APIRouter(prefix="/api/fabric", tags=["fabric"])


@router.get("", response_model=FabricListResponse)
async def list_fabric(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> FabricListResponse:
    """List production lines and work-order summary.

    Falls back to seed data when the database is empty or unavailable.
    """
    data = get_seed_data()
    lines = data["production_lines"]
    work_orders = data["work_orders"]

    fabric_items: list[FabricItem] = []
    for pl in lines:
        wo_for_line = [wo for wo in work_orders if wo.get("production_line_id") == pl["id"]]
        active = sum(1 for wo in wo_for_line if wo["status"] in ("in_progress", "scheduled"))
        fabric_items.append(
            FabricItem(
                id=pl["id"],
                name=pl["name"],
                location=pl["location"],
                capacity_units_per_day=pl["capacity_units_per_day"],
                status=pl["status"],
                current_workorder_id=pl.get("current_workorder_id"),
                active_work_orders=active,
                total_work_orders=len(wo_for_line),
                source=pl.get("source", "synthetic_seeded"),
                source_id=pl.get("source_id"),
            )
        )

    running = sum(1 for item in fabric_items if item.status == "running")

    return FabricListResponse(
        production_lines=fabric_items,
        total_lines=len(fabric_items),
        lines_running=running,
        total_work_orders=len(work_orders),
    )


@router.get("/scene", response_model=SceneResponse)
async def get_factory_scene(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SceneResponse:
    """Return 3D scene objects for the factory layout visualisation."""
    data = get_seed_data()
    scene = data["factory_scene"]

    objects = [
        SceneObject(
            id=obj["id"],
            name=obj["name"],
            type=obj["type"],
            position=Vec3(**obj["position"]),
            rotation=Vec3(**obj["rotation"]),
            scale=Vec3(**obj["scale"]),
            color=obj["color"],
            metadata=obj.get("metadata"),
        )
        for obj in scene["objects"]
    ]
    cam = scene["camera"]
    camera = CameraDefaults(
        position=Vec3(**cam["position"]),
        target=Vec3(**cam["target"]),
        fov=cam.get("fov", 60.0),
    )
    return SceneResponse(objects=objects, camera=camera)
