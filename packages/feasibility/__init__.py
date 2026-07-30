"""
SolarScan Feasibility Package
Rooftop GIS building extraction and geometry processing.
"""
from .osm_extractor import extract_building_polygons
from .roof_geometry import calculate_useable_roof_area

__all__ = ["extract_building_polygons", "calculate_useable_roof_area"]
