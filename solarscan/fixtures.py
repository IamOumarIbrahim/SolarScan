import json
import os
from solarscan.osm import query_osm_building

def capture_fixture(lat, lon, out_path):
    """
    Calls query_osm_building(lat, lon) and writes the resulting dict (including
    query_lat and query_lon) as JSON to out_path. Returns the captured dict.
    """
    result = query_osm_building(lat, lon)
    fixture_data = {
        "building_id": result["building_id"],
        "polygon_coords": result["polygon_coords"],
        "obstruction_area": result.get("obstruction_area", 0.0),
        "query_lat": lat,
        "query_lon": lon
    }
    
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixture_data, f, indent=2)
        
    return fixture_data

def load_fixture(path):
    """
    Loads JSON fixture from path and returns dict matching query_osm_building shape
    plus query_lat and query_lon.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    polygon_coords = [tuple(pt) for pt in data["polygon_coords"]]
    return {
        "building_id": data["building_id"],
        "polygon_coords": polygon_coords,
        "obstruction_area": data.get("obstruction_area", 0.0),
        "query_lat": data["query_lat"],
        "query_lon": data["query_lon"]
    }
