"""Tests for the deterministic seed generator."""

from __future__ import annotations

from app.seed.generator import SeedGenerator


def test_seed_determinism() -> None:
    """Two generators with the same seed must produce identical output."""
    gen1 = SeedGenerator(seed=42)
    gen2 = SeedGenerator(seed=42)

    data1 = gen1.generate_all()
    data2 = gen2.generate_all()

    # Compare every key
    assert set(data1.keys()) == set(data2.keys())
    for key in data1:
        assert data1[key] == data2[key], f"Mismatch in entity type: {key}"


def test_different_seed_produces_different_data() -> None:
    """Generators with different seeds must produce different data."""
    gen1 = SeedGenerator(seed=42)
    gen2 = SeedGenerator(seed=99)

    data1 = gen1.generate_all()
    data2 = gen2.generate_all()

    # Leads should differ (names are randomly generated)
    assert data1["leads"][0]["name"] != data2["leads"][0]["name"]


def test_all_records_have_provenance() -> None:
    """Every generated record must carry source='synthetic_seeded'."""
    gen = SeedGenerator(seed=42)
    data = gen.generate_all()

    for key, records in data.items():
        if key == "factory_scene":
            # Scene is a dict, not a list of records
            continue
        assert isinstance(records, list), f"{key} should be a list"
        for rec in records:
            assert rec.get("source") == "synthetic_seeded", (
                f"Record in {key} missing source='synthetic_seeded': {rec.get('id', 'unknown')}"
            )


def test_no_lsf_materials() -> None:
    """Seed data must NOT contain LSF or weak materials."""
    gen = SeedGenerator(seed=42)
    data = gen.generate_all()

    for mat in data["materials"]:
        name_lower = mat["name"].lower()
        assert "lsf" not in name_lower, f"LSF material found: {mat['name']}"
        assert "light steel frame" not in name_lower, f"LSF material found: {mat['name']}"
        assert "light gauge" not in name_lower, f"Weak material found: {mat['name']}"


def test_entity_counts() -> None:
    """Verify expected entity counts from default generation."""
    gen = SeedGenerator(seed=42)
    data = gen.generate_all()

    assert len(data["suppliers"]) == 8
    assert len(data["materials"]) == 14
    assert len(data["house_configs"]) == 6
    assert len(data["frameworks"]) == 4
    assert len(data["patents"]) == 6
    assert len(data["leads"]) == 15
    assert len(data["production_lines"]) == 4
    assert len(data["partners"]) == 8
    assert len(data["insight_reports"]) == 8
    assert len(data["partner_quotes"]) > 0
    assert len(data["time_series_data"]) > 0
    assert len(data["qa_outlier_records"]) > 0
    # Dependent entities should have at least some records
    assert len(data["opportunities"]) > 0
    assert len(data["boms"]) > 0
    assert len(data["work_orders"]) > 0


def test_factory_scene_structure() -> None:
    """Factory scene should have objects and camera."""
    gen = SeedGenerator(seed=42)
    data = gen.generate_all()

    scene = data["factory_scene"]
    assert "objects" in scene
    assert "camera" in scene
    assert len(scene["objects"]) > 0
    for obj in scene["objects"]:
        assert "id" in obj
        assert "name" in obj
        assert "type" in obj
        assert "position" in obj
        assert "scale" in obj
