"""NER-LDI Road Network Impact Engine."""
import json
from pathlib import Path
from typing import Dict, List
import math

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ROADS_PATH = PROJECT_ROOT / "data" / "processed" / "roads" / "ner_roads.geojson"


def _load_roads():
    if not ROADS_PATH.exists():
        return []
    with open(ROADS_PATH) as f:
        data = json.load(f)
    return data.get("features", [])


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def compute_road_impact(lat: float, lon: float, risk_score: float, radius_km: float = 5.0) -> Dict:
    """Compute road impact for a landslide risk location."""
    roads = _load_roads()
    affected_roads = []

    for road in roads:
        props = road.get("properties", {})
        geom = road.get("geometry", {})
        coords = geom.get("coordinates", [])

        # Check if any road segment is within radius
        min_dist = float("inf")
        if geom.get("type") == "LineString":
            for c in coords:
                d = _haversine(lat, lon, c[1], c[0])
                min_dist = min(min_dist, d)
        elif geom.get("type") == "MultiLineString":
            for line in coords:
                for c in line:
                    d = _haversine(lat, lon, c[1], c[0])
                    min_dist = min(min_dist, d)

        if min_dist <= radius_km:
            blockage_prob = risk_score * max(0, 1.0 - min_dist / radius_km) * 0.8
            affected_roads.append({
                "road_id": props.get("road_id"),
                "name": props.get("name"),
                "road_type": props.get("road_type"),
                "distance_km": round(min_dist, 2),
                "blockage_probability": round(blockage_prob, 4),
                "is_critical": props.get("road_type") in ("NH", "SH"),
                "length_km": props.get("length_km", 0),
            })

    affected_roads.sort(key=lambda x: x["blockage_probability"], reverse=True)
    max_blockage = affected_roads[0]["blockage_probability"] if affected_roads else 0

    # Alternative routes
    alternatives = [r for r in affected_roads if r["blockage_probability"] < 0.3]

    return {
        "road_blockage_probability": round(max_blockage, 4),
        "road_risk_level": "HIGH" if max_blockage > 0.6 else "MODERATE" if max_blockage > 0.3 else "LOW",
        "affected_roads": affected_roads[:10],
        "critical_roads_at_risk": [r for r in affected_roads if r["is_critical"]],
        "alternative_routes": len(alternatives),
        "response_accessibility": "DEGRADED" if max_blockage > 0.5 else "NORMAL",
    }
