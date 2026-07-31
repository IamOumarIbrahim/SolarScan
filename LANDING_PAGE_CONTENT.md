# SolarScan — Landing Page Content Manifest

## 1. Five-Second Positioning Message
- **Target Audience**: Commercial Solar Developers, Energy Analysts, Building Portfolio Managers.
- **5-Second Statement**: "Helps commercial solar developers and portfolio managers generate automated rooftop solar PV feasibility reports from OpenStreetMap building footprints."
- **Primary Mechanism**: End-to-end Python engine querying OpenStreetMap Overpass building polygons, calculating usable roof area via Shoelace geometry after fire-code setback insets, and outputting DC array sizing, annual yield, and NREL SAM reports.

## 2. Role-Based Pathways
- **Role 1: Commercial Solar Developer**: Focuses on usable area inset calculations ($A_{\text{usable}} = A - P \cdot s - A_{\text{obstruction}}$), module efficiency (20.0%), DC array sizing ($C_{\text{array}} = A_{\text{usable}} \times 0.20\text{ kW/m}^2$), and string inverter sizing (1.20 DC/AC oversizing ratio).
- **Role 2: Building Portfolio Manager**: Focuses on Google Maps URL / address scanning, batch CSV multi-building processing, annual energy yield (232,394 kWh/yr), local tariff savings, simple financial payback (3.08 years), and client PDF report generation.

## 3. Verified Commands & Installation
- **Verified Direct Scan Command**:
  ```bash
  python -m solarscan "Computer Science Department W5 Sharjah"
  ```
- **Pip Editable Installation**:
  ```bash
  pip install -e .
  ```
- **1-Click Windows Executable**:
  Bundled standalone Windows installer (`SolarScan_Setup_v0.5.0.exe`).
- **Test Suite Verification**:
  ```bash
  py -m pytest -v
  # Output: 26 passed in 3.12s
  ```

## 4. Empirical Case Study & Geometry Baseline
- **Verified Case Study**: Computer Science Dept W5, University of Sharjah, UAE (OSM Way ID `204709053`).
  - Google Earth Manual Measure Trace Area: 1,699.86 m²
  - SolarScan Shoelace Polygon Area: 1,610.02 m²
  - Spatial Agreement: **94.7% Agreement** (< 5.2% variance)
  - Usable Roof Area (after 1.50m setback): 1,361.92 m²
  - Recommended DC Array Capacity: **272.38 kW DC** (226.99 kW AC)
- **Mathematical Formulations**:
  - Shoelace Footprint Area: $A = \frac{1}{2} |\sum_{i=1}^n (x_i y_{i+1} - x_{i+1} y_i)|$
  - Derate Factors: 5.5 PSH, 0.6348 azimuth/tilt factor, 0.85 system loss.

## 5. Feasibility Disclaimer & Data Provenance
- **Preliminary Feasibility Disclaimer**: SolarScan provides preliminary automated solar PV feasibility assessments based on public 2D GIS building footprints. Detailed on-site structural engineering, shading analysis, and local utility interconnect approval remain required prior to commercial procurement.
- **Browser Estimator Disclosure**: The interactive rooftop estimator renders real OSM footprint vertices and calculations for bundled case study fixtures (Computer Science Dept W5 Sharjah, Way `204709053`).
