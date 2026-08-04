import csv
import json
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET_CSV = ROOT / "validation" / "dataset.csv"
FIXTURES_DIR = ROOT / "validation" / "fixtures"
DIAGRAMS_DIR = ROOT / "validation" / "diagrams"

def test_validation_dataset_gate_checks():
    assert DATASET_CSV.exists()
    
    with open(DATASET_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Row count between 25 and 30
    assert 25 <= len(rows) <= 30

    categories = set()
    hard_cases = 0

    fixture_files = list(FIXTURES_DIR.glob("*.json"))
    diagram_files = list(DIAGRAMS_DIR.glob("*.png"))

    assert len(fixture_files) == len(rows)
    assert len(diagram_files) == len(rows)

    for row in rows:
        cid = row["id"]
        assert (FIXTURES_DIR / f"{cid}.json").exists()
        assert (DIAGRAMS_DIR / f"{cid}.png").exists()

        categories.add(row["category"])

        if row.get("hard_case") == "true":
            hard_cases += 1
            assert row["osm_building_id"] in ("", "synthetic_fallback") or float(row["osm_area_m2"]) > 0
        else:
            assert row["osm_building_id"] != ""
            assert float(row["osm_area_m2"]) > 0

        # manual_area_m2 must be empty in Module 3
        assert row["manual_area_m2"].strip() == ""

    assert len(categories) >= 4
    assert hard_cases >= 1
