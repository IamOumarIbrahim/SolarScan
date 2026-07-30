"""
PV Array Sizing Calculator
Calculates system DC capacity (kWp) and total PV module counts based on area and module ratings.
"""
from typing import Dict, Any

def calculate_array_capacity(usable_area_sqm: float, module_wattage: int = 400, module_area_sqm: float = 2.0) -> Dict[str, Any]:
    """
    Computes total module count and total DC system capacity.
    """
    num_modules = int(usable_area_sqm // module_area_sqm)
    dc_capacity_kw = (num_modules * module_wattage) / 1000.0
    return {
        "num_modules": num_modules,
        "module_wattage": module_wattage,
        "dc_capacity_kw": dc_capacity_kw
    }
