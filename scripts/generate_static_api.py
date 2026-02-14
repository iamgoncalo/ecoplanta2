#!/usr/bin/env python3
"""Generate static JSON files for GitHub Pages preview mode.

Uses the existing SeedGenerator to produce deterministic data that matches
the exact response shapes of the real API endpoints.

Usage:
    python scripts/generate_static_api.py

Environment:
    SEED  -- random seed (default 42)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Add the backend package to sys.path so we can import from app.*
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.seed.generator import SeedGenerator  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEED = int(os.environ.get("SEED", "42"))
OUTPUT_DIR = REPO_ROOT / "frontend" / "public" / "api"


# ---------------------------------------------------------------------------
# JSON serialisation helper
# ---------------------------------------------------------------------------
def _json_serializer(obj: Any) -> Any:
    """Handle datetime / date objects for json.dumps."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _write_json(filename: str, data: Any) -> None:
    """Write *data* as pretty-printed JSON to OUTPUT_DIR/filename."""
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=_json_serializer, ensure_ascii=False)
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Builders -- each mirrors the corresponding route handler
# ---------------------------------------------------------------------------


def build_health() -> dict[str, Any]:
    """GET /api/health -- static version always reports disconnected."""
    return {
        "status": "ok",
        "db_connected": False,
        "redis_connected": False,
        "version": "0.1.0",
    }


