import pytest
import os
from solarscan.geometry import calculate_shoelace_area, calculate_perimeter, calculate_usable_area
from solarscan.osm import query_osm_building
from solarscan.cli import run_scan
import matplotlib

def test_troubleshooting_issue1_manual_lat_lon(tmp_path):
    """
    Issue: OSM query returns no building / missing address.
    Resolution: Manually pass --lat / --lon override.
    """
    # Manual lat/lon pass
    pdf_path = run_scan("Unmapped Remote Field", lat=25.2048, lon=55.2708, out_dir=str(tmp_path))
    assert os.path.exists(pdf_path)

def test_troubleshooting_issue2_setback_too_large(tmp_path):
    """
    Issue: Usable area computes as zero or negative when setback_m is too large relative to footprint.
    Resolution: Reduce setback_m.
    """
    raw_area = 50.0   # small 5m x 10m building
    perimeter = 30.0  # 2*(5+10) = 30m
    
    # Large setback causes negative usable area without protection, or 0 with max(0, usable)
    large_setback = 3.0  # 30 * 3.0 = 90 > 50
    usable_zero = calculate_usable_area(raw_area, perimeter, setback_m=large_setback)
    assert usable_zero == 0.0  # Zero usable area
    
    # Resolution: Reduce setback to 0.5m
    reduced_setback = 0.5  # 30 * 0.5 = 15 < 50
    usable_valid = calculate_usable_area(raw_area, perimeter, setback_m=reduced_setback)
    assert usable_valid == 35.0  # Usable area restored!

def test_troubleshooting_issue3_matplotlib_backend(tmp_path):
    """
    Issue: PDF report missing footprint diagram if matplotlib backend fails.
    Resolution: Ensure non-gui backend ('Agg') is configured properly and plot builds.
    """
    assert matplotlib.get_backend().lower() == 'agg'
    pdf_path = run_scan("Test Matplotlib", out_dir=str(tmp_path))
    assert os.path.exists(pdf_path)
