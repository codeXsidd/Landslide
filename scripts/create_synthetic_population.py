"""
NER-LDI MVP — Synthetic Population Exposure Layer Generator
Creates clearly labelled SYNTHETIC population exposure data for Northeast India.

SYNTHETIC DATA — FOR DEMONSTRATION PURPOSES ONLY
"""
import os
import json
import random
import math
import csv

random.seed(42)

# NER grid: 0.1° resolution covering NER bounding box
LON_MIN, LON_MAX = 88.0, 97.5
LAT_MIN, LAT_MAX = 21.9, 29.5
RESOLUTION = 0.1  # degrees

# State-based population density (persons per km2) — approximate real values
STATE_DENSITY = {
    "Assam": 398,
    "Tripura": 350,
    "Meghalaya": 132,
    "Manipur": 122,
    "Nagaland": 119,
    "Mizoram": 52,
    "Arunachal Pradesh": 17,
    "Sikkim": 86,
    "Outside NER": 0,
}

# Simple state bounding boxes
STATE_BBOXES = {
    "Assam": (89.7, 24.1, 96.0, 28.0),
    "Arunachal Pradesh": (91.5, 26.6, 97.5, 29.5),
    "Meghalaya": (89.8, 25.0, 92.8, 26.2),
    "Nagaland": (93.3, 25.2, 95.3, 27.0),
    "Manipur": (93.0, 23.8, 94.8, 25.7),
    "Mizoram": (92.2, 21.9, 93.4, 24.5),
    "Tripura": (91.1, 22.9, 92.7, 24.5),
    "Sikkim": (88.0, 27.0, 88.9, 28.1),
}

def get_state(lat, lon):
    for state, (xmin, ymin, xmax, ymax) in STATE_BBOXES.items():
        if xmin <= lon <= xmax and ymin <= lat <= ymax:
            return state
    return None

def main():
    os.makedirs("data/synthetic/population", exist_ok=True)
    
    records = []
    lon = LON_MIN
    while lon < LON_MAX:
        lat = LAT_MIN
        while lat < LAT_MAX:
            state = get_state(lat, lon)
            if state:
                density = STATE_DENSITY.get(state, 0)
                # Cell area approx (km²)
                cell_area = (RESOLUTION * 111) * (RESOLUTION * 111 * math.cos(math.radians(lat)))
                # Base population
                base_pop = density * cell_area
                # Add spatial variation (log-normal distribution for realism)
                pop = max(0, int(random.lognormvariate(math.log(max(1, base_pop)), 0.8)))
                
                # Landslide exposure: proportion of population at risk (based on elevation proxy)
                # Higher lat/more mountainous → higher exposure
                elevation_proxy = max(0, (lat - 22) / 8 * 2000 + random.gauss(0, 300))
                if elevation_proxy > 1500:
                    exposure_factor = 0.6
                elif elevation_proxy > 800:
                    exposure_factor = 0.3
                else:
                    exposure_factor = 0.1
                    
                pop_at_risk = int(pop * exposure_factor)
                
                records.append({
                    "latitude": round(lat + RESOLUTION / 2, 4),
                    "longitude": round(lon + RESOLUTION / 2, 4),
                    "state": state,
                    "grid_cell_id": f"POP_{len(records):05d}",
                    "population_total": pop,
                    "population_at_risk": pop_at_risk,
                    "area_km2": round(cell_area, 2),
                    "density_per_km2": round(pop / max(0.01, cell_area), 1),
                    "elevation_proxy_m": round(elevation_proxy, 1),
                    "landslide_exposure_class": "HIGH" if exposure_factor > 0.4 else "MEDIUM" if exposure_factor > 0.15 else "LOW",
                    "is_synthetic": True,
                    "data_source": "SYNTHETIC_DEMO",
                })
            lat = round(lat + RESOLUTION, 4)
        lon = round(lon + RESOLUTION, 4)
    
    # Write CSV
    csv_path = "data/synthetic/population/ner_population_exposure.csv"
    if records:
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    
    # Write metadata
    total_pop = sum(r["population_total"] for r in records)
    total_at_risk = sum(r["population_at_risk"] for r in records)
    
    metadata = {
        "data_type": "SYNTHETIC_DEMO",
        "warning": "THIS IS SYNTHETIC POPULATION DATA FOR DEMONSTRATION ONLY. Not real WorldPop data.",
        "resolution_degrees": RESOLUTION,
        "bbox": {"lon_min": LON_MIN, "lat_min": LAT_MIN, "lon_max": LON_MAX, "lat_max": LAT_MAX},
        "total_grid_cells": len(records),
        "total_population_synthetic": total_pop,
        "total_population_at_risk_synthetic": total_at_risk,
        "states_covered": list(STATE_BBOXES.keys()),
        "generated_at": "2026-08-27T10:00:00Z",
        "csv_output": csv_path,
    }
    with open("data/synthetic/population/population_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Synthetic population layer created:")
    print(f"  Grid cells: {len(records)}")
    print(f"  Total synthetic population: {total_pop:,}")
    print(f"  Population at risk (synthetic): {total_at_risk:,}")
    print(f"  Output: {csv_path}")

if __name__ == "__main__":
    main()
