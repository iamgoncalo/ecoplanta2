#!/usr/bin/env python3
"""Generate static JSON files for GitHub Pages preview mode.

Produces deterministic data that matches the exact TypeScript interfaces
used by the frontend components (not the backend API shapes).

Usage:
    python scripts/generate_static_api.py

Environment:
    SEED  -- random seed (default 42)
"""

from __future__ import annotations

import json
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

SEED = int(os.environ.get("SEED", "42"))
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "frontend" / "public" / "api"

random.seed(SEED)


def _uid() -> str:
    return str(uuid4())


def _json_serializer(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _write_json(filename: str, data: Any) -> None:
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=_json_serializer, ensure_ascii=False)
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# health.json
# ---------------------------------------------------------------------------
def build_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "db_connected": False,
        "redis_connected": False,
        "version": "0.1.0",
    }


# ---------------------------------------------------------------------------
# fabric.json  - matches FabricResponse TypeScript interface
# ---------------------------------------------------------------------------
def build_fabric() -> dict[str, Any]:
    statuses = ["running", "idle", "maintenance", "running", "running"]
    products = [
        "EcoContainer 20ft",
        "EcoContainer 40ft",
        "Planta Module A",
        "Planta Module B",
        "EcoContainer HQ",
    ]
    lines = []
    for i in range(5):
        eff = round(random.uniform(72, 98), 1)
        lines.append({
            "id": _uid(),
            "name": f"Line {chr(65 + i)}",
            "status": statuses[i],
            "throughput": random.randint(40, 120),
            "efficiency": eff,
            "product": products[i],
        })

    priorities = ["high", "medium", "low"]
    wo_statuses = ["in_progress", "scheduled", "completed", "in_progress", "scheduled",
                   "completed", "in_progress", "scheduled"]
    orders = []
    for i in range(8):
        orders.append({
            "id": _uid(),
            "product": random.choice(products),
            "quantity": random.randint(2, 50),
            "status": wo_statuses[i],
            "due_date": (date.today() + timedelta(days=random.randint(3, 45))).isoformat(),
            "priority": random.choice(priorities),
        })

    running = sum(1 for l in lines if l["status"] == "running")
    avg_eff = round(sum(l["efficiency"] for l in lines) / len(lines), 1)
    total_tp = sum(l["throughput"] for l in lines)
    open_orders = sum(1 for o in orders if o["status"] != "completed")

    return {
        "production_lines": lines,
        "work_orders": orders,
        "metrics": {
            "active_lines": running,
            "avg_efficiency": avg_eff,
            "total_throughput": total_tp,
            "open_orders": open_orders,
            "lines_change": 1,
            "efficiency_change": 2.3,
        },
    }


