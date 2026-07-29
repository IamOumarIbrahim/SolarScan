# SolarScan Requirements Checklist

## 1. Metadata & Badges
- REQ-001: License badge links to CC0 1.0 Public Domain Dedication.
- REQ-002: Python version badge specifies Python 3.10+.
- REQ-003: Platform badge specifies Cross-platform.
- REQ-004: Key Dependency badge specifies OSM Overpass API.

## 2. Key Features & Functional Requirements
- REQ-005: Footprint-Accurate Area Extraction: Queries OSM Overpass API for building footprint polygon vertices and computes usable area via shoelace formula.
- REQ-006: Orientation & Tilt Penalty Modeling: Derives roof azimuth from footprint dominant edge, applies irradiance derating curve for non-optimal orientation and configurable default tilt.
- REQ-007: Setback-Aware Usable Area: Insets usable area polygon by configurable fire-code setback distance and subtracts detected obstruction tags.
- REQ-008: Automated System Sizing: Converts usable area into DC array size at standard module efficiency and recommends inverter capacity band using DC/AC ratio.
- REQ-009: One-Click PDF Report: Generates PDF with footprint diagram, system specs, estimated annual kWh yield, and simple payback estimate using utility rate input.
- REQ-010: Batch Mode for Portfolios: Accepts CSV of addresses and produces one PDF feasibility report per row.

## 3. Mathematical Foundations & Formulas
- REQ-011: Formula 1 - Shoelace Formula for Footprint Area: $$A = \frac{1}{2}\left|\sum_{i=1}^{n}(x_i y_{i+1} - x_{i+1} y_i)\right|$$
- REQ-012: Formula 2 - Usable Roof Area After Setback: $$A_{usable} = A - P \cdot s - A_{obstruction}$$
- REQ-013: Formula 3 - DC Array Capacity Sizing: $$C_{array} = A_{usable} \times \eta_{module} \times 1000\ \text{W/m}^2$$

## 4. System Architecture Stages
- REQ-014: Stage 1: OSM Overpass API Building Footprint Query.
- REQ-015: Stage 2: Shoelace Area + Azimuth Extraction.
- REQ-016: Stage 3: Setback Inset & Obstruction Subtraction.
- REQ-017: Stage 4: System Sizing: DC Array + Inverter Band.
- REQ-018: Stage 5: Yield & Payback Estimator.
- REQ-019: Stage 6 Output: PDF Feasibility Report.

## 5. Configuration Fields (`solarscan.yaml`)
- REQ-020: `default_tilt_deg`: Assumed panel tilt (float/int, default 15).
- REQ-021: `setback_m`: Fire-code setback distance (float/int, default 1.5).
- REQ-022: `module_efficiency`: Panel efficiency (float, default 0.20).
- REQ-023: `dc_ac_ratio`: Target DC/AC ratio for inverter sizing (float, default 1.2).

## 6. CLI Syntax & Commands
- REQ-024: Single scan command: `python -m solarscan.cli scan "<address>" [--tilt <deg>] [--rate-aed <rate>] [--module-efficiency <eff>]` (or via `solarscan scan`).
- REQ-025: Batch scan command: `python -m solarscan.cli batch <csv_file> --out <dir>` (or via `solarscan batch`).

## 7. File Structure
- REQ-026: `solarscan/` package containing `__init__.py`, `osm.py`, `geometry.py`, `sizing.py`, `yield_estimate.py`, `report.py`, `cli.py`.
- REQ-027: `examples/addresses.csv`.
- REQ-028: `tests/` directory with pytest test suite.
- REQ-029: `solarscan.yaml` config file.
- REQ-030: `README.md` and `LICENSE`.

## 8. Troubleshooting Scenarios
- REQ-031: Issue 1: OSM query returns no building -> Support manual `--lat`/`--lon` fallback or raising descriptive error.
- REQ-032: Issue 2: Usable area computes as zero/negative -> Support reducing `setback_m` or handling small roofs.
- REQ-033: Issue 3: PDF report missing footprint diagram -> Matplotlib installation / missing backend check.
