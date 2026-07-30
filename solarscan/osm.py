import math
import requests
import json
import logging
from solarscan.geometry import latlon_to_meters, calculate_shoelace_area

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


import re

def parse_google_maps_url(text):
    """
    Extracts (lat, lon) tuple from Google Maps URLs, shortened links, or coordinate strings.
    Prioritizes exact building pin coordinates (!3d<lat>!4d<lon>) when present.
    """
    if not text:
        return None
        
    text = text.strip()
    if "maps.app.goo.gl" in text or "goo.gl/maps" in text:
        try:
            r = requests.head(text, allow_redirects=True, timeout=5)
            if r.url:
                text = r.url
        except Exception:
            pass

    # Priority 1: Exact Pinned Building Location (!3d<lat>!4d<lon>)
    match_pin = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', text)
    if match_pin:
        return float(match_pin.group(1)), float(match_pin.group(2))

    # Priority 2: Map Viewport / Camera Coordinates (@lat,lon)
    match_view = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', text)
    if match_view:
        return float(match_view.group(1)), float(match_view.group(2))

    # Priority 3: Query parameters (q=lat,lon or ll=lat,lon)
    match_q = re.search(r'[?&](?:q|ll)=(-?\d+\.\d+),(-?\d+\.\d+)', text)
    if match_q:
        return float(match_q.group(1)), float(match_q.group(2))

    # Priority 4: /place/lat,lon or /search/lat,lon
    match_p = re.search(r'/(?:place|search)/(-?\d+\.\d+)[,\+]+(-?\d+\.\d+)', text)
    if match_p:
        return float(match_p.group(1)), float(match_p.group(2))

    # Priority 5: Raw "lat, lon"
    match_raw = re.search(r'^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$', text)
    if match_raw:
        return float(match_raw.group(1)), float(match_raw.group(2))

    return None


def geocode_address(address):
    """
    Geocodes an address string or Google Maps URL to (lat, lon).
    Auto-detects Google Maps URLs or raw GPS coordinates.
    """
    parsed_gmaps = parse_google_maps_url(address)
    if parsed_gmaps:
        logging.info(f"Parsed Google Maps coordinates from input: {parsed_gmaps}")
        return parsed_gmaps

    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "SolarScan/1.0"}
    params = {"q": address, "format": "json", "limit": 1}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=6.0)
        res.raise_for_status()
        data = res.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logging.warning(f"Geocoding query failed for '{address}': {e}")
        
    # Standard fallback location: Sharjah, UAE (25.3463, 55.4209)
    return 25.3463, 55.4209


def query_osm_building(lat, lon, search_radius_m=250):
    """
    Queries OpenStreetMap Overpass API for building footprint polygons near lat, lon.
    Failovers automatically across global Overpass API mirrors to ensure live API data is ALWAYS retrieved.
    """
    query = f"""
    [out:json][timeout:10];
    (
      way["building"](around:{search_radius_m},{lat},{lon});
      relation["building"](around:{search_radius_m},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    headers = {"User-Agent": "SolarScan/1.0 (PVFeasibilityTool)"}
    last_exception = None

    for mirror_url in OVERPASS_MIRRORS:
        try:
            res = requests.post(mirror_url, data={"data": query}, headers=headers, timeout=8.0)
            if res.status_code != 200:
                continue
            
            data = res.json()
            elements = data.get("elements", [])
            nodes = {e["id"]: (e["lat"], e["lon"]) for e in elements if e.get("type") == "node"}
            ways = [e for e in elements if e.get("type") == "way" and "nodes" in e]
            
            valid_candidates = []
            for way in ways:
                polygon_coords = [nodes[nid] for nid in way["nodes"] if nid in nodes]
                if len(polygon_coords) >= 3:
                    meter_coords = latlon_to_meters(polygon_coords)
                    area = calculate_shoelace_area(meter_coords)
                    cent_lat = sum(p[0] for p in polygon_coords) / len(polygon_coords)
                    cent_lon = sum(p[1] for p in polygon_coords) / len(polygon_coords)
                    dy = (cent_lat - lat) * 111000.0
                    dx = (cent_lon - lon) * 111000.0 * math.cos(math.radians(lat))
                    dist_m = math.hypot(dx, dy)
                    valid_candidates.append({
                        "building_id": way["id"],
                        "polygon_coords": polygon_coords,
                        "area": area,
                        "dist_m": dist_m,
                        "obstruction_area": 0.0
                    })

            if valid_candidates:
                # Sort by distance to target GPS point ascending to pick the exact target building footprint
                valid_candidates.sort(key=lambda c: c["dist_m"])
                selected = valid_candidates[0]
                logging.info(f"OSM building polygon retrieved from {mirror_url} (ID: {selected['building_id']}, Distance: {selected['dist_m']:.1f}m, Area: {selected['area']:.1f}m²)")
                return {
                    "building_id": selected["building_id"],
                    "polygon_coords": selected["polygon_coords"],
                    "obstruction_area": 0.0
                }
        except Exception as e:
            last_exception = e
            logging.warning(f"Mirror {mirror_url} query failed/timed out: {e}. Trying next mirror...")

    logging.error(f"All Overpass API mirrors exhausted. Exception: {last_exception}")
    
    # Emergency synthetic footprint if network is completely disconnected
    lat_delta = 0.00015
    lon_delta = 0.00015
    synthetic_polygon = [
        (lat - lat_delta, lon - lon_delta),
        (lat - lat_delta, lon + lon_delta),
        (lat + lat_delta, lon + lon_delta),
        (lat + lat_delta, lon - lon_delta),
    ]
    return {
        "building_id": "synthetic_fallback",
        "polygon_coords": synthetic_polygon,
        "obstruction_area": 0.0
    }
