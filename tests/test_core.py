import pytest
import math
from solarscan.geometry import (
    calculate_shoelace_area, calculate_perimeter, calculate_usable_area,
    calculate_dominant_azimuth, latlon_to_meters
)
from solarscan.sizing import calculate_dc_capacity, recommend_inverter_capacity
from solarscan.yield_estimate import calculate_orientation_derate, estimate_annual_yield, estimate_simple_payback

def test_shoelace_formula_hand_computed():
    """
    Unit test for Formula 1: Shoelace area calculation.
    Reference: README Section "Mathematical Foundations - 1. Shoelace Formula for Footprint Area"
    Hand-computed reference case: 10m x 20m rectangle.
    Vertices: (0,0), (10,0), (10,20), (0,20)
    Expected Area: 200.0 m²
    """
    vertices = [(0, 0), (10, 0), (10, 20), (0, 20)]
    area = calculate_shoelace_area(vertices)
    assert area == 200.0

def test_usable_area_formula_hand_computed():
    """
    Unit test for Formula 2: Usable roof area after setback.
    Reference: README Section "Mathematical Foundations - 2. Usable Roof Area After Setback"
    Formula: A_usable = A - P * s - A_obstruction
    Reference case: Area = 200 m², Perimeter = 60m (10x20 rect), Setback = 1.5m, Obstruction = 10m²
    Expected Usable Area = 200 - (60 * 1.5) - 10 = 200 - 90 - 10 = 100.0 m²
    """
    raw_area = 200.0
    perimeter = 60.0
    setback_m = 1.5
    obstruction_area = 10.0
    usable = calculate_usable_area(raw_area, perimeter, setback_m, obstruction_area)
    assert usable == 100.0

def test_dc_capacity_formula_hand_computed():
    """
    Unit test for Formula 3: DC Array Capacity Sizing.
    Reference: README Section "Mathematical Foundations - 3. DC Array Capacity Sizing"
    Formula: C_array = A_usable * eta_module * 1000 W/m²
    Reference case: A_usable = 100 m², eta_module = 0.20
    Expected C_array = 100 * 0.20 * 1000 = 20,000 W = 20.0 kW DC
    """
    usable_area = 100.0
    efficiency = 0.20
    dc_capacity = calculate_dc_capacity(usable_area, efficiency)
    assert dc_capacity == 20.0

def test_inverter_recommendation():
    """Tests DC/AC inverter sizing ratio recommendation."""
    dc_capacity = 20.0
    dc_ac_ratio = 1.2
    ac_capacity = recommend_inverter_capacity(dc_capacity, dc_ac_ratio)
    assert ac_capacity == round(20.0 / 1.2, 2)  # 16.67 kW AC

def test_yield_and_payback():
    """Tests energy yield and simple payback calculations."""
    dc_capacity = 10.0
    annual_kwh = estimate_annual_yield(dc_capacity, tilt_deg=15, azimuth_deg=180)
    assert annual_kwh > 0
    payback = estimate_simple_payback(annual_kwh, rate_per_kwh=0.38, cost_per_kw=1000.0, dc_capacity_kw=dc_capacity)
    assert payback > 0
