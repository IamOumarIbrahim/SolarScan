import os
import csv
import json
import time
from solarscan.fixtures import capture_fixture, load_fixture
from solarscan.geometry import latlon_to_meters, calculate_shoelace_area
from solarscan.report import generate_footprint_diagram

CANDIDATES = [
    {
        "id": "uos_w5",
        "name": "CS Department W5",
        "address": "Computer Science Department W5 Sharjah",
        "lat": 25.2893304,
        "lon": 55.4783103,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "uos_m13",
        "name": "Engineering Complex M13",
        "address": "College of Engineering M13 University of Sharjah",
        "lat": 25.28695,
        "lon": 55.47953,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "uos_m3",
        "name": "Student Center M3",
        "address": "Student Center M3 University of Sharjah",
        "lat": 25.28588,
        "lon": 55.48512,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "aus_main",
        "name": "AUS Main Building",
        "address": "Main Building American University of Sharjah",
        "lat": 25.30905,
        "lon": 55.49122,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "aus_engineering",
        "name": "AUS Engineering ES",
        "address": "Engineering Building ES AUS Sharjah",
        "lat": 25.31175,
        "lon": 55.49298,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "saf_art",
        "name": "Sharjah Art Foundation",
        "address": "Sharjah Art Foundation Al Mureijah Sharjah",
        "lat": 25.35824,
        "lon": 55.38379,
        "category": "Mixed-Use",
        "hard_case": "false"
    },
    {
        "id": "kingfisher_lodge",
        "name": "Kingfisher Retreat",
        "address": "Kingfisher Retreat Kalba Sharjah",
        "lat": 25.01258,
        "lon": 56.36302,
        "category": "Residential",
        "hard_case": "false"
    },
    {
        "id": "saif_wh1",
        "name": "SAIF Zone Warehouse 1",
        "address": "SAIF Zone Cargo Complex Sharjah",
        "lat": 25.32845,
        "lon": 55.51230,
        "category": "Warehouse",
        "hard_case": "false"
    },
    {
        "id": "saif_wh2",
        "name": "SAIF Zone Industrial Depot",
        "address": "SAIF Zone Executive Park Sharjah",
        "lat": 25.32410,
        "lon": 55.51680,
        "category": "Warehouse",
        "hard_case": "false"
    },
    {
        "id": "dubai_mall",
        "name": "Dubai Mall Complex",
        "address": "Financial Center Rd Downtown Dubai",
        "lat": 25.19720,
        "lon": 55.27970,
        "category": "Retail",
        "hard_case": "false"
    },
    {
        "id": "moe_dubai",
        "name": "Mall of the Emirates",
        "address": "Sheikh Zayed Rd Al Barsha 1 Dubai",
        "lat": 25.11810,
        "lon": 55.20060,
        "category": "Retail",
        "hard_case": "false"
    },
    {
        "id": "dha_warehouse",
        "name": "Al Quoz Logistics Complex",
        "address": "Al Quoz Industrial Area 3 Dubai",
        "lat": 25.14320,
        "lon": 55.23410,
        "category": "Warehouse",
        "hard_case": "false"
    },
    {
        "id": "jebel_ali_wh",
        "name": "JAFZA Logistics Depot",
        "address": "Jebel Ali Freezone South Dubai",
        "lat": 24.97540,
        "lon": 55.07680,
        "category": "Warehouse",
        "hard_case": "false"
    },
    {
        "id": "al_serkal",
        "name": "Alserkal Avenue Cultural District",
        "address": "17th St Al Quoz 1 Dubai",
        "lat": 25.14150,
        "lon": 55.22680,
        "category": "Mixed-Use",
        "hard_case": "false"
    },
    {
        "id": "al_satwa_res",
        "name": "Satwa Residential Block",
        "address": "Al Satwa Block 4 Dubai",
        "lat": 25.21540,
        "lon": 55.26820,
        "category": "Residential",
        "hard_case": "false"
    },
    {
        "id": "jumeirah_mosque",
        "name": "Jumeirah Grand Mosque",
        "address": "Jumeirah Beach Rd Jumeirah 1 Dubai",
        "lat": 25.23360,
        "lon": 55.26540,
        "category": "Mosque",
        "hard_case": "false"
    },
    {
        "id": "nyu_abudhabi",
        "name": "NYU Abu Dhabi Campus Center",
        "address": "Saadiyat Marina District Abu Dhabi",
        "lat": 24.52380,
        "lon": 54.43440,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "masdar_mist",
        "name": "Masdar Institute Knowledge Center",
        "address": "Masdar City Abu Dhabi",
        "lat": 24.42850,
        "lon": 54.61480,
        "category": "Campus",
        "hard_case": "false"
    },
    {
        "id": "ad_mall",
        "name": "Abu Dhabi Mall Center",
        "address": "Al Zahiya Tourist Club Area Abu Dhabi",
        "lat": 24.49520,
        "lon": 54.38380,
        "category": "Retail",
        "hard_case": "false"
    },
    {
        "id": "mussafah_wh",
        "name": "Mussafah Industrial Complex",
        "address": "Mussafah M-14 Abu Dhabi",
        "lat": 24.36450,
        "lon": 54.49850,
        "category": "Warehouse",
        "hard_case": "false"
    },
    {
        "id": "sheikh_zayed_mosque",
        "name": "Sheikh Zayed Mosque Annex",
        "address": "Sheikh Rashid Bin Saeed St Abu Dhabi",
        "lat": 24.41280,
        "lon": 54.47490,
        "category": "Mosque",
        "hard_case": "false"
    },
    {
        "id": "ajman_city_center",
        "name": "City Centre Ajman",
        "address": "Al Jerf 2 Ajman",
        "lat": 25.39950,
        "lon": 55.47920,
        "category": "Retail",
        "hard_case": "false"
    },
    {
        "id": "ajman_uni",
        "name": "Ajman University J1 Building",
        "address": "University St Al Jerf 1 Ajman",
        "lat": 25.41250,
        "lon": 55.51420,
        "category": "University",
        "hard_case": "false"
    },
    {
        "id": "rak_mall",
        "name": "RAK Mall Khuzam",
        "address": "Khuzam Rd Ras Al Khaimah",
        "lat": 25.77250,
        "lon": 55.95250,
        "category": "Retail",
        "hard_case": "false"
    },
    {
        "id": "rak_al_hamra",
        "name": "Al Hamra Village Compound",
        "address": "Al Hamra Village Ras Al Khaimah",
        "lat": 25.68850,
        "lon": 55.77850,
        "category": "Residential",
        "hard_case": "false"
    },
    {
        "id": "empty_quarter_desert",
        "name": "Unmapped Desert Outpost",
        "address": "Rub Al Khali Dunes Liwa Abu Dhabi",
        "lat": 22.85000,
        "lon": 54.00000,
        "category": "Residential",
        "hard_case": "true"
    }
]

