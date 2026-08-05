import argparse
import os
import sys
import yaml
import csv

from solarscan.osm import geocode_address, query_osm_building
from solarscan.fixtures import load_fixture
from solarscan.geometry import (
    latlon_to_meters, calculate_shoelace_area, calculate_perimeter,
    calculate_usable_area, calculate_dominant_azimuth
)
from solarscan.sizing import calculate_dc_capacity, recommend_inverter_capacity
from solarscan.yield_estimate import estimate_annual_yield, estimate_simple_payback
from solarscan.report import generate_pdf_report, generate_html_report


def load_config(config_path="solarscan.yaml"):
    defaults = {
        "default_tilt_deg": 15,
        "setback_m": 1.5,
        "module_efficiency": 0.20,
        "dc_ac_ratio": 1.2
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_cfg = yaml.safe_load(f)
                if isinstance(user_cfg, dict):
                    defaults.update(user_cfg)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    return defaults


import re

def run_scan(address, lat=None, lon=None, tilt=None, rate_aed=0.38, module_eff=None, setback=None, out_dir="reports", config_path="solarscan.yaml", fixture_path=None, fmt="pdf"):
    cfg = load_config(config_path)
    
    tilt_deg = tilt if tilt is not None else cfg.get("default_tilt_deg", 15)
    setback_m = setback if setback is not None else cfg.get("setback_m", 1.5)
    eff = module_eff if module_eff is not None else cfg.get("module_efficiency", 0.20)
    dc_ac_ratio = cfg.get("dc_ac_ratio", 1.2)

    if fixture_path:
        osm_data = load_fixture(fixture_path)
        lat = osm_data["query_lat"]
        lon = osm_data["query_lon"]
    else:
        if lat is None or lon is None:
            lat, lon = geocode_address(address)
        osm_data = query_osm_building(lat, lon)

    polygon_coords = osm_data["polygon_coords"]
    obstruction_area = osm_data.get("obstruction_area", 0.0)

    meter_coords = latlon_to_meters(polygon_coords)
    raw_area = calculate_shoelace_area(meter_coords)
    perimeter = calculate_perimeter(meter_coords)
    usable_area = calculate_usable_area(raw_area, perimeter, setback_m, obstruction_area)
    
    azimuth_deg = calculate_dominant_azimuth(meter_coords)
    dc_capacity_kw = calculate_dc_capacity(usable_area, eff)
    ac_capacity_kw = recommend_inverter_capacity(dc_capacity_kw, dc_ac_ratio)
    
    annual_kwh = estimate_annual_yield(dc_capacity_kw, tilt_deg=tilt_deg, azimuth_deg=azimuth_deg)
    payback_years = estimate_simple_payback(annual_kwh, rate_aed, dc_capacity_kw=dc_capacity_kw)

    if address.startswith(("http://", "https://")):
        match_place = re.search(r'/place/([^/@]+)', address)
        if match_place:
            raw_name = match_place.group(1).replace('+', '_')
        else:
            raw_name = f"scan_{lat:.4f}_{lon:.4f}"
        safe_name = "".join(c if c.isalnum() else "_" for c in raw_name)[:35].strip('_')
        if not safe_name:
            safe_name = f"scan_{lat:.4f}_{lon:.4f}"
    else:
        safe_name = "".join(c if c.isalnum() else "_" for c in address)[:35].strip('_')

    out_pdf = os.path.join(out_dir, f"SolarScan_Report_{safe_name}.pdf")
    out_html = os.path.join(out_dir, f"SolarScan_Report_{safe_name}.html")

    report_data = {
        "address": address,
        "lat": lat,
        "lon": lon,
        "polygon_coords": polygon_coords,
        "meter_coords": meter_coords,
        "raw_area": raw_area,
        "perimeter": perimeter,
        "usable_area": usable_area,
        "setback_m": setback_m,
        "module_efficiency": eff,
        "dc_capacity_kw": dc_capacity_kw,
        "ac_capacity_kw": ac_capacity_kw,
        "azimuth_deg": azimuth_deg,
        "tilt_deg": tilt_deg,
        "annual_kwh": annual_kwh,
        "rate_aed": rate_aed,
        "payback_years": payback_years
    }

    if fmt in ("pdf", "both"):
        generate_pdf_report(report_data, out_pdf)
    if fmt in ("html", "both"):
        generate_html_report(report_data, out_html)
    
    print(f"Scan completed for '{address}':")
    print(f"  - Raw Area: {raw_area:.2f} m² | Usable Area: {usable_area:.2f} m²")
    print(f"  - DC Capacity: {dc_capacity_kw:.2f} kW DC | Inverter Band: {ac_capacity_kw:.2f} kW AC")
    print(f"  - Annual Yield: {annual_kwh:,.2f} kWh/yr | Payback: {payback_years:.2f} yrs")
    if fmt in ("pdf", "both"):
        print(f"  - PDF Report saved to: {out_pdf}")
    if fmt in ("html", "both"):
        print(f"  - HTML Report saved to: {out_html}")
    return out_html if fmt == "html" else out_pdf


def main():
    parser = argparse.ArgumentParser(prog="solarscan", description="SolarScan Rooftop Solar Feasibility CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan a single address")
    scan_parser.add_argument("address", type=str, help="Target address")
    scan_parser.add_argument("--lat", type=float, default=None, help="Latitude override")
    scan_parser.add_argument("--lon", type=float, default=None, help="Longitude override")
    scan_parser.add_argument("--tilt", type=float, default=None, help="Assumed panel tilt in degrees")
    scan_parser.add_argument("--rate-aed", type=float, default=0.38, help="Utility rate per kWh")
    scan_parser.add_argument("--module-efficiency", type=float, default=None, help="Module efficiency (0.0 - 1.0)")
    scan_parser.add_argument("--setback", type=float, default=None, help="Fire-code setback in meters")
    scan_parser.add_argument("--out", type=str, default="reports", help="Output directory")
    scan_parser.add_argument("--config", type=str, default="solarscan.yaml", help="Path to config file")
    scan_parser.add_argument("--fixture", type=str, default=None, help="Path to offline JSON fixture")
    scan_parser.add_argument("--format", choices=["pdf", "html", "both"], default="pdf", help="Output format")

    # Demo subcommand
    demo_parser = subparsers.add_parser("demo", help="Run deterministic offline demo case study")
    demo_parser.add_argument("--format", choices=["pdf", "html", "both"], default="pdf", help="Output format")

    # Batch subcommand
    batch_parser = subparsers.add_parser("batch", help="Batch scan addresses from CSV")
    batch_parser.add_argument("csv_file", type=str, help="CSV file containing 'address' column")
    batch_parser.add_argument("--out", type=str, default="reports", help="Output directory")
    batch_parser.add_argument("--config", type=str, default="solarscan.yaml", help="Path to config file")
    batch_parser.add_argument("--format", choices=["pdf", "html", "both"], default="pdf", help="Output format")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(
            address=args.address,
            lat=args.lat,
            lon=args.lon,
            tilt=args.tilt,
            rate_aed=args.rate_aed,
            module_eff=args.module_efficiency,
            setback=args.setback,
            out_dir=args.out,
            config_path=args.config,
            fixture_path=args.fixture,
            fmt=args.format
        )
    elif args.command == "demo":
        run_scan(
            address="Computer Science Department W5 Sharjah",
            fixture_path="fixtures/w5_demo.json",
            tilt=15,
            rate_aed=0.38,
            out_dir="reports/demo",
            fmt=args.format
        )
    elif args.command == "batch":
        if not os.path.exists(args.csv_file):
            print(f"Error: CSV file '{args.csv_file}' not found.")
            sys.exit(1)
            
        with open(args.csv_file, 'r', encoding='utf-8') as f:
            rows = [r for r in csv.DictReader(f) if r.get("address")]
            total = len(rows)
            print(f"Starting batch scan for {total} location(s)...")
            for idx, row in enumerate(rows, 1):
                addr = row.get("address")
                lat = float(row["lat"]) if row.get("lat") and row["lat"].strip() else None
                lon = float(row["lon"]) if row.get("lon") and row["lon"].strip() else None
                print(f"\n[{idx}/{total}] Processing '{addr}'...")
                run_scan(address=addr, lat=lat, lon=lon, out_dir=args.out, config_path=args.config, fmt=args.format)
            print(f"\n[COMPLETE] Batch processing finished! Reports saved to '{args.out}'.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
