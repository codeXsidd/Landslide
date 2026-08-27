"""
NER-LDI MVP — Impact / Consequence Engine
Calculates cascading consequences of a landslide event.

Uses:
- Synthetic road network (NetworkX graph from GeoJSON)
- Synthetic village data
- Synthetic infrastructure data
- Synthetic population exposure

Outputs:
- road_blockage_probability
- village_isolation_probability
- population_exposed
- hospital_accessibility_degraded
- alternate_route_available
"""

import json
import math
import os
from datetime import UTC, datetime
from typing import Any

import networkx as nx


# ── Load Synthetic Geospatial Data ────────────────────────────────

_roads_graph: nx.Graph | None = None
_villages: list[dict] | None = None
_infrastructure: list[dict] | None = None
_population: list[dict] | None = None


def _load_roads_graph() -> nx.Graph:
    global _roads_graph
    if _roads_graph is not None:
        return _roads_graph

    G = nx.Graph()
    roads_path = "data/processed/roads/ner_roads.geojson"
    if not os.path.exists(roads_path):
        return G

    with open(roads_path) as f:
        gj = json.load(f)

    for feat in gj.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        road_id = props.get("road_id", "UNKNOWN")
        road_type = props.get("road_type", "unknown")
        length_km = props.get("length_km", 50)

        if geom.get("type") == "LineString":
            coords = geom.get("coordinates", [])
            if len(coords) >= 2:
                # Nodes = endpoints
                start = (round(coords[0][0], 3), round(coords[0][1], 3))
                end = (round(coords[-1][0], 3), round(coords[-1][1], 3))
                G.add_node(start, node_type="junction")
                G.add_node(end, node_type="junction")
                G.add_edge(start, end,
                           road_id=road_id,
                           road_type=road_type,
                           length_km=length_km,
                           weight=length_km)

    _roads_graph = G
    return G


def _load_villages() -> list[dict]:
    global _villages
    if _villages is not None:
        return _villages
    path = "data/processed/villages/ner_villages.geojson"
    if not os.path.exists(path):
        return []
    with open(path) as f:
        gj = json.load(f)
    _villages = [
        {**feat["properties"],
         "lat": feat["geometry"]["coordinates"][1],
         "lon": feat["geometry"]["coordinates"][0]}
        for feat in gj.get("features", [])
    ]
    return _villages


def _load_infrastructure() -> list[dict]:
    global _infrastructure
    if _infrastructure is not None:
        return _infrastructure
    path = "data/processed/infrastructure/ner_infrastructure.geojson"
    if not os.path.exists(path):
        return []
    with open(path) as f:
        gj = json.load(f)
    _infrastructure = [
        {**feat["properties"],
         "lat": feat["geometry"]["coordinates"][1],
         "lon": feat["geometry"]["coordinates"][0]}
        for feat in gj.get("features", [])
    ]
    return _infrastructure


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def _find_nearby_villages(lat: float, lon: float, radius_km: float = 30) -> list[dict]:
    villages = _load_villages()
    return [
        v for v in villages
        if _haversine_km(lat, lon, v["lat"], v["lon"]) <= radius_km
    ]


def _find_nearby_hospitals(lat: float, lon: float, radius_km: float = 80) -> list[dict]:
    infra = _load_infrastructure()
    return [
        h for h in infra
        if h.get("type") == "hospital" and _haversine_km(lat, lon, h["lat"], h["lon"]) <= radius_km
    ]