def build_fabric(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/fabric -- production lines with work-order summary."""
    lines = data["production_lines"]
    work_orders = data["work_orders"]

    fabric_items: list[dict[str, Any]] = []
    for pl in lines:
        wo_for_line = [wo for wo in work_orders if wo.get("production_line_id") == pl["id"]]
        active = sum(1 for wo in wo_for_line if wo["status"] in ("in_progress", "scheduled"))
        fabric_items.append(
            {
                "id": pl["id"],
                "name": pl["name"],
                "location": pl["location"],
                "capacity_units_per_day": pl["capacity_units_per_day"],
                "status": pl["status"],
                "current_workorder_id": pl.get("current_workorder_id"),
                "active_work_orders": active,
                "total_work_orders": len(wo_for_line),
                "source": pl.get("source", "synthetic_seeded"),
                "source_id": pl.get("source_id"),
                "created_at": pl.get("created_at"),
                "updated_at": pl.get("updated_at"),
            }
        )

    running = sum(1 for item in fabric_items if item["status"] == "running")

    return {
        "production_lines": fabric_items,
        "total_lines": len(fabric_items),
        "lines_running": running,
        "total_work_orders": len(work_orders),
    }


def build_fabric_scene(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/fabric/scene -- 3D scene objects for factory layout."""
    scene = data["factory_scene"]

    objects: list[dict[str, Any]] = []
    for obj in scene["objects"]:
        objects.append(
            {
                "id": obj["id"],
                "name": obj["name"],
                "type": obj["type"],
                "position": {"x": obj["position"]["x"], "y": obj["position"]["y"], "z": obj["position"]["z"]},
                "rotation": {"x": obj["rotation"]["x"], "y": obj["rotation"]["y"], "z": obj["rotation"]["z"]},
                "scale": {"x": obj["scale"]["x"], "y": obj["scale"]["y"], "z": obj["scale"]["z"]},
                "color": obj["color"],
                "metadata": obj.get("metadata"),
            }
        )

    cam = scene["camera"]
    camera = {
        "position": {"x": cam["position"]["x"], "y": cam["position"]["y"], "z": cam["position"]["z"]},
        "target": {"x": cam["target"]["x"], "y": cam["target"]["y"], "z": cam["target"]["z"]},
        "fov": cam.get("fov", 60.0),
    }

    return {"objects": objects, "camera": camera}


def build_frameworks(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/frameworks -- frameworks with related materials and patents."""
    frameworks_raw = data["frameworks"]
    materials_raw = data["materials"]
    patents_raw = data["patents"]

    # Build material summaries
    material_summaries: list[dict[str, Any]] = [
        {
            "id": m["id"],
            "name": m["name"],
            "category": m["category"],
            "grade": m["grade"],
            "is_smart_material": m["is_smart_material"],
            "tensile_strength": m["tensile_strength"],
            "embodied_carbon_kg": m["embodied_carbon_kg"],
            "source": m.get("source", "synthetic_seeded"),
            "source_id": m.get("source_id"),
            "created_at": m.get("created_at"),
            "updated_at": m.get("updated_at"),
        }
        for m in materials_raw
    ]

    # Build patent summaries
    patent_summaries: list[dict[str, Any]] = [
        {
            "id": p["id"],
            "title": p["title"],
            "filing_number": p["filing_number"],
            "status": p["status"],
            "filing_date": p.get("filing_date"),
            "source": p.get("source", "synthetic_seeded"),
            "source_id": p.get("source_id"),
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at"),
        }
        for p in patents_raw
    ]

    framework_items: list[dict[str, Any]] = []
    for idx, fw in enumerate(frameworks_raw):
        # Same slicing logic as the route handler
        fw_materials = material_summaries[idx * 3 : idx * 3 + 3]
        fw_patents = patent_summaries[idx : idx + 2]

        framework_items.append(
            {
                "id": fw["id"],
                "name": fw["name"],
                "framework_type": fw["framework_type"],
                "description": fw.get("description"),
                "structural_rating": fw["structural_rating"],
                "materials": fw_materials,
                "patents": fw_patents,
                "source": fw.get("source", "synthetic_seeded"),
                "source_id": fw.get("source_id"),
                "created_at": fw.get("created_at"),
                "updated_at": fw.get("updated_at"),
            }
        )

    return {
        "frameworks": framework_items,
        "total_frameworks": len(framework_items),
        "total_materials": len(materials_raw),
        "total_patents": len(patents_raw),
    }


def build_sales(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/sales -- leads with opportunities and pipeline stats."""
    leads_raw = data["leads"]
    opps_raw = data["opportunities"]

    # Index opportunities by lead_id
    opps_by_lead: dict[str, list[dict[str, Any]]] = {}
    for opp in opps_raw:
        opps_by_lead.setdefault(opp["lead_id"], []).append(opp)

    lead_items: list[dict[str, Any]] = []
    for ld in leads_raw:
        lead_opps = opps_by_lead.get(ld["id"], [])
        opp_summaries = [
            {
                "id": o["id"],
                "title": o["title"],
                "value": o["value"],
                "stage": o["stage"],
                "probability": o["probability"],
                "source": o.get("source", "synthetic_seeded"),
                "source_id": o.get("source_id"),
                "created_at": o.get("created_at"),
                "updated_at": o.get("updated_at"),
            }
            for o in lead_opps
        ]
        lead_items.append(
            {
                "id": ld["id"],
                "name": ld["name"],
                "email": ld["email"],
                "company": ld.get("company"),
                "status": ld["status"],
                "score": ld["score"],
                "opportunities": opp_summaries,
                "source": ld.get("source", "synthetic_seeded"),
                "source_id": ld.get("source_id"),
                "created_at": ld.get("created_at"),
                "updated_at": ld.get("updated_at"),
            }
        )

    # Pipeline stats
    total_value = sum(o["value"] for o in opps_raw)
    weighted_value = sum(o["value"] * o["probability"] for o in opps_raw)
    qualified = sum(
        1 for ld in leads_raw if ld["status"] in ("qualified", "proposal", "negotiation", "won")
    )
    avg_deal = total_value / len(opps_raw) if opps_raw else 0.0

    pipeline = {
        "total_leads": len(leads_raw),
        "qualified_leads": qualified,
        "total_pipeline_value": round(total_value, 2),
        "weighted_pipeline_value": round(weighted_value, 2),
        "avg_deal_size": round(avg_deal, 2),
    }

    return {"leads": lead_items, "pipeline": pipeline}


def build_intelligence(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/intelligence -- insight reports and analytics."""
    reports_raw = data["insight_reports"]

    insights: list[dict[str, Any]] = []
    for rpt in reports_raw:
        params = rpt.get("parameters_json")
        results = rpt.get("results_json")
        insights.append(
            {
                "id": rpt["id"],
                "title": rpt["title"],
                "module": rpt["module"],
                "report_type": rpt["report_type"],
                "parameters": json.loads(params) if isinstance(params, str) else params,
                "results": json.loads(results) if isinstance(results, str) else results,
                "generated_at": rpt.get("generated_at"),
                "source": rpt.get("source", "synthetic_seeded"),
                "source_id": rpt.get("source_id"),
                "created_at": rpt.get("created_at"),
                "updated_at": rpt.get("updated_at"),
            }
        )

    return {
        "insights": insights,
        "total_insights": len(insights),
    }


def build_deploy(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/deploy -- deliveries with deployment jobs."""
    deliveries_raw = data["deliveries"]
    jobs_raw = data["deployment_jobs"]

    # Index deployment jobs by delivery_id
    jobs_by_delivery: dict[str, list[dict[str, Any]]] = {}
    for job in jobs_raw:
        jobs_by_delivery.setdefault(job["delivery_id"], []).append(job)

    deploy_items: list[dict[str, Any]] = []
    for dlv in deliveries_raw:
        dlv_jobs = jobs_by_delivery.get(dlv["id"], [])
        job_summaries = [
            {
                "id": j["id"],
                "site_address": j["site_address"],
                "status": j["status"],
                "commissioning_date": j.get("commissioning_date"),
                "crew_lead": j.get("crew_lead"),
                "source": j.get("source", "synthetic_seeded"),
                "source_id": j.get("source_id"),
                "created_at": j.get("created_at"),
                "updated_at": j.get("updated_at"),
            }
            for j in dlv_jobs
        ]
        deploy_items.append(
            {
                "id": dlv["id"],
                "origin": dlv["origin"],
                "destination": dlv["destination"],
                "carrier": dlv["carrier"],
                "status": dlv["status"],
                "estimated_arrival": dlv.get("estimated_arrival"),
                "actual_arrival": dlv.get("actual_arrival"),
                "deployment_jobs": job_summaries,
                "source": dlv.get("source", "synthetic_seeded"),
                "source_id": dlv.get("source_id"),
                "created_at": dlv.get("created_at"),
                "updated_at": dlv.get("updated_at"),
            }
        )

    in_transit = sum(1 for d in deploy_items if d["status"] == "in_transit")
    delivered = sum(1 for d in deploy_items if d["status"] == "delivered")

    return {
        "deliveries": deploy_items,
        "total_deliveries": len(deploy_items),
        "in_transit": in_transit,
        "delivered": delivered,
    }


def build_partners(data: dict[str, Any]) -> dict[str, Any]:
    """GET /api/partners -- partners with capacity plans and utilisation stats."""
    partners_raw = data["partners"]
    plans_raw = data["capacity_plans"]

    # Index capacity plans by partner_id
    plans_by_partner: dict[str, list[dict[str, Any]]] = {}
    for plan in plans_raw:
        plans_by_partner.setdefault(plan["partner_id"], []).append(plan)

    partner_items: list[dict[str, Any]] = []
    for p in partners_raw:
        p_plans = plans_by_partner.get(p["id"], [])
        plan_summaries = [
            {
                "id": cp["id"],
                "month": cp["month"],
                "allocated_units": cp["allocated_units"],
                "available_units": cp["available_units"],
                "utilization_pct": cp["utilization_pct"],
                "source": cp.get("source", "synthetic_seeded"),
                "source_id": cp.get("source_id"),
                "created_at": cp.get("created_at"),
                "updated_at": cp.get("updated_at"),
            }
            for cp in p_plans
        ]
        partner_items.append(
            {
                "id": p["id"],
                "name": p["name"],
                "country": p["country"],
                "region": p["region"],
                "capacity_units_per_month": p["capacity_units_per_month"],
                "contact_email": p.get("contact_email"),
                "rating": p["rating"],
                "lead_time_days": p["lead_time_days"],
                "capacity_plans": plan_summaries,
                "source": p.get("source", "synthetic_seeded"),
                "source_id": p.get("source_id"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
            }
        )

    total_cap = sum(p["capacity_units_per_month"] for p in partner_items)
    all_util = [cp["utilization_pct"] for cp in plans_raw]
    avg_util = round(sum(all_util) / len(all_util), 1) if all_util else 0.0

    return {
        "partners": partner_items,
        "total_partners": len(partner_items),
        "total_capacity": total_cap,
        "avg_utilization": avg_util,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print(f"Generating static API JSON files (SEED={SEED}) ...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gen = SeedGenerator(seed=SEED)
    data = gen.generate_all()

    _write_json("health.json", build_health())
    _write_json("fabric.json", build_fabric(data))
    _write_json("fabric-scene.json", build_fabric_scene(data))
    _write_json("frameworks.json", build_frameworks(data))
    _write_json("sales.json", build_sales(data))
    _write_json("intelligence.json", build_intelligence(data))
    _write_json("deploy.json", build_deploy(data))
    _write_json("partners.json", build_partners(data))

    print("Done.")


if __name__ == "__main__":
    main()
