"""
NER-LDI MVP — Synthetic Geospatial Data Generator
Creates clearly labelled SYNTHETIC demo roads, villages, hospitals, schools, bridges
for Northeast India. These are NOT real OSM data.

SYNTHETIC DATA — FOR DEMONSTRATION PURPOSES ONLY
"""
import json
import os
import random
import math

random.seed(42)

# NER state capitals and major hubs (approximate real coordinates for realism)
NER_ANCHORS = [
    {"name": "Guwahati", "lat": 26.144, "lon": 91.736, "state": "Assam", "pop": 957352},
    {"name": "Shillong", "lat": 25.578, "lon": 91.893, "state": "Meghalaya", "pop": 143229},
    {"name": "Aizawl", "lat": 23.727, "lon": 92.717, "state": "Mizoram", "pop": 293416},
    {"name": "Kohima", "lat": 25.670, "lon": 94.110, "state": "Nagaland", "pop": 99039},
    {"name": "Imphal", "lat": 24.817, "lon": 93.950, "state": "Manipur", "pop": 268243},
    {"name": "Agartala", "lat": 23.831, "lon": 91.286, "state": "Tripura", "pop": 438724},
    {"name": "Itanagar", "lat": 27.084, "lon": 93.606, "state": "Arunachal Pradesh", "pop": 59490},
    {"name": "Gangtok", "lat": 27.329, "lon": 88.612, "state": "Sikkim", "pop": 100286},
    {"name": "Dibrugarh", "lat": 27.480, "lon": 94.912, "state": "Assam", "pop": 154296},
    {"name": "Silchar", "lat": 24.826, "lon": 92.797, "state": "Assam", "pop": 228985},
    {"name": "Jorhat", "lat": 26.752, "lon": 94.203, "state": "Assam", "pop": 153889},
    {"name": "Tezpur", "lat": 26.633, "lon": 92.795, "state": "Assam", "pop": 87594},
    {"name": "Tura", "lat": 25.512, "lon": 90.208, "state": "Meghalaya", "pop": 73000},
    {"name": "Churachandpur", "lat": 24.333, "lon": 93.680, "state": "Manipur", "pop": 56000},
    {"name": "Lunglei", "lat": 22.888, "lon": 92.736, "state": "Mizoram", "pop": 51000},
    {"name": "Dimapur", "lat": 25.909, "lon": 93.727, "state": "Nagaland", "pop": 122834},
    {"name": "Pasighat", "lat": 28.067, "lon": 95.333, "state": "Arunachal Pradesh", "pop": 20000},
    {"name": "Dharmanagar", "lat": 24.375, "lon": 92.163, "state": "Tripura", "pop": 52000},
]

# ── ROADS ─────────────────────────────────────────────────────────
def generate_roads():
    roads = []
    road_id = 1
    
    # Major national highways connecting anchor cities
    highway_pairs = [
        (0, 1, "NH-6", "national_highway"),   # Guwahati-Shillong
        (0, 6, "NH-15", "national_highway"),   # Guwahati-Itanagar
        (0, 8, "NH-37", "national_highway"),   # Guwahati-Dibrugarh
        (0, 9, "NH-44", "national_highway"),   # Guwahati-Silchar
        (0, 11, "NH-52", "national_highway"),  # Guwahati-Tezpur
        (4, 3, "NH-2", "national_highway"),    # Imphal-Kohima
        (5, 9, "NH-44S", "national_highway"),  # Agartala-Silchar
        (1, 12, "NH-62", "state_highway"),     # Shillong-Tura
        (2, 14, "NH-54", "state_highway"),     # Aizawl-Lunglei
        (3, 15, "NH-29", "state_highway"),     # Kohima-Dimapur
        (8, 16, "NH-52B", "state_highway"),    # Dibrugarh-Pasighat
        (7, 0, "NH-10", "national_highway"),   # Gangtok-Guwahati
    ]
    
    for i, (a_idx, b_idx, road_name, road_type) in enumerate(highway_pairs):
        a = NER_ANCHORS[a_idx]
        b = NER_ANCHORS[b_idx]
        
        # Create intermediate waypoints for realistic road geometry
        n_waypoints = random.randint(3, 6)
        coords = [[a["lon"], a["lat"]]]
        for j in range(1, n_waypoints):
            t = j / n_waypoints
            # Add slight sinusoidal deviation to simulate mountain roads
            mid_lon = a["lon"] + t * (b["lon"] - a["lon"]) + random.gauss(0, 0.15)
            mid_lat = a["lat"] + t * (b["lat"] - a["lat"]) + random.gauss(0, 0.15)
            coords.append([round(mid_lon, 6), round(mid_lat, 6)])
        coords.append([[b["lon"], b["lat"]]])
        coords[-1] = [b["lon"], b["lat"]]
        
        # Approximate length
        dx = (b["lon"] - a["lon"]) * 111 * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
        dy = (b["lat"] - a["lat"]) * 111
        length_km = round(math.sqrt(dx**2 + dy**2), 1)
        
        road = {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "road_id": f"ROAD_{road_id:03d}",
                "name": road_name,
                "road_type": road_type,
                "surface": "paved",
                "lanes": 2 if road_type == "national_highway" else 1,
                "length_km": length_km,
                "from_city": a["name"],
                "to_city": b["name"],
                "from_state": a["state"],
                "to_state": b["state"],
                "landslide_risk_zone": True if length_km > 100 else False,
                "is_synthetic": True,
                "data_source": "SYNTHETIC_DEMO",
            }
        }
        roads.append(road)
        road_id += 1
    
    # Add smaller district roads
    for state in set(a["state"] for a in NER_ANCHORS):
        state_anchors = [a for a in NER_ANCHORS if a["state"] == state]
        for i in range(min(3, len(state_anchors))):
            anchor = state_anchors[i % len(state_anchors)]
            for _ in range(2):
                dist = random.uniform(20, 60)
                angle = random.uniform(0, 2 * math.pi)
                end_lon = anchor["lon"] + dist / (111 * math.cos(math.radians(anchor["lat"]))) * math.cos(angle)
                end_lat = anchor["lat"] + dist / 111 * math.sin(angle)
                
                coords = [[anchor["lon"], anchor["lat"]], [round(end_lon, 6), round(end_lat, 6)]]
                road = {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {
                        "road_id": f"ROAD_{road_id:03d}",
                        "name": f"District Road {road_id}",
                        "road_type": "district_road",
                        "surface": "gravel",
                        "lanes": 1,
                        "length_km": round(dist, 1),
                        "from_city": anchor["name"],
                        "to_city": f"Village_{road_id}",
                        "from_state": state,
                        "to_state": state,
                        "landslide_risk_zone": True,
                        "is_synthetic": True,
                        "data_source": "SYNTHETIC_DEMO",
                    }
                }
                roads.append(road)
                road_id += 1
    
    return {
        "type": "FeatureCollection",
        "metadata": {
            "data_type": "SYNTHETIC_DEMO",
            "warning": "THIS IS SYNTHETIC DATA FOR DEMONSTRATION ONLY. Not real OSM data.",
            "total_roads": len(roads),
            "generated_at": "2026-08-27T10:00:00Z",
        },
        "features": roads
    }

