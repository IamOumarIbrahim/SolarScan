"""
NREL SAM (System Advisor Model) Exporter
Formats solar design metrics into PySAM/SAM compatible JSON schema.
"""
import json
from typing import Dict, Any

def export_sam_config(dc_capacity_kw: float, tilt_deg: float = 20.0, azimuth_deg: float = 180.0) -> str:
    """
    Exports SAM simulation inputs to JSON string format.
    """
    config = {
        "system_capacity": dc_capacity_kw,
        "module_type": 0, # Standard C-Si
        "array_type": 0,  # Fixed Open Rack
        "tilt": tilt_deg,
        "azimuth": azimuth_deg,
        "losses": 14.0    # Standard system losses (%)
    }
    return json.dumps(config, indent=2)
