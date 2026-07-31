import pytest


@pytest.fixture(autouse=True)
def deterministic_scan_inputs(monkeypatch):
    """Keep unit tests independent of geocoding and Overpass availability."""
    center_lat = 25.2893304
    center_lon = 55.4783103
    lat_delta = 0.00009
    lon_delta = 0.00015
    polygon = [
        (center_lat - lat_delta, center_lon - lon_delta),
        (center_lat - lat_delta, center_lon + lon_delta),
        (center_lat + lat_delta, center_lon + lon_delta),
        (center_lat + lat_delta, center_lon - lon_delta),
    ]

    monkeypatch.setattr(
        "solarscan.cli.geocode_address",
        lambda _address: (center_lat, center_lon),
    )
    monkeypatch.setattr(
        "solarscan.cli.query_osm_building",
        lambda _lat, _lon: {
            "building_id": "test-fixture",
            "polygon_coords": polygon,
            "obstruction_area": 0.0,
        },
    )