# ── VILLAGES ──────────────────────────────────────────────────────
def generate_villages():
    villages = []
    village_id = 1
    
    # State-based village distributions (realistic for NER)
    state_configs = {
        "Assam": {"count": 25, "lat_range": (24.1, 27.9), "lon_range": (89.7, 95.9), "avg_pop": 1200},
        "Arunachal Pradesh": {"count": 20, "lat_range": (26.6, 29.4), "lon_range": (91.5, 97.4), "avg_pop": 350},
        "Meghalaya": {"count": 12, "lat_range": (25.0, 26.1), "lon_range": (89.8, 92.7), "avg_pop": 800},
        "Nagaland": {"count": 10, "lat_range": (25.2, 26.9), "lon_range": (93.3, 95.2), "avg_pop": 600},
        "Manipur": {"count": 10, "lat_range": (23.8, 25.6), "lon_range": (93.0, 94.7), "avg_pop": 700},
        "Mizoram": {"count": 8, "lat_range": (21.9, 24.4), "lon_range": (92.2, 93.3), "avg_pop": 400},
        "Tripura": {"count": 8, "lat_range": (22.9, 24.4), "lon_range": (91.1, 92.6), "avg_pop": 900},
        "Sikkim": {"count": 5, "lat_range": (27.0, 28.0), "lon_range": (88.0, 88.8), "avg_pop": 300},
    }
    
    for state, cfg in state_configs.items():
        for i in range(cfg["count"]):
            lat = random.uniform(*cfg["lat_range"])
            lon = random.uniform(*cfg["lon_range"])
            pop = max(50, int(random.gauss(cfg["avg_pop"], cfg["avg_pop"] * 0.4)))
            
            village = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
                "properties": {
                    "village_id": f"VIL_{village_id:04d}",
                    "name": f"{state[:3].upper()}_Village_{village_id:04d}",
                    "state": state,
                    "district": f"{state}_District_{(village_id % 5) + 1}",
                    "population": pop,
                    "households": max(10, pop // 5),
                    "elevation_approx_m": round(random.uniform(100, 2500), 1),
                    "has_health_facility": random.random() < 0.2,
                    "has_school": random.random() < 0.6,
                    "road_connectivity": random.choice(["connected", "connected", "isolated"]),
                    "landslide_exposure": random.choice(["HIGH", "HIGH", "MEDIUM", "LOW"]),
                    "is_synthetic": True,
                    "data_source": "SYNTHETIC_DEMO",
                }
            }
            villages.append(village)
            village_id += 1
    
    return {
        "type": "FeatureCollection",
        "metadata": {
            "data_type": "SYNTHETIC_DEMO",
            "warning": "THIS IS SYNTHETIC DATA FOR DEMONSTRATION ONLY.",
            "total_villages": len(villages),
            "generated_at": "2026-08-27T10:00:00Z",
        },
        "features": villages
    }

