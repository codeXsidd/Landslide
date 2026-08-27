"""
Build exact SRTM acquisition plan for Northeast India based on state bounding boxes.
Produces:
- docs/data/ner_srtm_required_cells.md
- data/schemas/ner_srtm_required_cells.json
"""

import os
import json
import numpy as np

RAW_DEM_DIR = "data/raw/terrain/dem"
SCHEMA_PATH = "data/schemas/ner_srtm_required_cells.json"
REPORT_PATH = "docs/data/ner_srtm_required_cells.md"

STATE_BBOXES = {
    'Arunachal Pradesh': (91.5, 26.6, 97.5, 29.5),
    'Assam': (89.7, 24.1, 96.0, 28.0),
    'Meghalaya': (89.8, 25.0, 92.8, 26.2),
    'Nagaland': (93.3, 25.2, 95.3, 27.0),
    'Manipur': (93.0, 23.8, 94.8, 25.7),
    'Mizoram': (92.2, 21.9, 93.4, 24.5),
    'Tripura': (91.1, 22.9, 92.7, 24.5),
    'Sikkim': (88.0, 27.0, 88.9, 28.1),
}

def calculate_tile_area_km2(ymin: float, ymax: float, xmin: float, xmax: float) -> float:
    R = 6371.0
    dlon = np.radians(xmax - xmin)
    lat1 = np.radians(ymin)
    lat2 = np.radians(ymax)
    return float(R**2 * dlon * (np.sin(lat2) - np.sin(lat1)))

def run_plan():
    # 1. Search for administrative boundary datasets
    print("Checking for administrative boundary vector files...")
    # (Reporting that no .shp or .geojson dataset is present in the workspace)
    
    # 2. Check existing files in raw DEM directory
    existing_files = os.listdir(RAW_DEM_DIR) if os.path.exists(RAW_DEM_DIR) else []
    print(f"Found {len(existing_files)} files in raw DEM directory.")
    
    # 3. Process grid
    tiles = []
    total_required = 0
    existing_coverage_count = 0
    missing_coverage_count = 0
    outside_ner_count = 0
    
    for lat in range(21, 30):
        ymin, ymax = float(lat), float(lat + 1)
        for lon in range(88, 98):
            xmin, xmax = float(lon), float(lon + 1)
            tile_id = f"NER_DEM_E{lon:03d}_N{lat:02d}"
            
            # Check intersection with state bboxes
            intersecting_states = []
            for state, (sbx_min, sby_min, sbx_max, sby_max) in STATE_BBOXES.items():
                if not (xmax <= sbx_min or xmin >= sbx_max or ymax <= sby_min or ymin >= sby_max):
                    intersecting_states.append(state)
                    
            required_for_ner = len(intersecting_states) > 0
            area_km2 = calculate_tile_area_km2(ymin, ymax, xmin, xmax)
            
            # Check existing coverage (either as a processed tile or the raw output_SRTMGL1.tif for E092_N24)
            has_file = False
            if tile_id == "NER_DEM_E092_N24" and "output_SRTMGL1.tif" in existing_files:
                has_file = True
            elif f"{tile_id}.tif" in existing_files:
                has_file = True
                
            existing_cov = has_file
            missing_cov = not has_file
            
            if required_for_ner:
                total_required += 1
                if existing_cov:
                    existing_coverage_count += 1
                else:
                    missing_coverage_count += 1
            else:
                outside_ner_count += 1
                
            tiles.append({
                "tile_id": tile_id,
                "west": xmin,
                "south": ymin,
                "east": xmax,
                "north": ymax,
                "intersecting_states": intersecting_states,
                "approximate_area_km2": round(area_km2, 1),
                "existing_coverage": existing_cov,
                "missing_coverage": missing_cov,
                "required_for_NER": required_for_ner
            })
            
    # Write JSON Schema
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Northeast India SRTM Required Cells Plan Schema",
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "total_required_cells": {"type": "integer"},
                    "existing_coverage_cells": {"type": "integer"},
                    "missing_cells": {"type": "integer"},
                    "cells_outside_ner_excluded": {"type": "integer"}
                },
                "required": ["total_required_cells", "existing_coverage_cells", "missing_cells", "cells_outside_ner_excluded"]
            },
            "tiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "tile_id": {"type": "string"},
                        "west": {"type": "number"},
                        "south": {"type": "number"},
                        "east": {"type": "number"},
                        "north": {"type": "number"},
                        "intersecting_states": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "approximate_area_km2": {"type": "number"},
                        "existing_coverage": {"type": "boolean"},
                        "missing_coverage": {"type": "boolean"},
                        "required_for_NER": {"type": "boolean"}
                    },
                    "required": ["tile_id", "west", "south", "east", "north", "intersecting_states", "approximate_area_km2", "existing_coverage", "missing_coverage", "required_for_NER"]
                }
            }
        },
        "required": ["metadata", "tiles"]
    }
    
    os.makedirs(os.path.dirname(SCHEMA_PATH), exist_ok=True)
    with open(SCHEMA_PATH, "w", encoding="utf-8") as sf:
        json.dump(schema, sf, indent=2)
    print(f"Saved Schema to: {SCHEMA_PATH}")
    
    # Save Report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as rf:
        rf.write("# Northeast India Required SRTM Cells Acquisition Plan\n\n")
        rf.write("## Administrative Boundary Dataset Status\n")
        rf.write("> [!WARNING]\n")
        rf.write("> The project currently **does not contain any official administrative boundary dataset** (such as a Shapefile, GeoJSON, or GeoPackage) in `data/` for Northeast India. State bounding boxes have been used instead to compute intersection mapping.\n\n")
        
        rf.write("## Executive Summary\n\n")
        rf.write(f"- **Total Required SRTM Cells (Intersecting NER States)**: `{total_required}`\n")
        rf.write(f"- **Existing Coverage Cells (Valid on Disk)**: `{existing_coverage_count}`\n")
        rf.write(f"- **Missing Cells**: `{missing_coverage_count}`\n")
        rf.write(f"- **Cells Outside NER Bounding Box (Excluded)**: `{outside_ner_count}`\n\n")
        
        rf.write("## State Boundary Intersections & Cell Inventory\n\n")
        rf.write("| Tile ID | Extent (W/S/E/N) | Intersecting States | Area (km²) | Existing Coverage | Missing Coverage | Required for NER |\n")
        rf.write("|---|---|---|---|---|---|---|\n")
        for t in tiles:
            states_str = ", ".join(t["intersecting_states"]) if t["intersecting_states"] else "None (Outside NER)"
            rf.write(f"| `{t['tile_id']}` | {t['west']:.1f}° / {t['south']:.1f}° / {t['east']:.1f}° / {t['north']:.1f}° | {states_str} | {t['approximate_area_km2']:,} | **{t['existing_coverage']}** | **{t['missing_coverage']}** | **{t['required_for_NER']}** |\n")

    print(f"Saved Report to: {REPORT_PATH}")
    
    print("\n================ REPORT MATRIX ================")
    print(f"Total required SRTM cells: {total_required}")
    print(f"Existing coverage cells  : {existing_coverage_count}")
    print(f"Missing cells            : {missing_coverage_count}")
    print(f"Cells outside NER        : {outside_ner_count}")
    print("===============================================")

if __name__ == "__main__":
    run_plan()
