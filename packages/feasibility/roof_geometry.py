"""
Roof Geometry & Setback Calculator
Computes usable rooftop area accounting for fire setbacks, HVAC obstructions, and tilt.
"""

def calculate_useable_roof_area(gross_area_sqm: float, setback_ratio: float = 0.15) -> float:
    """
    Computes usable solar panel area after applying boundary setbacks.
    """
    return max(0.0, gross_area_sqm * (1.0 - setback_ratio))