# ── INFRASTRUCTURE ─────────────────────────────────────────────────
def generate_infrastructure():
    features = []
    infra_id = 1
    
    # Hospitals near each anchor city
    for anchor in NER_ANCHORS:
        n_hospitals = random.randint(1, 3)
        for j in range(n_hospitals):
            offset_lat = random.gauss(0, 0.05)
            offset_lon = random.gauss(0, 0.05)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [
                    round(anchor["lon"] + offset_lon, 6),
                    round(anchor["lat"] + offset_lat, 6)
                ]},
                "properties": {
                    "infra_id": f"HOSP_{infra_id:03d}",
                    "type": "hospital",
                    "name": f"{anchor['name']} {'District ' if j > 0 else ''}Hospital",
                    "state": anchor["state"],
                    "beds": random.choice([30, 50, 100, 200, 300]) if j == 0 else random.choice([10, 20, 30]),
                    "has_emergency": j == 0,
                    "has_icu": j == 0 and anchor["pop"] > 100000,
                    "helicopter_pad": random.random() < 0.3,
                    "is_synthetic": True,
                    "data_source": "SYNTHETIC_DEMO",
                }
            })
            infra_id += 1
    
    # Schools (more numerous)
    for anchor in NER_ANCHORS:
        for j in range(random.randint(2, 5)):
            offset_lat = random.gauss(0, 0.1)
            offset_lon = random.gauss(0, 0.1)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [
                    round(anchor["lon"] + offset_lon, 6),
                    round(anchor["lat"] + offset_lat, 6)
                ]},
                "properties": {
                    "infra_id": f"SCH_{infra_id:03d}",
                    "type": "school",
                    "name": f"{anchor['name']} School {j+1}",
                    "state": anchor["state"],
                    "students": random.randint(100, 2000),
                    "is_synthetic": True,
                    "data_source": "SYNTHETIC_DEMO",
                }
            })
            infra_id += 1
    
    # Bridges (on major road segments - critical infrastructure)
    bridge_locations = [
        (26.15, 91.8, "Brahmaputra Bridge 1", "Assam"),
        (26.2, 91.5, "Brahmaputra Bridge 2", "Assam"),
        (26.7, 94.2, "Jorhat Bridge", "Assam"),
        (25.5, 91.9, "Shillong Bridge", "Meghalaya"),
        (27.3, 88.6, "Teesta Bridge", "Sikkim"),
        (24.8, 93.9, "Imphal River Bridge", "Manipur"),
        (23.7, 92.7, "Tlawng River Bridge", "Mizoram"),
        (25.9, 93.7, "Dhansiri Bridge", "Nagaland"),
        (28.0, 95.3, "Siang River Bridge", "Arunachal Pradesh"),
        (27.0, 93.6, "Subansiri Bridge", "Arunachal Pradesh"),
    ]
    
    for (lat, lon, name, state) in bridge_locations:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "infra_id": f"BRG_{infra_id:03d}",
                "type": "bridge",
                "name": name,
                "state": state,
                "critical": True,
                "single_point_of_failure": True,
                "load_capacity_tons": random.choice([20, 40, 70, 100]),
                "age_years": random.randint(5, 45),
                "condition": random.choice(["good", "fair", "poor"]),
                "is_synthetic": True,
                "data_source": "SYNTHETIC_DEMO",
            }
        })
        infra_id += 1
    
    return {
        "type": "FeatureCollection",
        "metadata": {
            "data_type": "SYNTHETIC_DEMO",
            "warning": "THIS IS SYNTHETIC DATA FOR DEMONSTRATION ONLY.",
            "total_features": len(features),
            "types": {"hospitals": len([f for f in features if f["properties"]["type"] == "hospital"]),
                      "schools": len([f for f in features if f["properties"]["type"] == "school"]),
                      "bridges": len([f for f in features if f["properties"]["type"] == "bridge"])},
            "generated_at": "2026-08-27T10:00:00Z",
        },
        "features": features
    }

def main():
    os.makedirs("data/processed/roads", exist_ok=True)
    os.makedirs("data/processed/villages", exist_ok=True)
    os.makedirs("data/processed/infrastructure", exist_ok=True)
    
    print("Generating synthetic roads...")
    roads = generate_roads()
    with open("data/processed/roads/ner_roads.geojson", "w") as f:
        json.dump(roads, f, indent=2)
    print(f"  Saved {roads['metadata']['total_roads']} roads")
    
    print("Generating synthetic villages...")
    villages = generate_villages()
    with open("data/processed/villages/ner_villages.geojson", "w") as f:
        json.dump(villages, f, indent=2)
    print(f"  Saved {villages['metadata']['total_villages']} villages")
    
    print("Generating synthetic infrastructure...")
    infra = generate_infrastructure()
    with open("data/processed/infrastructure/ner_infrastructure.geojson", "w") as f:
        json.dump(infra, f, indent=2)
    print(f"  Saved {infra['metadata']['total_features']} infrastructure items")
    
    print("Done! All synthetic geospatial data generated.")

if __name__ == "__main__":
    main()