def _find_nearby_roads(lat: float, lon: float, radius_km: float = 15) -> list[dict]:
    roads_path = "data/processed/roads/ner_roads.geojson"
    if not os.path.exists(roads_path):
        return []
    with open(roads_path) as f:
        gj = json.load(f)
    nearby = []
    for feat in gj.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        if geom.get("type") == "LineString":
            coords = geom.get("coordinates", [])
            if coords:
                mid = coords[len(coords)//2]
                d = _haversine_km(lat, lon, mid[1], mid[0])
                if d <= radius_km:
                    nearby.append({**props, "distance_km": round(d, 2)})
    return nearby


def compute_impact(
    location_id: str,
    lat: float,
    lon: float,
    risk_score: float,
    scenario_rainfall_factor: float = 1.0,
) -> dict[str, Any]:
    """
    Compute cascading impact of a potential landslide.

    Args:
        location_id: Location identifier
        lat, lon: Location coordinates
        risk_score: ML risk probability [0,1]
        scenario_rainfall_factor: Rainfall multiplier for what-if scenarios

    Returns:
        Full impact assessment dictionary
    """
    # Adjust risk for scenario rainfall
    effective_risk = min(1.0, risk_score * (1.0 + (scenario_rainfall_factor - 1.0) * 0.6))

    # ── Road Analysis ──────────────────────────────────────────────
    nearby_roads = _find_nearby_roads(lat, lon, radius_km=20)
    G = _load_roads_graph()

    road_blockage_prob = min(0.98, effective_risk * 0.85 + (len(nearby_roads) > 0) * 0.05)

    national_highways = [r for r in nearby_roads if r.get("road_type") == "national_highway"]
    district_roads = [r for r in nearby_roads if r.get("road_type") == "district_road"]

    # Count alternate routes (simple heuristic: > 1 path in graph)
    alternate_routes = max(0, len(nearby_roads) - 1)
    has_alternate_route = alternate_routes > 0

    # ── Village Analysis ───────────────────────────────────────────
    nearby_villages = _find_nearby_villages(lat, lon, radius_km=30)
    total_village_pop = sum(v.get("population", 0) for v in nearby_villages)

    # Isolation probability depends on road blockage and whether villages are off-grid
    isolated_villages = [v for v in nearby_villages if v.get("road_connectivity") == "isolated"]
    connected_villages = [v for v in nearby_villages if v.get("road_connectivity") != "isolated"]

    # Isolation probability: higher if only one road exists
    if not has_alternate_route:
        isolation_prob = min(0.95, road_blockage_prob * 0.90)
    else:
        isolation_prob = min(0.70, road_blockage_prob * 0.50)

    # Population exposed (within influence zone)
    population_exposed = int(total_village_pop * effective_risk * 0.6)

    # ── Hospital Analysis ──────────────────────────────────────────
    nearby_hospitals = _find_nearby_hospitals(lat, lon, radius_km=80)
    hospital_access_degraded = road_blockage_prob > 0.6 and len(nearby_hospitals) > 0

    # Helicopter accessibility
    helicopter_capable = any(h.get("helicopter_pad") for h in nearby_hospitals)

    # ── Bridges ────────────────────────────────────────────────────
    infra = _load_infrastructure()
    nearby_bridges = [
        b for b in infra
        if b.get("type") == "bridge"
        and _haversine_km(lat, lon, b["lat"], b["lon"]) <= 15
    ]
    critical_bridge_at_risk = any(b.get("critical") for b in nearby_bridges)

    # ── Impact Level ───────────────────────────────────────────────
    impact_score = (
        road_blockage_prob * 0.30
        + isolation_prob * 0.30
        + min(population_exposed / 10000, 1.0) * 0.20
        + int(hospital_access_degraded) * 0.20
    )

    if impact_score >= 0.70:
        impact_level = "CATASTROPHIC"
    elif impact_score >= 0.50:
        impact_level = "SEVERE"
    elif impact_score >= 0.30:
        impact_level = "MODERATE"
    else:
        impact_level = "MINOR"

    return {
        "location_id": location_id,
        "latitude": lat,
        "longitude": lon,
        "risk_score_used": round(effective_risk, 3),
        "scenario_rainfall_factor": scenario_rainfall_factor,
        "road_blockage_probability": round(road_blockage_prob, 3),
        "village_isolation_probability": round(isolation_prob, 3),
        "population_exposed": population_exposed,
        "hospital_accessibility_degraded": hospital_access_degraded,
        "alternate_route_available": has_alternate_route,
        "alternate_route_count": alternate_routes,
        "nearby_road_count": len(nearby_roads),
        "national_highways_affected": [r.get("name") for r in national_highways],
        "district_roads_affected": [r.get("road_id") for r in district_roads],
        "nearby_village_count": len(nearby_villages),
        "villages_at_risk": [
            {"village_id": v.get("village_id"), "name": v.get("name"),
             "population": v.get("population"), "state": v.get("state")}
            for v in nearby_villages[:10]
        ],
        "nearby_hospitals": [
            {"name": h.get("name"), "beds": h.get("beds"),
             "has_emergency": h.get("has_emergency"), "helicopter_pad": h.get("helicopter_pad")}
            for h in nearby_hospitals[:5]
        ],
        "critical_bridge_at_risk": critical_bridge_at_risk,
        "helicopter_accessible": helicopter_capable,
        "impact_score": round(impact_score, 3),
        "impact_level": impact_level,
        "is_synthetic_data": True,
        "data_warning": "Infrastructure data is SYNTHETIC DEMO. Not real OSM data.",
        "computed_at": datetime.now(UTC).isoformat(),
    }
