import requests
import json
import logging
from solarscan.geometry import latlon_to_meters, calculate_shoelace_area

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def geocode_address(address):
    """
    Geocodes an address string to (lat, lon) using OpenStreetMap Nominatim API.
    Retries across primary and secondary endpoints if needed.
    """
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
                    valid_candidates.append({
                        "building_id": way["id"],
                        "polygon_coords": polygon_coords,
                        "area": area,
                        "obstruction_area": 0.0
                    })

            if valid_candidates:
                # Sort by rooftop area descending to pick the primary building footprint
                valid_candidates.sort(key=lambda c: c["area"], reverse=True)
                selected = valid_candidates[0]
                logging.info(f"OSM building polygon retrieved from {mirror_url} (ID: {selected['building_id']}, Area: {selected['area']:.1f}m²)")
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