def main():
    os.makedirs("validation/fixtures", exist_ok=True)
    os.makedirs("validation/diagrams", exist_ok=True)

    dataset_rows = []

    print(f"Capturing fixtures for {len(CANDIDATES)} validation candidates...")
    for idx, item in enumerate(CANDIDATES, 1):
        cid = item["id"]
        lat = item["lat"]
        lon = item["lon"]
        fixture_path = f"validation/fixtures/{cid}.json"
        diagram_path = f"validation/diagrams/{cid}.png"

        print(f"[{idx}/{len(CANDIDATES)}] Capturing '{cid}' ({item['name']})...")
        if os.path.exists(fixture_path):
            try:
                fixture_data = load_fixture(fixture_path)
            except Exception:
                fixture_data = capture_fixture(lat, lon, fixture_path)
                time.sleep(1.0)
        else:
            try:
                fixture_data = capture_fixture(lat, lon, fixture_path)
            except Exception as e:
                print(f"  Warning: capture failed for {cid}: {e}. Generating synthetic fallback.")
                lat_delta = 0.00015
                lon_delta = 0.00015
                synthetic_polygon = [
                    (lat - lat_delta, lon - lon_delta),
                    (lat - lat_delta, lon + lon_delta),
                    (lat + lat_delta, lon + lon_delta),
                    (lat + lat_delta, lon - lon_delta),
                ]
                fixture_data = {
                    "building_id": "synthetic_fallback",
                    "polygon_coords": synthetic_polygon,
                    "obstruction_area": 0.0,
                    "query_lat": lat,
                    "query_lon": lon
                }
                with open(fixture_path, "w", encoding="utf-8") as f:
                    json.dump(fixture_data, f, indent=2)
            time.sleep(1.0)

        meter_coords = latlon_to_meters(fixture_data["polygon_coords"])
        raw_area = calculate_shoelace_area(meter_coords)

        generate_footprint_diagram(meter_coords, diagram_path)

        dataset_rows.append({
            "id": cid,
            "name": item["name"],
            "address": item["address"],
            "lat": str(lat),
            "lon": str(lon),
            "category": item["category"],
            "hard_case": item["hard_case"],
            "osm_building_id": str(fixture_data["building_id"]),
            "osm_area_m2": f"{raw_area:.2f}",
            "manual_area_m2": "",
            "manual_source": "",
            "manual_measured_date": "",
            "notes": "Unmapped desert location trigger" if item["hard_case"] == "true" else ""
        })

    fieldnames = [
        "id", "name", "address", "lat", "lon", "category", "hard_case",
        "osm_building_id", "osm_area_m2", "manual_area_m2", "manual_source",
        "manual_measured_date", "notes"
    ]

    with open("validation/dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset_rows)

    print(f"Dataset captured successfully! Wrote {len(dataset_rows)} rows to validation/dataset.csv")

if __name__ == "__main__":
    main()
