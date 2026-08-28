"""NER-LDI Village Connectivity and Isolation Engine."""
import json, math
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VILLAGES_PATH = PROJECT_ROOT / "data" / "processed" / "villages" / "ner_villages.geojson"
INFRA_PATH = PROJECT_ROOT / "data" / "processed" / "infrastructure" / "ner_infrastructure.geojson"


def _load_villages():
    if not VILLAGES_PATH.exists():
        return []
    with open(VILLAGES_PATH) as f:
        return json.load(f).get("features", [])


def _load_infrastructure():
    if not INFRA_PATH.exists():
        return []
    with open(INFRA_PATH) as f:
        return json.load(f).get("features", [])


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def compute_village_isolation(lat: float, lon: float, road_blockage_prob: float, radius_km: float = 10.0) -> Dict:
    """Compute village isolation risk from a potential road blockage."""
    villages = _load_villages()
    infrastructure = _load_infrastructure()
    affected_villages = []
    total_population = 0

    for v in villages:
        props = v.get("properties", {})
        geom = v.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])

        if dist <= radius_km:
            isolation_prob = road_blockage_prob * max(0, 1.0 - dist / radius_km)
            pop = props.get("population", 0)
            affected_villages.append({
                "village_id": props.get("village_id"),
                "name": props.get("name"),
                "distance_km": round(dist, 2),
                "population": pop,
                "isolation_probability": round(isolation_prob, 4),
                "has_health_facility": props.get("has_health_facility", False),
            })
            if isolation_prob > 0.3:
                total_population += pop

    # Hospital access
    hospitals_nearby = []
    for inf in infrastructure:
        props = inf.get("properties", {})
        if props.get("type") != "hospital":
            continue
        geom = inf.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])
        if dist <= radius_km * 2:
            hospitals_nearby.append({
                "name": props.get("name"),
                "distance_km": round(dist, 2),
                "beds": props.get("beds", 0),
                "access_degraded": dist <= radius_km and road_blockage_prob > 0.4
            })

    affected_villages.sort(key=lambda x: x["isolation_probability"], reverse=True)
    max_isolation = affected_villages[0]["isolation_probability"] if affected_villages else 0

    return {
        "village_isolation_probability": round(max_isolation, 4),
        "villages_at_risk": affected_villages[:10],
        "population_affected": total_population,
        "hospitals_nearby": hospitals_nearby,
        "hospital_access_degraded": any(h["access_degraded"] for h in hospitals_nearby),
        "emergency_access_loss": road_blockage_prob > 0.6,
        "alternate_route_available": road_blockage_prob < 0.8,
    }


def compute_infrastructure_exposure(lat: float, lon: float, risk_score: float, radius_km: float = 5.0) -> Dict:
    """Compute infrastructure exposure at risk location."""
    infrastructure = _load_infrastructure()
    villages = _load_villages()
    exposed = []
    critical = []

    for inf in infrastructure:
        props = inf.get("properties", {})
        geom = inf.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])
        if dist <= radius_km:
            item = {"type": props.get("type"), "name": props.get("name"), "distance_km": round(dist, 2)}
            exposed.append(item)
            if props.get("type") in ("hospital", "school", "emergency_facility"):
                critical.append(item)

    pop_exposed = sum(v["properties"].get("population", 0) for v in villages
                      if v.get("geometry", {}).get("type") == "Point" and
                      _haversine(lat, lon, v["geometry"]["coordinates"][1], v["geometry"]["coordinates"][0]) <= radius_km)

    exposure_score = min(1.0, (len(critical) * 0.2 + pop_exposed / 10000) * risk_score)

    return {
        "exposure_score": round(exposure_score, 4),
        "assets_affected": exposed,
        "critical_assets": critical,
        "population_exposed": pop_exposed,
    }
