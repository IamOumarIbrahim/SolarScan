import math
import numpy as np

def calculate_shoelace_area(vertices):
    """
    Computes the exact roof area from OSM-tagged polygon vertices via the shoelace formula.
    Ref: README Section "Mathematical Foundations - 1. Shoelace Formula for Footprint Area"
    Formula: A = 0.5 * | sum_{i=1}^n (x_i * y_{i+1} - x_{i+1} * y_i) |
    """
    if len(vertices) < 3:
        return 0.0
    
    n = len(vertices)
    area = 0.0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += (x1 * y2) - (x2 * y1)
    return abs(area) / 2.0


def calculate_perimeter(vertices):
    """Calculates the total perimeter of a polygon defined by 2D vertices."""
    if len(vertices) < 3:
        return 0.0
    p = 0.0
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        p += math.hypot(x2 - x1, y2 - y1)
    return p


def calculate_usable_area(raw_area, perimeter, setback_m, obstruction_area=0.0):
    """
    Reduces raw footprint area by fire-code setback and known obstructions.
    Ref: README Section "Mathematical Foundations - 2. Usable Roof Area After Setback"
    Formula: A_usable = A - P * s - A_obstruction
    """
    usable = raw_area - (perimeter * setback_m) - obstruction_area
    return max(0.0, usable)


def calculate_dominant_azimuth(vertices):
    """
    Derives roof azimuth in degrees (0 = North, 90 = East, 180 = South, 270 = West)
    from the longest edge of the polygon footprint.
    """
    if len(vertices) < 2:
        return 180.0  # Default to south
    
    max_len = -1.0
    dominant_angle = 180.0
    n = len(vertices)
    
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist > max_len:
            max_len = dist
            # Angle relative to North (Y axis)
            dx = x2 - x1
            dy = y2 - y1
            angle = math.degrees(math.atan2(dx, dy)) % 360.0
            dominant_angle = angle
            
    return dominant_angle


def latlon_to_meters(coords):
    """
    Converts (lat, lon) vertices in degrees into relative meters (x, y) relative to the centroid.
    Uses Equirectangular approximation suitable for building-scale polygons.
    """
    if not coords:
        return []
    
    avg_lat = sum(c[0] for c in coords) / len(coords)
    avg_lon = sum(c[1] for c in coords) / len(coords)
    
    r_earth = 6371000.0  # Earth radius in meters
    lat_rad = math.radians(avg_lat)
    
    meter_coords = []
    for lat, lon in coords:
        dlat = math.radians(lat - avg_lat)
        dlon = math.radians(lon - avg_lon)
        y = dlat * r_earth
        x = dlon * r_earth * math.cos(lat_rad)
        meter_coords.append((x, y))
        
    return meter_coords
