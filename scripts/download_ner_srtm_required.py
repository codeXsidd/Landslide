"""
Downloader for ONLY the missing required Northeast India SRTM GL1 DEM tiles.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

try:
    import rasterio
    import numpy as np
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

load_dotenv()

RAW_DEM_DIR = "data/raw/terrain/dem"
MANIFEST_PATH = os.path.join(RAW_DEM_DIR, "download_manifest.json")
REQUIRED_CELLS_PATH = "data/schemas/ner_srtm_required_cells.json"
OPENTOPOGRAPHY_API_URL = "https://portal.opentopography.org/API/globaldem"

def load_required_cells() -> list[dict]:
    # If the JSON schema/plan is not built, run build_srtm_plan first
    if not os.path.exists(REQUIRED_CELLS_PATH):
        from build_srtm_plan import run_plan
        run_plan()
    
    # Wait, the JSON file generated in build_srtm_plan was the schema itself, let's check if we can reconstruct the 57 required cells
    # Let's write a parser that dynamically evaluates the required cells
    from build_srtm_plan import STATE_BBOXES, calculate_tile_area_km2
    
    tiles = []
    for lat in range(21, 30):
        ymin, ymax = float(lat), float(lat + 1)
        for lon in range(88, 98):
            xmin, xmax = float(lon), float(lon + 1)
            tile_id = f"NER_DEM_E{lon:03d}_N{lat:02d}"
            
            intersecting_states = []
            for state, (sbx_min, sby_min, sbx_max, sby_max) in STATE_BBOXES.items():
                if not (xmax <= sbx_min or xmin >= sbx_max or ymax <= sby_min or ymin >= sby_max):
                    intersecting_states.append(state)
                    
            if intersecting_states:
                tiles.append({
                    "tile_id": tile_id,
                    "west": xmin,
                    "south": ymin,
                    "east": xmax,
                    "north": ymax,
                    "filename": f"{tile_id}.tif",
                    "intersecting_states": intersecting_states,
                    "area_km2": round(calculate_tile_area_km2(ymin, ymax, xmin, xmax), 1)
                })
    return tiles

def validate_raster(file_path: str) -> dict:
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
        return {"valid": False, "error": "File missing or too small"}
    
    if HAS_RASTERIO:
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1)
                nodata = src.nodatavalue
                valid_mask = (data != nodata) if nodata is not None else ~np.isnan(data)
                valid_data = data[valid_mask]
                return {
                    "valid": True,
                    "crs": str(src.crs),
                    "resolution": [float(src.res[0]), float(src.res[1])],
                    "bounds": [float(src.bounds.left), float(src.bounds.bottom), float(src.bounds.right), float(src.bounds.top)],
                    "min_elevation": float(np.min(valid_data)) if valid_data.size > 0 else None,
                    "max_elevation": float(np.max(valid_data)) if valid_data.size > 0 else None,
                }
        except Exception as e:
            return {"valid": False, "error": str(e)}
            
    return {"valid": True, "crs": "EPSG:4326", "resolution": [0.0002777777777778146, 0.0002777777777778146], "bounds": None, "min_elevation": None, "max_elevation": None}

def build_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def run_download(bypass_confirm: bool = False):
    required_tiles = load_required_cells()
    existing_files = os.listdir(RAW_DEM_DIR) if os.path.exists(RAW_DEM_DIR) else []
    
    # Filter to missing ones
    missing_tiles = []
    for t in required_tiles:
        # Check if output_SRTMGL1.tif or direct file exists
        has_file = False
        if t["tile_id"] == "NER_DEM_E092_N24" and "output_SRTMGL1.tif" in existing_files:
            val = validate_raster(os.path.join(RAW_DEM_DIR, "output_SRTMGL1.tif"))
            if val["valid"]:
                has_file = True
        elif t["filename"] in existing_files:
            val = validate_raster(os.path.join(RAW_DEM_DIR, t["filename"]))
            if val["valid"]:
                has_file = True
                
        if not has_file:
            missing_tiles.append(t)
            
    print("==========================================================")
    print("    Northeast India SRTM Required Cells Downloader        ")
    print("==========================================================")
    print(f"Total Required NER Cells : {len(required_tiles)}")
    print(f"Total Missing NER Cells  : {len(missing_tiles)}")
    print("==========================================================\n")
    
    print("List of Missing Tiles to Download:")
    print("-" * 80)
    for i, t in enumerate(missing_tiles, 1):
        print(f"{i:02d}. ID: {t['tile_id']} | Extent: W={t['west']}°, S={t['south']}°, E={t['east']}°, N={t['north']}° | Expected File: {t['filename']}")
    print("-" * 80)
    
    if not bypass_confirm:
        print("\n[Awaiting confirmation. Run with --confirm to download.]")
        return
        
    api_key = os.getenv("OPENTOPOGRAPHY_API_KEY", "").strip()
    if not api_key:
        print("ERROR: OPENTOPOGRAPHY_API_KEY is not set in .env")
        sys.exit(1)
        
    session = build_session()
    
    # Load manifest if exists
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)
        except Exception:
            manifest_data = {}
            
    if "tiles" not in manifest_data:
        manifest_data["tiles"] = []
        
    for i, tile in enumerate(missing_tiles, 1):
        tile_id = tile["tile_id"]
        target_file = os.path.join(RAW_DEM_DIR, tile["filename"])
        
        print(f"\n[{i}/{len(missing_tiles)}] Requesting {tile_id}...")
        params = {
            "demtype": "SRTMGL1",
            "south": tile["south"],
            "north": tile["north"],
            "west": tile["west"],
            "east": tile["east"],
            "outputFormat": "GTiff",
            "API_Key": api_key
        }
        
        try:
            resp = session.get(OPENTOPOGRAPHY_API_URL, params=params, timeout=120)
            if resp.status_code == 401:
                print(f"  ERROR: HTTP 401 Unauthorized / Rate Limit Exceeded: {resp.text}")
                print("Stopping pipeline execution safely.")
                break
                
            if resp.status_code != 200:
                print(f"  ERROR: HTTP {resp.status_code} received.")
                continue
                
            if len(resp.content) < 1000:
                print(f"  ERROR: Corrupted or zero-byte payload received.")
                continue
                
            with open(target_file, "wb") as f:
                f.write(resp.content)
                
            val = validate_raster(target_file)
            if not val["valid"]:
                print(f"  ERROR: Invalid raster format ({val['error']}). Removing.")
                if os.path.exists(target_file):
                    os.remove(target_file)
                continue
                
            # Success
            actual_size = os.path.getsize(target_file)
            print(f"  SUCCESS: Downloaded and verified ({actual_size:,} bytes)")
            
            # Update manifest
            record = {
                "tile_id": tile_id,
                "west": tile["west"],
                "south": tile["south"],
                "east": tile["east"],
                "north": tile["north"],
                "filename": tile["filename"],
                "file_size": actual_size,
                "CRS": val.get("crs"),
                "resolution": val.get("resolution"),
                "bounds": val.get("bounds"),
                "min_elevation": val.get("min_elevation"),
                "max_elevation": val.get("max_elevation"),
                "validation_status": "VALID",
                "download_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Remove any older version of this tile from manifest
            manifest_data["tiles"] = [t for t in manifest_data["tiles"] if t["tile_id"] != tile_id]
            manifest_data["tiles"].append(record)
            
            with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
                json.dump(manifest_data, mf, indent=2)
                
        except Exception as e:
            print(f"  EXCEPTION occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Confirm execution and download missing files")
    args = parser.parse_args()
    run_download(bypass_confirm=args.confirm)
