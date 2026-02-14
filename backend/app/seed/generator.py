"""Deterministic seeded data generator for EcoContainer + Planta Smart Homes.

Uses Faker with a fixed seed so that every run produces identical data.
All generated records are tagged ``source="synthetic_seeded"``.
"""

from __future__ import annotations

import json
import random
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from faker import Faker


class SeedGenerator:
    """Generates realistic, deterministic domain data for all modules.

    Parameters
    ----------
    seed : int
        Fixed random seed used by both ``Faker`` and ``random`` to ensure
        reproducibility.  Default is 42.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.fake = Faker(["pt_PT", "en_US"])
        Faker.seed(seed)
        self._rng = random.Random(seed)
        self._uuid_ns = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

    # ── helpers ───────────────────────────────────────────────────────────────

    def _deterministic_uuid(self, namespace: str, index: int) -> str:
        return str(uuid.uuid5(self._uuid_ns, f"{namespace}-{index}"))

    def _utcnow(self) -> datetime:
        return datetime(2025, 6, 1, 12, 0, 0, tzinfo=UTC)

    def _random_date(self, start_year: int = 2024, end_year: int = 2026) -> date:
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = (end - start).days
        return start + timedelta(days=self._rng.randint(0, delta))

    def _random_datetime(self, start_year: int = 2024, end_year: int = 2026) -> datetime:
        d = self._random_date(start_year, end_year)
        return datetime(
            d.year,
            d.month,
            d.day,
            self._rng.randint(6, 20),
            self._rng.choice([0, 15, 30, 45]),
            tzinfo=UTC,
        )

    def _provenance(self) -> dict[str, Any]:
        now = self._utcnow()
        return {
            "source": "synthetic_seeded",
            "source_id": f"seed-{self.seed}",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Suppliers
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_suppliers(self, count: int = 8) -> list[dict[str, Any]]:
        eu_suppliers = [
            ("ArcelorMittal Iberica", "Portugal", "ISO 9001, ISO 14001, CE Mark"),
            ("Siemens Building Technologies", "Germany", "ISO 9001, ISO 50001, TUV"),
            ("BASF Construction Chemicals", "Germany", "ISO 9001, ISO 14001, REACH"),
            ("Saint-Gobain Portugal", "Portugal", "ISO 9001, CE Mark, EPD"),
            ("Kingspan Insulated Panels", "Ireland", "ISO 9001, ISO 14001, BRE A+"),
            ("Covestro High Performance", "Germany", "ISO 9001, ISO 14001, UL"),
            ("Stora Enso CLT Division", "Finland", "ISO 9001, FSC, PEFC, EPD"),
            ("REHAU Smart Infrastructure", "Germany", "ISO 9001, ISO 14001, CE Mark"),
        ]
        items = []
        for i in range(min(count, len(eu_suppliers))):
            name, country, certs = eu_suppliers[i]
            items.append(
                {
                    "id": self._deterministic_uuid("supplier", i),
                    "name": name,
                    "country": country,
                    "rating": round(self._rng.uniform(4.0, 5.0), 1),
                    "lead_time_days": self._rng.choice([7, 10, 14, 21, 28]),
                    "certifications": certs,
                    "contact_email": f"sales@{name.lower().replace(' ', '').replace('.', '')[:12]}.eu",
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Materials (high-quality only, NO LSF, NO weak materials)
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_materials(self, suppliers: list[dict]) -> list[dict[str, Any]]:
        # Validate: NO LSF, NO weak materials in this list
        high_quality_materials = [
            {
                "name": "Cross-Laminated Timber (CLT) Grade C24",
                "category": "structural_timber",
                "grade": "C24",
                "density": 470.0,
                "tensile_strength": 420.0,
                "thermal_conductivity": 0.12,
                "embodied_carbon_kg": 110.0,
                "is_smart_material": False,
                "compliance_certs": "EN 16351, CE Mark, FSC, EPD",
            },
            {
                "name": "Ultra-High Performance Concrete (UHPC)",
                "category": "smart_concrete",
                "grade": "UHPC-150",
                "density": 2500.0,
                "tensile_strength": 150.0,
                "thermal_conductivity": 1.6,
                "embodied_carbon_kg": 280.0,
                "is_smart_material": False,
                "compliance_certs": "EN 206, CE Mark, EPD",
            },
            {
                "name": "Aerogel Insulation Panel",
                "category": "insulation_aerogel",
                "grade": "AeroTherm-Pro",
                "density": 150.0,
                "tensile_strength": 8.0,
                "thermal_conductivity": 0.015,
                "embodied_carbon_kg": 45.0,
                "is_smart_material": True,
                "compliance_certs": "EN 13162, CE Mark, Euroclass A2",
            },
            {
                "name": "Triple-Glazed Smart Glass",
                "category": "smart_glass",
                "grade": "SmartView-3X",
                "density": 2500.0,
                "tensile_strength": 120.0,
                "thermal_conductivity": 0.5,
                "embodied_carbon_kg": 95.0,
                "is_smart_material": True,
                "compliance_certs": "EN 1279, EN 410, CE Mark",
            },
            {
                "name": "Phase-Change Material Wallboard",
                "category": "phase_change_material",
                "grade": "PCM-23",
                "density": 850.0,
                "tensile_strength": 15.0,
                "thermal_conductivity": 0.18,
                "embodied_carbon_kg": 35.0,
                "is_smart_material": True,
                "compliance_certs": "EN 13501, Euroclass B-s1-d0",
            },
            {
                "name": "High-Strength Structural Steel S460",
                "category": "structural_steel",
                "grade": "S460ML",
                "density": 7850.0,
                "tensile_strength": 540.0,
                "thermal_conductivity": 50.0,
                "embodied_carbon_kg": 1200.0,
                "is_smart_material": False,
                "compliance_certs": "EN 10025, CE Mark, EPD",
            },
            {
                "name": "Self-Healing Bio-Concrete",
                "category": "smart_concrete",
                "grade": "BioHeal-50",
                "density": 2350.0,
                "tensile_strength": 55.0,
                "thermal_conductivity": 1.4,
                "embodied_carbon_kg": 180.0,
                "is_smart_material": True,
                "compliance_certs": "EN 206, CE Mark, Innovation Cert",
            },
            {
                "name": "Vacuum Insulation Panel (VIP)",
                "category": "insulation_aerogel",
                "grade": "VIP-Core-7",
                "density": 200.0,
                "tensile_strength": 5.0,
                "thermal_conductivity": 0.007,
                "embodied_carbon_kg": 30.0,
                "is_smart_material": False,
                "compliance_certs": "EN 13166, CE Mark, EPD",
            },
            {
                "name": "Carbon Fiber Reinforced Polymer (CFRP) Rebar",
                "category": "carbon_fiber",
                "grade": "CFRP-12",
                "density": 1600.0,
                "tensile_strength": 2000.0,
                "thermal_conductivity": 5.0,
                "embodied_carbon_kg": 320.0,
                "is_smart_material": False,
                "compliance_certs": "ACI 440, CE Mark",
            },
            {
                "name": "Piezoelectric Energy Harvesting Tile",
                "category": "smart_coating",
                "grade": "PZT-Floor-V2",
                "density": 3200.0,
                "tensile_strength": 80.0,
                "thermal_conductivity": 1.1,
                "embodied_carbon_kg": 55.0,
                "is_smart_material": True,
                "compliance_certs": "CE Mark, IEC 61010, EN 50581",
            },
            {
                "name": "Graphene-Enhanced Waterproofing Membrane",
                "category": "smart_coating",
                "grade": "GrapheneSeal-Pro",
                "density": 950.0,
                "tensile_strength": 35.0,
                "thermal_conductivity": 0.17,
                "embodied_carbon_kg": 18.0,
                "is_smart_material": True,
                "compliance_certs": "EN 13967, CE Mark, EPD",
            },
            {
                "name": "Recycled Aluminium Composite Panel",
                "category": "composite_panel",
                "grade": "ReAlu-FR-A2",
                "density": 2700.0,
                "tensile_strength": 310.0,
                "thermal_conductivity": 160.0,
                "embodied_carbon_kg": 85.0,
                "is_smart_material": False,
                "compliance_certs": "EN 13501, Euroclass A2, EPD",
            },
            {
                "name": "Structural Aluminium Alloy 6082-T6",
                "category": "structural_aluminum",
                "grade": "6082-T6",
                "density": 2710.0,
                "tensile_strength": 310.0,
                "thermal_conductivity": 170.0,
                "embodied_carbon_kg": 95.0,
                "is_smart_material": False,
                "compliance_certs": "EN 1999, CE Mark, EPD",
            },
            {
                "name": "Basalt Fiber Composite Panel",
                "category": "composite_panel",
                "grade": "BasaltComp-HT",
                "density": 1900.0,
                "tensile_strength": 480.0,
                "thermal_conductivity": 0.9,
                "embodied_carbon_kg": 65.0,
                "is_smart_material": False,
                "compliance_certs": "EN 13706, CE Mark, EPD",
            },
        ]
        # Validate: reject LSF and weak materials
        excluded_terms = {"lsf", "light steel frame", "light gauge"}
        for mat in high_quality_materials:
            name_lower = str(mat["name"]).lower()
            for term in excluded_terms:
                assert term not in name_lower, f"LSF/weak material in seed: {mat['name']}"
        items = []
        for i, mat in enumerate(high_quality_materials):
            supplier = suppliers[i % len(suppliers)]
            items.append(
                {
                    "id": self._deterministic_uuid("material", i),
                    "supplier_id": supplier["id"],
                    **mat,
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # House Configs
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_house_configs(self, count: int = 6) -> list[dict[str, Any]]:
        configs = [
            ("Planta Compact T1", "compact", 3, 45.0, 1),
            ("Planta Family T3", "family", 6, 110.0, 2),
            ("Planta Villa T4+", "villa", 10, 200.0, 2),
            ("Planta Studio", "studio", 2, 32.0, 1),
            ("Planta Duplex T2", "duplex", 5, 85.0, 2),
            ("Planta Eco-Lodge", "eco_lodge", 8, 150.0, 1),
        ]
        items = []
        for i in range(min(count, len(configs))):
            name, model_type, modules, area, floors = configs[i]
            items.append(
                {
                    "id": self._deterministic_uuid("house_config", i),
                    "name": name,
                    "model_type": model_type,
                    "num_modules": modules,
                    "floor_area_m2": area,
                    "num_floors": floors,
                    "config_json": json.dumps(
                        {
                            "insulation": "aerogel",
                            "glazing": "triple_smart",
                            "hvac": "heat_pump",
                            "solar_kw": round(area * 0.08, 1),
                            "battery_kwh": round(area * 0.12, 1),
                            "smart_home": True,
                        }
                    ),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Frameworks
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_frameworks(self, count: int = 4) -> list[dict[str, Any]]:
        frameworks = [
            (
                "EcoFrame Hybrid CLT-Steel",
                "hybrid",
                "Patented hybrid cross-laminated timber and high-strength steel "
                "modular framing system for seismic zone IV compliance.",
                "A+",
            ),
            (
                "BioFrame Self-Healing Concrete",
                "concrete",
                "Self-healing bio-concrete structural framework with embedded "
                "sensors for real-time stress monitoring.",
                "A",
            ),
            (
                "NanoFrame Graphene-Enhanced",
                "composite",
                "Graphene-enhanced composite framework with superior "
                "strength-to-weight ratio and thermal performance.",
                "A+",
            ),
            (
                "SmartFrame Adaptive Skin",
                "adaptive",
                "Adaptive building envelope framework integrating phase-change "
                "materials, smart glass, and piezoelectric harvesting.",
                "A",
            ),
        ]
        items = []
        for i in range(min(count, len(frameworks))):
            name, ftype, desc, rating = frameworks[i]
            items.append(
                {
                    "id": self._deterministic_uuid("framework", i),
                    "name": name,
                    "framework_type": ftype,
                    "description": desc,
                    "structural_rating": rating,
                    "materials_json": json.dumps(
                        [f"material-ref-{j}" for j in range(self._rng.randint(2, 5))]
                    ),
                    "patent_ids": json.dumps(
                        [f"patent-ref-{j}" for j in range(self._rng.randint(1, 3))]
                    ),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Patents
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_patents(self, count: int = 6) -> list[dict[str, Any]]:
        patents = [
            (
                "Modular CLT-Steel Hybrid Connector for Seismic Resilience",
                "EP-2024-001234",
                "granted",
            ),
            (
                "Self-Healing Bio-Concrete Mix with Bacillus Subtilis Integration",
                "EP-2024-001567",
                "granted",
            ),
            (
                "Adaptive Smart Glass Facade with Electrochromic Control System",
                "EP-2025-002345",
                "pending",
            ),
            (
                "Phase-Change Material Thermal Storage for Modular Housing",
                "EP-2025-002789",
                "pending",
            ),
            (
                "Graphene-Enhanced Waterproofing Membrane for CLT Structures",
                "PT-2025-003456",
                "filed",
            ),
            (
                "Piezoelectric Floor Tile Energy Harvesting System for Smart Homes",
                "EP-2025-004123",
                "filed",
            ),
        ]
        items = []
        for i in range(min(count, len(patents))):
            title, filing, status = patents[i]
            filing_date = self._random_date(2024, 2025)
            items.append(
                {
                    "id": self._deterministic_uuid("patent", i),
                    "title": title,
                    "filing_number": filing,
                    "status": status,
                    "filing_date": filing_date.isoformat(),
                    "claims_json": json.dumps(
                        {
                            "independent_claims": self._rng.randint(2, 5),
                            "dependent_claims": self._rng.randint(5, 15),
                            "summary": f"Novel approach to {title.lower()[:60]}",
                        }
                    ),
                    "experiment_results_json": json.dumps(
                        {
                            "tests_conducted": self._rng.randint(5, 20),
                            "success_rate_pct": round(self._rng.uniform(88, 99.5), 1),
                            "peer_reviewed": self._rng.choice([True, False]),
                        }
                    ),
                    "inventors": "Dr. Maria Santos, Eng. Pedro Almeida, Dr. Sofia Costa",
                    "novelty_notes": f"First application of this technology in modular housing: {title}",
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Leads
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_leads(self, count: int = 15) -> list[dict[str, Any]]:
        statuses = ["new", "contacted", "qualified", "proposal", "negotiation", "won"]
        companies = [
            "Grupo Pestana Hotels",
            "Sonae Sierra",
            "CBRE Portugal",
            "Merlin Properties",
            "Vanguard Properties",
            "JLL Portugal",
            "Habitat Invest",
            "Square Asset Management",
            "Explorer Investments",
            "Norfin SGFII",
            "Avenue Real Estate",
            "Kronos Real Estate",
            "Nexity Portugal",
            "Libertas Group",
            "Telhabel Construcoes",
        ]
        regions = ["Lisboa", "Porto", "Algarve", "Centro", "Norte", "Alentejo"]
        items = []
        for i in range(count):
            status = statuses[i % len(statuses)]
            region = regions[i % len(regions)]
            value = round(self._rng.uniform(120_000, 650_000), 2)
            items.append(
                {
                    "id": self._deterministic_uuid("lead", i),
                    "name": self.fake.name(),
                    "email": self.fake.email(),
                    "phone": self.fake.phone_number(),
                    "company": companies[i % len(companies)],
                    "status": status,
                    "score": self._rng.randint(20, 95),
                    "assigned_to": self.fake.name(),
                    "region": region,
                    "pipeline_value": value,
                    "notes": f"Interested in Planta Smart Homes {self._rng.choice(['T1', 'T3', 'T4+', 'Studio', 'Duplex'])} model.",
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Opportunities
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_opportunities(self, leads: list[dict]) -> list[dict[str, Any]]:
        stages = ["discovery", "proposal", "negotiation", "closed_won", "closed_lost"]
        items = []
        for i, lead in enumerate(leads):
            if lead["status"] in ("qualified", "proposal", "negotiation", "won"):
                stage = stages[self._rng.randint(0, len(stages) - 1)]
                value = round(self._rng.uniform(120_000, 650_000), 2)
                items.append(
                    {
                        "id": self._deterministic_uuid("opportunity", i),
                        "lead_id": lead["id"],
                        "title": f"Planta Smart Home - {lead['company']}",
                        "value": value,
                        "stage": stage,
                        "probability": round(self._rng.uniform(0.3, 0.95), 2),
                        "expected_close": self._random_date(2025, 2026).isoformat(),
                        **self._provenance(),
                    }
                )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Contracts
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_contracts(self, opportunities: list[dict]) -> list[dict[str, Any]]:
        items = []
        idx = 0
        for opp in opportunities:
            if opp["stage"] in ("negotiation", "closed_won"):
                items.append(
                    {
                        "id": self._deterministic_uuid("contract", idx),
                        "opportunity_id": opp["id"],
                        "number": f"ECO-{2025}-{idx + 1:04d}",
                        "value": opp["value"],
                        "status": "active" if opp["stage"] == "closed_won" else "pending",
                        "signed_date": (
                            self._random_date(2025, 2025).isoformat()
                            if opp["stage"] == "closed_won"
                            else None
                        ),
                        "terms": "Standard EcoContainer modular housing contract with 10-year structural warranty.",
                        **self._provenance(),
                    }
                )
                idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # BOMs
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_boms(
        self, house_configs: list[dict], materials: list[dict]
    ) -> list[dict[str, Any]]:
        items = []
        for i, hc in enumerate(house_configs):
            num_items = self._rng.randint(8, 15)
            bom_items = []
            total = 0.0
            for j in range(num_items):
                mat = materials[j % len(materials)]
                qty = self._rng.randint(1, 50)
                unit_cost = round(self._rng.uniform(50, 5000), 2)
                line_cost = round(qty * unit_cost, 2)
                total += line_cost
                bom_items.append(
                    {
                        "material_id": mat["id"],
                        "material_name": mat["name"],
                        "quantity": qty,
                        "unit": "units",
                        "unit_cost": unit_cost,
                        "line_cost": line_cost,
                    }
                )
            items.append(
                {
                    "id": self._deterministic_uuid("bom", i),
                    "house_config_id": hc["id"],
                    "version": 1,
                    "items_json": json.dumps(bom_items),
                    "total_cost": round(total, 2),
                    "status": self._rng.choice(["draft", "approved", "in_production"]),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Production Lines
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_production_lines(self, count: int = 4) -> list[dict[str, Any]]:
        lines = [
            ("Line A - CLT Assembly", "Figueira da Foz, Portugal", 3),
            ("Line B - Steel Framing", "Figueira da Foz, Portugal", 2),
            ("Line C - Module Integration", "Figueira da Foz, Portugal", 4),
            ("Line D - Smart Systems Install", "Figueira da Foz, Portugal", 5),
        ]
        items = []
        for i in range(min(count, len(lines))):
            name, loc, cap = lines[i]
            items.append(
                {
                    "id": self._deterministic_uuid("production_line", i),
                    "name": name,
                    "location": loc,
                    "capacity_units_per_day": cap,
                    "status": self._rng.choice(["idle", "running", "running", "running"]),
                    "current_workorder_id": None,
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Work Orders
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_work_orders(
        self,
        boms: list[dict],
        production_lines: list[dict],
    ) -> list[dict[str, Any]]:
        statuses = ["planned", "scheduled", "in_progress", "completed"]
        items = []
        for i, bom in enumerate(boms):
            pl = production_lines[i % len(production_lines)]
            start = self._random_datetime(2025, 2025)
            end = start + timedelta(days=self._rng.randint(5, 30))
            wo_status = statuses[i % len(statuses)]
            items.append(
                {
                    "id": self._deterministic_uuid("work_order", i),
                    "bom_id": bom["id"],
                    "production_line_id": pl["id"],
                    "status": wo_status,
                    "priority": self._rng.randint(1, 5),
                    "scheduled_start": start.isoformat(),
                    "scheduled_end": end.isoformat(),
                    "actual_start": start.isoformat()
                    if wo_status in ("in_progress", "completed")
                    else None,
                    "actual_end": end.isoformat() if wo_status == "completed" else None,
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Inventory Items
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_inventory_items(self, materials: list[dict]) -> list[dict[str, Any]]:
        warehouses = [
            "Armazem Principal - Figueira da Foz",
            "Armazem Smart Materials - Coimbra",
        ]
        items = []
        for i, mat in enumerate(materials):
            wh = warehouses[i % len(warehouses)]
            items.append(
                {
                    "id": self._deterministic_uuid("inventory", i),
                    "material_id": mat["id"],
                    "warehouse": wh,
                    "quantity": round(self._rng.uniform(100, 10000), 1),
                    "unit": "kg" if mat["category"] not in ("glazing", "energy") else "units",
                    "min_stock": round(self._rng.uniform(50, 500), 1),
                    "max_stock": round(self._rng.uniform(10000, 50000), 1),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # QA Records
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_qa_records(self, work_orders: list[dict]) -> list[dict[str, Any]]:
        inspectors = [
            "Eng. Ana Ferreira",
            "Eng. Joao Oliveira",
            "Eng. Catarina Sousa",
            "Eng. Miguel Rocha",
        ]
        items = []
        for i, wo in enumerate(work_orders):
            if wo["status"] in ("completed", "in_progress"):
                items.append(
                    {
                        "id": self._deterministic_uuid("qa_record", i),
                        "work_order_id": wo["id"],
                        "inspector": inspectors[i % len(inspectors)],
                        "result": self._rng.choice(["pass", "pass", "pass", "minor_defect"]),
                        "defects_json": json.dumps([])
                        if self._rng.random() > 0.2
                        else json.dumps(
                            [
                                {
                                    "type": "cosmetic",
                                    "description": "Minor surface scratch on module panel",
                                    "severity": "low",
                                }
                            ]
                        ),
                        "notes": "Quality inspection completed per EcoContainer QA-001 standard.",
                        "inspected_at": self._random_datetime(2025, 2025).isoformat(),
                        **self._provenance(),
                    }
                )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Deliveries
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_deliveries(self, work_orders: list[dict]) -> list[dict[str, Any]]:
        carriers = ["Transporte Modular EU", "Logistica Verde SA", "EcoFreight Iberia"]
        destinations_pt = [
            "Lisboa, Portugal",
            "Porto, Portugal",
            "Faro, Portugal",
            "Braga, Portugal",
            "Coimbra, Portugal",
            "Setubal, Portugal",
        ]
        items = []
        idx = 0
        for wo in work_orders:
            if wo["status"] in ("completed",):
                est = self._random_datetime(2025, 2026)
                items.append(
                    {
                        "id": self._deterministic_uuid("delivery", idx),
                        "work_order_id": wo["id"],
                        "origin": "Figueira da Foz, Portugal",
                        "destination": destinations_pt[idx % len(destinations_pt)],
                        "carrier": carriers[idx % len(carriers)],
                        "status": self._rng.choice(["preparing", "in_transit", "delivered"]),
                        "estimated_arrival": est.isoformat(),
                        "actual_arrival": est.isoformat() if self._rng.random() > 0.4 else None,
                        **self._provenance(),
                    }
                )
                idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Deployment Jobs
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_deployment_jobs(self, deliveries: list[dict]) -> list[dict[str, Any]]:
        crew_leads = [
            "Mestre Carlos Mendes",
            "Mestre Rita Pinto",
            "Mestre Tiago Alves",
            "Mestre Ines Rodrigues",
        ]
        items = []
        for i, dlv in enumerate(deliveries):
            items.append(
                {
                    "id": self._deterministic_uuid("deployment", i),
                    "delivery_id": dlv["id"],
                    "site_address": dlv["destination"],
                    "status": self._rng.choice(
                        ["planned", "site_prep", "installing", "commissioning", "completed"]
                    ),
                    "installation_checklist_json": json.dumps(
                        {
                            "foundation_check": True,
                            "utility_connections": True,
                            "module_alignment": True,
                            "smart_system_boot": self._rng.choice([True, False]),
                            "final_inspection": self._rng.choice([True, False]),
                        }
                    ),
                    "commissioning_date": self._random_date(2025, 2026).isoformat(),
                    "crew_lead": crew_leads[i % len(crew_leads)],
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Partners
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_partners(self, count: int = 8) -> list[dict[str, Any]]:
        partners = [
            ("Modular Iberia SA", "Portugal", "Iberia", 20),
            ("Casas Modulares Espana SL", "Spain", "Iberia", 18),
            ("EcoBuild Deutschland GmbH", "Germany", "Central Europe", 25),
            ("Duurzaam Wonen BV", "Netherlands", "Benelux", 22),
            ("Green Homes France SAS", "France", "Western Europe", 18),
            ("Smart Living Italia SpA", "Italy", "Southern Europe", 12),
            ("EcoModul Polska Sp z o.o.", "Poland", "Central Europe", 16),
            ("NachhaltigBau GmbH", "Austria", "Central Europe", 14),
        ]
        items = []
        for i in range(min(count, len(partners))):
            name, country, region, cap = partners[i]
            items.append(
                {
                    "id": self._deterministic_uuid("partner", i),
                    "name": name,
                    "country": country,
                    "region": region,
                    "capacity_units_per_month": cap,
                    "compliance_docs_json": json.dumps(
                        {
                            "iso_9001": True,
                            "iso_14001": True,
                            "ce_mark": True,
                            "local_building_code": True,
                        }
                    ),
                    "contact_email": f"partnerships@{name.lower().replace(' ', '')[:15]}.eu",
                    "rating": round(self._rng.uniform(3.5, 5.0), 1),
                    "lead_time_days": self._rng.choice([21, 30, 45, 60]),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Capacity Plans
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_capacity_plans(self, partners: list[dict]) -> list[dict[str, Any]]:
        months = [f"2025-{m:02d}" for m in range(1, 13)]
        items = []
        idx = 0
        for partner in partners:
            cap = partner["capacity_units_per_month"]
            for month in months:
                alloc = self._rng.randint(int(cap * 0.3), cap)
                avail = cap - alloc
                items.append(
                    {
                        "id": self._deterministic_uuid("capacity_plan", idx),
                        "partner_id": partner["id"],
                        "month": month,
                        "allocated_units": alloc,
                        "available_units": avail,
                        "utilization_pct": round(alloc / cap * 100, 1) if cap > 0 else 0.0,
                        **self._provenance(),
                    }
                )
                idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Home Units
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_home_units(
        self, house_configs: list[dict], count: int = 10
    ) -> list[dict[str, Any]]:
        statuses = ["manufacturing", "shipped", "installed", "active"]
        locations_pt = [
            "Rua Augusta 45, Lisboa",
            "Av. dos Aliados 120, Porto",
            "Rua de Santa Catarina 88, Porto",
            "Praia da Rocha, Portimao",
            "Universidade de Coimbra, Coimbra",
            "Parque das Nacoes, Lisboa",
            "Av. da Liberdade 200, Lisboa",
            "Cais da Ribeira 15, Porto",
            "Bairro Alto 33, Lisboa",
            "Alfama 7, Lisboa",
        ]
        items = []
        for i in range(count):
            hc = house_configs[i % len(house_configs)]
            items.append(
                {
                    "id": self._deterministic_uuid("home_unit", i),
                    "house_config_id": hc["id"],
                    "serial_number": f"PSH-{2025}-{i + 1:05d}",
                    "owner_name": self.fake.name(),
                    "installation_date": self._random_date(2025, 2026).isoformat(),
                    "location": locations_pt[i % len(locations_pt)],
                    "status": statuses[i % len(statuses)],
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Telemetry Events
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_telemetry_events(
        self, home_units: list[dict], count_per_unit: int = 5
    ) -> list[dict[str, Any]]:
        event_types = [
            "temperature_reading",
            "energy_consumption",
            "solar_generation",
            "humidity_reading",
            "air_quality",
            "water_usage",
            "smart_glass_adjustment",
            "hvac_cycle",
        ]
        items = []
        idx = 0
        for hu in home_units:
            if hu["status"] in ("active", "installed"):
                for _ in range(count_per_unit):
                    evt = self._rng.choice(event_types)
                    items.append(
                        {
                            "id": self._deterministic_uuid("telemetry", idx),
                            "home_unit_id": hu["id"],
                            "event_type": evt,
                            "payload_json": json.dumps(
                                {
                                    "value": round(self._rng.uniform(0, 100), 2),
                                    "unit": {
                                        "temperature_reading": "C",
                                        "energy_consumption": "kWh",
                                        "solar_generation": "kWh",
                                        "humidity_reading": "%",
                                        "air_quality": "AQI",
                                        "water_usage": "L",
                                        "smart_glass_adjustment": "tint_%",
                                        "hvac_cycle": "min",
                                    }.get(evt, "unit"),
                                    "sensor_id": f"sensor-{self._rng.randint(1, 20)}",
                                }
                            ),
                            "timestamp": self._random_datetime(2025, 2025).isoformat(),
                            **self._provenance(),
                        }
                    )
                    idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Partner Quotes
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_partner_quotes(self, partners: list[dict]) -> list[dict[str, Any]]:
        """Generate realistic quotes from EU partners with lead times."""
        items = []
        idx = 0
        for partner in partners:
            num_quotes = self._rng.randint(2, 4)
            for _ in range(num_quotes):
                units = self._rng.randint(2, 15)
                price_per = round(self._rng.uniform(3500, 8000), 2)
                items.append(
                    {
                        "id": self._deterministic_uuid("partner_quote", idx),
                        "partner_id": partner["id"],
                        "units": units,
                        "price_per_unit": price_per,
                        "total_price": round(units * price_per, 2),
                        "lead_time_days": partner["lead_time_days"] + self._rng.randint(-5, 10),
                        "valid_until": self._random_date(2025, 2026).isoformat(),
                        "status": self._rng.choice(["active", "active", "expired"]),
                        **self._provenance(),
                    }
                )
                idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Time Series Data (for forecasting)
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_time_series_data(
        self, work_orders: list[dict], count: int = 30
    ) -> list[dict[str, Any]]:
        """Generate time series data suitable for lead time forecasting."""
        items = []
        for i in range(count):
            wo = work_orders[i % len(work_orders)] if work_orders else {}
            base_duration = self._rng.uniform(5, 30)
            # Add seasonal variation
            seasonal = 3.0 * (i % 7) / 7.0
            value = round(base_duration + seasonal, 2)
            items.append(
                {
                    "id": self._deterministic_uuid("time_series", i),
                    "metric": "lead_time_days",
                    "period": f"2025-W{(i % 52) + 1:02d}",
                    "value": value,
                    "work_order_id": wo.get("id"),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # QA Data with Outliers (for anomaly detection)
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_qa_with_outliers(self, work_orders: list[dict]) -> list[dict[str, Any]]:
        """Generate QA records with some outliers for anomaly detection testing."""
        inspectors = [
            "Eng. Ana Ferreira",
            "Eng. Joao Oliveira",
            "Eng. Catarina Sousa",
            "Eng. Miguel Rocha",
        ]
        items = []
        idx = 0
        for i, wo in enumerate(work_orders):
            if wo["status"] in ("completed", "in_progress"):
                # Normal record
                is_outlier = idx % 7 == 6  # Every 7th record is an outlier
                if is_outlier:
                    # Outlier: many defects
                    defects = [
                        {
                            "type": "structural",
                            "description": "Major alignment deviation detected",
                            "severity": "high",
                        },
                        {
                            "type": "cosmetic",
                            "description": "Surface damage on panel",
                            "severity": "medium",
                        },
                        {
                            "type": "functional",
                            "description": "Smart system connectivity failure",
                            "severity": "high",
                        },
                    ]
                    result = "fail"
                else:
                    defects = (
                        []
                        if self._rng.random() > 0.2
                        else [
                            {
                                "type": "cosmetic",
                                "description": "Minor surface scratch on module panel",
                                "severity": "low",
                            }
                        ]
                    )
                    result = self._rng.choice(["pass", "pass", "pass", "minor_defect"])

                items.append(
                    {
                        "id": self._deterministic_uuid("qa_outlier", idx),
                        "work_order_id": wo["id"],
                        "inspector": inspectors[i % len(inspectors)],
                        "result": result,
                        "defects_json": json.dumps(defects),
                        "notes": "Quality inspection per EcoContainer QA-001.",
                        "inspected_at": self._random_datetime(2025, 2025).isoformat(),
                        "defect_count": len(defects),
                        **self._provenance(),
                    }
                )
                idx += 1
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # Insight Reports
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_insight_reports(self, count: int = 8) -> list[dict[str, Any]]:
        reports = [
            ("Monthly Production Efficiency", "fabric", "kpi_dashboard"),
            ("Sales Pipeline Forecast Q3 2025", "sales", "forecast"),
            ("Material Cost Trend Analysis", "frameworks", "trend"),
            ("Smart Home Energy Optimization", "intelligence", "analysis"),
            ("Deployment Schedule Risk Assessment", "deploy", "risk"),
            ("Partner Capacity Utilization Report", "partners", "utilization"),
            ("Quality Defect Rate Trend", "fabric", "trend"),
            ("Carbon Footprint per Housing Unit", "intelligence", "sustainability"),
        ]
        items = []
        for i in range(min(count, len(reports))):
            title, module, rtype = reports[i]
            items.append(
                {
                    "id": self._deterministic_uuid("insight", i),
                    "title": title,
                    "module": module,
                    "report_type": rtype,
                    "parameters_json": json.dumps(
                        {
                            "period": "2025-Q3",
                            "granularity": "monthly",
                            "filters": {},
                        }
                    ),
                    "results_json": json.dumps(
                        {
                            "summary": f"Analysis of {title.lower()} completed.",
                            "key_metrics": {
                                "primary": round(self._rng.uniform(60, 99), 1),
                                "secondary": round(self._rng.uniform(40, 95), 1),
                                "trend": self._rng.choice(["up", "stable", "down"]),
                            },
                            "recommendations": [
                                "Continue monitoring key indicators.",
                                "Investigate outlier data points.",
                            ],
                        }
                    ),
                    "generated_at": self._random_datetime(2025, 2025).isoformat(),
                    **self._provenance(),
                }
            )
        return items

    # ═══════════════════════════════════════════════════════════════════════════
    # 3D Scene (factory layout)
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_factory_scene(self) -> dict[str, Any]:
        """Generate a 3D factory layout scene for the Fabric module."""
        objects = [
            {
                "id": self._deterministic_uuid("scene", 0),
                "name": "Factory Floor",
                "type": "floor",
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 50, "y": 0.1, "z": 30},
                "color": "#C0C0C0",
                "metadata": {"material": "concrete"},
            },
            {
                "id": self._deterministic_uuid("scene", 1),
                "name": "CLT Assembly Station",
                "type": "machine",
                "position": {"x": -15, "y": 1.5, "z": -8},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 6, "y": 3, "z": 4},
                "color": "#2196F3",
                "metadata": {"line": "Line A", "status": "running"},
            },
            {
                "id": self._deterministic_uuid("scene", 2),
                "name": "Steel Framing Robot",
                "type": "machine",
                "position": {"x": -5, "y": 2, "z": -8},
                "rotation": {"x": 0, "y": 45, "z": 0},
                "scale": {"x": 4, "y": 4, "z": 4},
                "color": "#FF9800",
                "metadata": {"line": "Line B", "status": "running"},
            },
            {
                "id": self._deterministic_uuid("scene", 3),
                "name": "Module Integration Bay",
                "type": "machine",
                "position": {"x": 8, "y": 2, "z": -5},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 10, "y": 4, "z": 8},
                "color": "#4CAF50",
                "metadata": {"line": "Line C", "status": "running"},
            },
            {
                "id": self._deterministic_uuid("scene", 4),
                "name": "Smart Systems Lab",
                "type": "machine",
                "position": {"x": 8, "y": 1.5, "z": 8},
                "rotation": {"x": 0, "y": 90, "z": 0},
                "scale": {"x": 6, "y": 3, "z": 5},
                "color": "#9C27B0",
                "metadata": {"line": "Line D", "status": "idle"},
            },
            {
                "id": self._deterministic_uuid("scene", 5),
                "name": "Main Conveyor Belt",
                "type": "conveyor",
                "position": {"x": 0, "y": 0.5, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 40, "y": 0.3, "z": 2},
                "color": "#607D8B",
                "metadata": {"speed_m_per_min": 2.5},
            },
            {
                "id": self._deterministic_uuid("scene", 6),
                "name": "Raw Materials Storage",
                "type": "storage",
                "position": {"x": -20, "y": 2, "z": 5},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 8, "y": 4, "z": 10},
                "color": "#795548",
                "metadata": {"capacity_tonnes": 500},
            },
            {
                "id": self._deterministic_uuid("scene", 7),
                "name": "QA Inspection Area",
                "type": "inspection",
                "position": {"x": 18, "y": 1, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "scale": {"x": 5, "y": 2, "z": 5},
                "color": "#F44336",
                "metadata": {"inspector_stations": 3},
            },
            {
                "id": self._deterministic_uuid("scene", 8),
                "name": "Loading Dock",
                "type": "dock",
                "position": {"x": 24, "y": 0.5, "z": 0},
                "rotation": {"x": 0, "y": 90, "z": 0},
                "scale": {"x": 4, "y": 1, "z": 12},
                "color": "#FF5722",
                "metadata": {"bays": 4},
            },
        ]
        camera = {
            "position": {"x": 30, "y": 25, "z": 30},
            "target": {"x": 0, "y": 0, "z": 0},
            "fov": 60.0,
        }
        return {"objects": objects, "camera": camera}

    # ═══════════════════════════════════════════════════════════════════════════
    # Master generator
    # ═══════════════════════════════════════════════════════════════════════════

    def generate_all(self) -> dict[str, Any]:
        """Generate all domain entities.  Returns a dict keyed by entity type.

        The output is fully deterministic: calling with the same seed
        always produces the same data.
        """
        # Reset state for reproducibility
        Faker.seed(self.seed)
        self._rng = random.Random(self.seed)
        self.fake = Faker(["pt_PT", "en_US"])
        Faker.seed(self.seed)

        suppliers = self.generate_suppliers()
        materials = self.generate_materials(suppliers)
        house_configs = self.generate_house_configs()
        frameworks = self.generate_frameworks()
        patents = self.generate_patents()
        leads = self.generate_leads()
        opportunities = self.generate_opportunities(leads)
        contracts = self.generate_contracts(opportunities)
        boms = self.generate_boms(house_configs, materials)
        production_lines = self.generate_production_lines()
        work_orders = self.generate_work_orders(boms, production_lines)
        inventory_items = self.generate_inventory_items(materials)
        qa_records = self.generate_qa_records(work_orders)
        deliveries = self.generate_deliveries(work_orders)
        deployment_jobs = self.generate_deployment_jobs(deliveries)
        partners = self.generate_partners()
        capacity_plans = self.generate_capacity_plans(partners)
        partner_quotes = self.generate_partner_quotes(partners)
        home_units = self.generate_home_units(house_configs)
        telemetry_events = self.generate_telemetry_events(home_units)
        time_series_data = self.generate_time_series_data(work_orders)
        qa_outlier_records = self.generate_qa_with_outliers(work_orders)
        insight_reports = self.generate_insight_reports()
        factory_scene = self.generate_factory_scene()

        return {
            "suppliers": suppliers,
            "materials": materials,
            "house_configs": house_configs,
            "frameworks": frameworks,
            "patents": patents,
            "leads": leads,
            "opportunities": opportunities,
            "contracts": contracts,
            "boms": boms,
            "production_lines": production_lines,
            "work_orders": work_orders,
            "inventory_items": inventory_items,
            "qa_records": qa_records,
            "deliveries": deliveries,
            "deployment_jobs": deployment_jobs,
            "partners": partners,
            "capacity_plans": capacity_plans,
            "partner_quotes": partner_quotes,
            "home_units": home_units,
            "telemetry_events": telemetry_events,
            "time_series_data": time_series_data,
            "qa_outlier_records": qa_outlier_records,
            "insight_reports": insight_reports,
            "factory_scene": factory_scene,
        }
