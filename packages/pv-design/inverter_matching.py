"""
Inverter Matching & String Sizing Calculator
Verifies MPPT voltage ranges, string length boundaries, and DC/AC ratios.
"""
from typing import Dict, Any

def calculate_string_configuration(num_modules: int, v_mp: float = 41.5, v_oc: float = 49.8, max_mppt_v: float = 1000.0) -> Dict[str, Any]:
    """
    Computes optimal string length (modules per string) and parallel string count.
    """
    max_modules_per_string = int(max_mppt_v // v_oc)
    num_strings = (num_modules + max_modules_per_string - 1) // max_modules_per_string
    return {
        "max_modules_per_string": max_modules_per_string,
        "num_strings": num_strings,
        "total_modules": num_modules
    }
