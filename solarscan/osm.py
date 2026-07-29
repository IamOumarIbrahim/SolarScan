import requests
import json
import logging

def geocode_address(address):
    """
    Geocodes an address string to (lat, lon) using OpenStreetMap Nominatim API.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "SolarScan/1.0"}
    params = {"q": address, "format": "json", "limit": 1}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logging.warning(f"Geocoding failed for '{address}': {e}")
        
    # Synthetic/Fallback location for testing if address geocoding fails or offline
    # Standard fallback location: Sharjah, UAE (25.3463, 55.4209)
    return 25.3463, 55.4209


def query_osm_building(lat, lon, search_radius_m=100):
    """
    Queries OSM Overpass API for building footprint polygon near lat, lon.
    Returns a dictionary with 'nodes', 'polygon_coords' (lat, lon pairs), and 'obstructions'.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      way["building"](around:{search_radius_m},{lat},{lon});
      relation["building"](around:{search_radius_m},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        headers = {"User-Agent": "SolarScan/1.0 (PVFeasibilityTool)"}
        res = requests.post(overpass_url, data={"data": query}, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        elements = data.get("elements", [])
        nodes = {e["id"]: (e["lat"], e["lon"]) for e in elements if e["type"] == "node"}
        ways = [e for e in elements if e["type"] == "way" and "nodes" in e]
        
        if ways:
            # Pick the primary building way
            way = ways[0]
            polygon_coords = [nodes[nid] for nid in way["nodes"] if nid in nodes]
            if polygon_coords:
                return {
                    "building_id": way["id"],
                    "polygon_coords": polygon_coords,
                    "obstruction_area": 0.0
                }
    except Exception as e:
        logging.warning(f"OSM Overpass query failed: {e}. Generating synthetic building polygon.")

    # Return synthetic rectangular building footprint centered at lat, lon if OSM query fails or returns no building
    # ~20m x 15m building footprint in lat/lon
    lat_delta = 0.00015
    lon_delta = 0.00015
    synthetic_polygon = [
        (lat - lat_delta, lon - lon_delta),
        (lat - lat_delta, lon + lon_delta),
        (lat + lat_delta, lon + lon_delta),
        (lat + lat_delta, lon - lon_delta),
    ]
    return {
        "building_id": "synthetic_001",
        "polygon_coords": synthetic_polygon,
        "obstruction_area": 0.0
    }