# ---------------------------------------------------------------------------
# fabric-scene.json - matches SceneObject[] (position/scale as tuples)
# ---------------------------------------------------------------------------
def build_fabric_scene() -> dict[str, Any]:
    types = ["box", "cylinder", "box", "box", "cylinder", "box", "box"]
    names = [
        "Assembly Station A",
        "Welding Robot 1",
        "Material Storage",
        "Quality Control",
        "Paint Booth",
        "CNC Mill",
        "Packaging Bay",
    ]
    colors = ["#3b82f6", "#ef4444", "#22c55e", "#eab308", "#8b5cf6", "#06b6d4", "#f97316"]

    objects = []
    for i, (tp, nm, col) in enumerate(zip(types, names, colors)):
        x = (i % 4) * 3.0 - 4.5
        z = (i // 4) * 4.0 - 2.0
        sy = round(random.uniform(0.8, 2.5), 1)
        objects.append({
            "id": _uid(),
            "type": tp,
            "name": nm,
            "position": [round(x, 1), round(sy / 2, 1), round(z, 1)],
            "scale": [round(random.uniform(1.0, 2.0), 1), sy, round(random.uniform(1.0, 2.0), 1)],
            "color": col,
            "metadata": {"zone": f"Zone {chr(65 + i)}", "capacity": random.randint(50, 200)},
        })

    return {"objects": objects}


# ---------------------------------------------------------------------------
# frameworks.json - matches FrameworksResponse
# ---------------------------------------------------------------------------
def build_frameworks() -> dict[str, Any]:
    fw_names = [
        "EcoFrame Premium",
        "Planta Structural Core",
        "HQ Steel Composite",
        "Smart Thermal Shell",
        "Bio-Composite Frame",
        "Nano-Enhanced Panel",
    ]
    fw_types = ["modular", "structural", "composite", "thermal", "bio", "nano"]
    fw_materials_list = [
        "High-Grade Steel",
        "Reinforced Concrete",
        "Carbon Fiber Composite",
        "Smart Glass",
        "Hemp Bio-Composite",
        "Graphene-Enhanced Polymer",
    ]
    fw_descs = [
        "Premium modular framework for rapid container assembly with superior load-bearing.",
        "Core structural system for Planta Smart Homes with integrated sensor mounting.",
        "High-quality steel and composite hybrid for headquarters-grade installations.",
        "Thermally adaptive shell with embedded smart material responses.",
        "Sustainable bio-composite framework using hemp fiber reinforcement.",
        "Next-generation nano-enhanced panels with self-healing properties.",
    ]

    frameworks = []
    for i in range(6):
        frameworks.append({
            "id": _uid(),
            "name": fw_names[i],
            "type": fw_types[i],
            "structural_rating": random.randint(6, 10),
            "material": fw_materials_list[i],
            "smart_enabled": i >= 3,
            "description": fw_descs[i],
        })

    mat_categories = ["steel", "composite", "insulation", "concrete", "polymer", "glass",
                      "bio-composite", "nano-material"]
    mat_grades = ["A+", "A", "B+", "B", "A+", "A", "A+", "A+"]
    mat_names = [
        "High-Tensile Steel S355",
        "Carbon Fiber Reinforced Polymer",
        "Aerogel Insulation Panel",
        "Ultra-High Performance Concrete",
        "Recycled HDPE Composite",
        "Low-E Smart Glass",
        "Hemp-Lime Bio Panel",
        "Graphene Oxide Coating",
    ]

    materials = []
    for i in range(8):
        is_smart = i in [2, 5, 7]
        materials.append({
            "id": _uid(),
            "name": mat_names[i],
            "category": mat_categories[i],
            "grade": mat_grades[i],
            "properties": {
                "density": round(random.uniform(1.5, 8.0), 2),
                "recyclable": random.choice([True, False]),
            },
            "strength": round(random.uniform(150, 900), 0) if i < 5 else None,
            "thermal_conductivity": round(random.uniform(0.01, 50), 2),
            "embodied_carbon": round(random.uniform(0.5, 25), 1),
            "is_smart": is_smart,
        })

    pat_statuses = ["granted", "pending", "filed", "granted", "pending"]
    pat_titles = [
        "Smart Container Thermal Regulation System",
        "Self-Healing Composite Panel Method",
        "Modular Frame Quick-Lock Mechanism",
        "AI-Optimized Structural Load Distribution",
        "Bio-Responsive Insulation Material",
    ]
    pat_descs = [
        "A thermal regulation system using phase-change materials embedded in container walls.",
        "Method for self-healing micro-cracks in composite building panels.",
        "Quick-lock mechanism allowing rapid modular frame assembly without welding.",
        "AI-driven system for optimizing load distribution across structural members.",
        "Insulation material that adapts thermal resistance based on ambient conditions.",
    ]

    patents = []
    for i in range(5):
        patents.append({
            "id": _uid(),
            "title": pat_titles[i],
            "filing_date": (date.today() - timedelta(days=random.randint(30, 400))).isoformat(),
            "status": pat_statuses[i],
            "description": pat_descs[i],
        })

    return {
        "frameworks": frameworks,
        "materials": materials,
        "patents": patents,
    }


# ---------------------------------------------------------------------------
# sales.json - matches SalesResponse
# ---------------------------------------------------------------------------
def build_sales() -> dict[str, Any]:
    stages = ["Discovery", "Proposal", "Negotiation", "Won", "Lost"]
    stage_counts = [12, 8, 5, 3, 2]
    stage_values = [1200000, 2400000, 1800000, 950000, 320000]

    pipeline = [
        {"name": stages[i], "count": stage_counts[i], "value": stage_values[i]}
        for i in range(5)
    ]

    companies = [
        "Porto Housing Corp", "Lisboa Green Builds", "Algarve Eco Villas",
        "Barcelona Modular SA", "Amsterdam Living Labs", "Berlin Container GmbH",
        "Milano Smart Homes", "Warsaw Urban Dev", "Vienna Eco-Build",
        "Paris Green Quarter",
    ]
    contacts = [
        "Ana Silva", "Miguel Santos", "Sofia Pereira", "Carlos Rodriguez",
        "Jan de Vries", "Klaus Schmidt", "Lucia Rossi", "Anna Kowalska",
        "Fritz Weber", "Marie Dupont",
    ]

    leads = []
    for i in range(10):
        stage = random.choice(stages[:4])
        leads.append({
            "id": _uid(),
            "company": companies[i],
            "contact": contacts[i],
            "score": random.randint(30, 98),
            "stage": stage,
            "value": random.randint(50000, 500000),
            "last_activity": (date.today() - timedelta(days=random.randint(0, 30))).isoformat(),
        })

    total_value = sum(s["value"] for s in pipeline)
    won_value = pipeline[3]["value"]
    total_leads = sum(s["count"] for s in pipeline)

    metrics = {
        "total_revenue": won_value,
        "conversion_rate": round(pipeline[3]["count"] / total_leads * 100, 1) if total_leads else 0,
        "avg_deal_size": round(total_value / total_leads, 0) if total_leads else 0,
        "pipeline_value": total_value,
    }

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    revenue_chart = []
    for m in months:
        rev = random.randint(150000, 400000)
        target = random.randint(200000, 350000)
        revenue_chart.append({"month": m, "revenue": rev, "target": target})

    return {
        "pipeline": pipeline,
        "leads": leads,
        "metrics": metrics,
        "revenue_chart": revenue_chart,
    }


# ---------------------------------------------------------------------------
# intelligence.json - matches IntelligenceResponse
# ---------------------------------------------------------------------------
def build_intelligence() -> dict[str, Any]:
    kpis = [
        {"name": "Production Efficiency", "value": 87.2, "unit": "%", "change": 2.3, "trend": "up"},
        {"name": "Defect Rate", "value": 1.8, "unit": "%", "change": -0.4, "trend": "down"},
        {"name": "Avg Lead Time", "value": 14.5, "unit": "days", "change": -1.2, "trend": "down"},
        {"name": "Energy Usage", "value": 342, "unit": "kWh/unit", "change": -8, "trend": "down"},
    ]

    quarters = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", "Q1 2025", "Q2 2025"]
    forecasts = []
    for i, q in enumerate(quarters):
        actual = random.randint(80, 120) if i < 4 else None
        forecast = random.randint(85, 125)
        forecasts.append({
            "period": q,
            "actual": actual,
            "forecast": forecast,
            "lower_bound": forecast - random.randint(5, 15),
            "upper_bound": forecast + random.randint(5, 15),
        })

    categories = ["production", "quality", "supply_chain", "sustainability", "market"]
    impacts = ["high", "medium", "high", "medium", "low"]
    insight_titles = [
        "Production Line Optimization Opportunity",
        "Quality Trend Analysis - Q4 Results",
        "Supply Chain Risk Assessment: EU Logistics",
        "Carbon Footprint Reduction Progress",
        "Market Demand Forecast: Modular Housing 2025",
        "Material Cost Trend: Steel Price Volatility",
    ]
    insight_summaries = [
        "Line C shows 15% under-utilization. Recommending shift rebalancing for +12% throughput.",
        "Defect rate dropped to 1.8% across all lines. Welding quality improved after training program.",
        "EU logistics delays expected in Q2 due to new border regulations. Recommend buffer stock increase.",
        "Carbon reduction targets on track: 22% reduction YoY. Bio-composite adoption accelerating.",
        "Modular housing demand in Portugal projected to grow 35% in 2025. Expansion recommended.",
        "Steel prices showing 8% quarterly volatility. Lock-in contracts recommended for Q2-Q3.",
    ]

    insights = []
    for i in range(6):
        insights.append({
            "id": _uid(),
            "title": insight_titles[i],
            "category": categories[i % len(categories)],
            "summary": insight_summaries[i],
            "date": (date.today() - timedelta(days=i * 7)).isoformat(),
            "impact": impacts[i % len(impacts)],
        })

    return {
        "insights": insights,
        "forecasts": forecasts,
        "kpis": kpis,
    }


# ---------------------------------------------------------------------------
# deploy.json - matches DeployResponse
# ---------------------------------------------------------------------------
def build_deploy() -> dict[str, Any]:
    destinations = [
        "Porto, Portugal", "Lisboa, Portugal", "Faro, Portugal",
        "Barcelona, Spain", "Madrid, Spain", "Amsterdam, Netherlands",
        "Berlin, Germany", "Milano, Italy",
    ]
    del_statuses = ["in_transit", "delivered", "in_transit", "preparing",
                    "delivered", "in_transit", "preparing", "delivered"]

    deliveries = []
    for i in range(8):
        progress = 100 if del_statuses[i] == "delivered" else random.randint(10, 90)
        deliveries.append({
            "id": _uid(),
            "destination": destinations[i],
            "status": del_statuses[i],
            "eta": (date.today() + timedelta(days=random.randint(1, 30))).isoformat(),
            "progress": progress,
            "items": random.randint(2, 24),
        })

    job_types = ["installation", "commissioning", "inspection", "handover",
                 "installation", "commissioning"]
    job_statuses = ["active", "completed", "active", "pending", "active", "completed"]
    sites = [
        "Site A - Porto Norte", "Site B - Lisboa Centro", "Site C - Faro Sul",
        "Site D - Barcelona Este", "Site E - Amsterdam West", "Site F - Berlin Mitte",
    ]
    teams = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"]

    jobs = []
    for i in range(6):
        jobs.append({
            "id": _uid(),
            "site": sites[i],
            "type": job_types[i],
            "status": job_statuses[i],
            "started": (date.today() - timedelta(days=random.randint(1, 30))).isoformat(),
            "team": teams[i],
        })

    in_transit = sum(1 for d in deliveries if d["status"] == "in_transit")
    delivered = sum(1 for d in deliveries if d["status"] == "delivered")
    active_sites = sum(1 for j in jobs if j["status"] == "active")

    return {
        "deliveries": deliveries,
        "jobs": jobs,
        "metrics": {
            "active_deliveries": len(deliveries),
            "in_transit": in_transit,
            "active_sites": active_sites,
            "completed": delivered,
        },
    }


# ---------------------------------------------------------------------------
# partners.json - matches PartnersResponse
# ---------------------------------------------------------------------------
def build_partners() -> dict[str, Any]:
    partner_data = [
        ("EcoBuild Portugal", "manufacturer", "Southern EU", "Portugal", 72),
        ("ModularTech Spain", "manufacturer", "Southern EU", "Spain", 85),
        ("GreenFrame Germany", "supplier", "Central EU", "Germany", 58),
        ("NordicPrefab Sweden", "manufacturer", "Northern EU", "Sweden", 64),
        ("DutchModular NL", "logistics", "Western EU", "Netherlands", 91),
        ("ItalBuild Milano", "manufacturer", "Southern EU", "Italy", 77),
        ("PolishStruct Warsaw", "supplier", "Eastern EU", "Poland", 45),
        ("AustriaPanel Wien", "manufacturer", "Central EU", "Austria", 69),
    ]

    partners = []
    for name, ptype, region, country, util in partner_data:
        partners.append({
            "id": _uid(),
            "name": name,
            "type": ptype,
            "region": region,
            "country": country,
            "capacity_utilization": util,
            "capacity": random.randint(100, 500),
            "compliance_status": random.choice(["compliant", "compliant", "compliant", "review_needed"]),
            "active_projects": random.randint(1, 8),
            "rating": random.randint(3, 5),
            "lead_time": random.randint(7, 28),
        })

    regions = list(set(p["region"] for p in partners))
    compliant = sum(1 for p in partners if p["compliance_status"] == "compliant")
    avg_util = round(sum(p["capacity_utilization"] for p in partners) / len(partners), 1)

    return {
        "partners": partners,
        "metrics": {
            "total_partners": len(partners),
            "regions": len(regions),
            "compliant": compliant,
            "avg_utilization": avg_util,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"Generating static API JSON files (SEED={SEED}) ...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    _write_json("health.json", build_health())
    _write_json("fabric.json", build_fabric())
    _write_json("fabric-scene.json", build_fabric_scene())
    _write_json("frameworks.json", build_frameworks())
    _write_json("sales.json", build_sales())
    _write_json("intelligence.json", build_intelligence())
    _write_json("deploy.json", build_deploy())
    _write_json("partners.json", build_partners())

    print("Done. All 8 files generated.")


if __name__ == "__main__":
    main()
