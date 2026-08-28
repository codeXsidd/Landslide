"""NER-LDI Hydrography Service — loads and caches OSM waterway data."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "processed" / "hydrography"
RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw" / "hydrography"
CACHE_FILE = CACHE_DIR / "ner_waterways.geojson"
METADATA_FILE = CACHE_DIR / "ner_waterways_metadata.json"

NER_BBOX = {"west": 88.0, "south": 25.0, "east": 97.0, "north": 29.5}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OVERPASS_QUERY = """
[out:json][timeout:90];
(
  way["waterway"="river"]({south},{west},{north},{east});
  way["waterway"="canal"]({south},{west},{north},{east});
  way["waterway"="stream"]["name"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
""".format(**NER_BBOX)


def _osm_to_geojson(data: dict) -> dict:
    """Convert Overpass JSON response to GeoJSON FeatureCollection."""
    nodes = {}
    ways = []

    for el in data.get("elements", []):
        if el["type"] == "node":
            nodes[el["id"]] = (el["lon"], el["lat"])
        elif el["type"] == "way":
            ways.append(el)

    features = []
    for way in ways:
        coords = [nodes[nid] for nid in way.get("nodes", []) if nid in nodes]
        if len(coords) < 2:
            continue

        tags = way.get("tags", {})
        waterway_type = tags.get("waterway", tags.get("water", "unknown"))
        name = tags.get("name", tags.get("name:en", ""))

        feature = {
            "type": "Feature",
            "properties": {
                "osm_id": way["id"],
                "name": name,
                "waterway_type": waterway_type,
                "source": "OpenStreetMap",
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}


def _validate_geojson(geojson: dict) -> dict:
    """Basic validation of GeoJSON structure."""
    valid_features = []
    invalid_count = 0

    for f in geojson.get("features", []):
        geom = f.get("geometry", {})
        coords = geom.get("coordinates", [])

        if geom.get("type") != "LineString":
            invalid_count += 1
            continue
        if len(coords) < 2:
            invalid_count += 1
            continue

        all_valid = True
        for c in coords:
            if not (isinstance(c, (list, tuple)) and len(c) >= 2):
                all_valid = False
                break
            lon, lat = c[0], c[1]
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                all_valid = False
                break

        if all_valid:
            valid_features.append(f)
        else:
            invalid_count += 1

    geojson["features"] = valid_features
    return {"valid": len(valid_features), "invalid": invalid_count}


def _write_metadata(geojson: dict, retrieval_time: str, from_cache: bool = False) -> None:
    """Write metadata JSON alongside the GeoJSON."""
    rivers = sum(1 for f in geojson["features"] if f["properties"]["waterway_type"] == "river")
    streams = sum(1 for f in geojson["features"] if f["properties"]["waterway_type"] == "stream")
    canals = sum(1 for f in geojson["features"] if f["properties"]["waterway_type"] == "canal")

    metadata = {
        "source": "OpenStreetMap",
        "retrieval_timestamp": retrieval_time,
        "bounding_area": NER_BBOX,
        "feature_count": len(geojson["features"]),
        "breakdown": {"rivers": rivers, "streams": streams, "canals": canals},
        "geometry_types": ["LineString"],
        "tags_used": ["waterway=river", "waterway=stream", "waterway=canal", "natural=water,water=river"],
        "crs": "EPSG:4326",
        "is_simulated": False,
        "from_cache": from_cache,
    }
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


async def fetch_from_overpass() -> Optional[dict]:
    """Download waterway data from Overpass API."""
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                OVERPASS_URL,
                data={"data": OVERPASS_QUERY},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


async def refresh_waterways() -> dict:
    """Fetch fresh data from Overpass, validate, cache, and return GeoJSON."""
    raw_data = await fetch_from_overpass()
    if raw_data is None:
        return {"error": "Overpass API unavailable"}

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"overpass_response_{int(time.time())}.json"
    raw_path.write_text(json.dumps(raw_data), encoding="utf-8")

    geojson = _osm_to_geojson(raw_data)
    validation = _validate_geojson(geojson)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(geojson), encoding="utf-8")

    retrieval_time = datetime.now(timezone.utc).isoformat()
    _write_metadata(geojson, retrieval_time, from_cache=False)

    return {
        "geojson": geojson,
        "source": "overpass_live",
        "retrieval_timestamp": retrieval_time,
        "validation": validation,
    }


def load_cached() -> Optional[dict]:
    """Load previously cached GeoJSON from disk."""
    if not CACHE_FILE.exists():
        return None
    try:
        geojson = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if geojson.get("type") == "FeatureCollection" and geojson.get("features"):
            return geojson
    except (json.JSONDecodeError, OSError):
        pass
    return None


def load_metadata() -> Optional[dict]:
    """Load metadata if available."""
    if not METADATA_FILE.exists():
        return None
    try:
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


async def get_waterways(force_refresh: bool = False) -> dict:
    """Main entry point: return cached data, or fetch if force_refresh=True."""
    cached = load_cached()

    if not force_refresh:
        if cached:
            meta = load_metadata()
            return {
                "geojson": cached,
                "source": "cached",
                "retrieval_timestamp": meta.get("retrieval_timestamp", "unknown") if meta else "unknown",
                "feature_count": len(cached.get("features", [])),
            }
        return {"geojson": {"type": "FeatureCollection", "features": []}, "source": "unavailable", "feature_count": 0}

    result = await refresh_waterways()
    if "error" in result:
        if cached:
            meta = load_metadata()
            return {
                "geojson": cached,
                "source": "cached_fallback",
                "retrieval_timestamp": meta.get("retrieval_timestamp", "unknown") if meta else "unknown",
                "feature_count": len(cached.get("features", [])),
                "warning": "Overpass unavailable, serving cached data",
            }
        return {"geojson": {"type": "FeatureCollection", "features": []}, "source": "unavailable", "feature_count": 0}

    return {
        "geojson": result["geojson"],
        "source": result["source"],
        "retrieval_timestamp": result["retrieval_timestamp"],
        "feature_count": len(result["geojson"].get("features", [])),
    }
