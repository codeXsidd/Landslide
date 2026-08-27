"""
Automated NASA SRTM GL1 30m DEM 90-Tile Grid Acquisition Pipeline
Using official OpenTopography Global Datasets API.

Target Region: West=88.0, South=21.0, East=98.0, North=30.0 (90 1x1 degree tiles)
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timezone
from PIL import Image
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

load_dotenv()

RAW_DEM_DIR = "data/raw/terrain/dem"
MANIFEST_PATH = os.path.join(RAW_DEM_DIR, "download_manifest.json")
DOC_REPORT_PATH = "docs/data/ner_srtm_download_report.md"
OPENTOPOGRAPHY_API_URL = "https://portal.opentopography.org/API/globaldem"
SINGLE_REQUEST_LIMIT_KM2 = 100000.0

EXISTING_TEST_FILE = "output_SRTMGL1.tif"
EXISTING_TEST_TILE_ID = "NER_DEM_E092_N24"

# State bboxes for metadata coverage mapping
STATE_BBOXES = {
    'Arunachal Pradesh': (91.5, 26.6, 97.5, 29.5),
    'Assam': (89.7, 24.1, 96.0, 28.0),
    'Meghalaya': (89.8, 25.0, 92.8, 26.2),
    'Nagaland': (93.3, 25.2, 95.3, 27.0),
    'Manipur': (93.0, 23.8, 94.8, 25.7),
    'Mizoram': (92.2, 21.9, 93.4, 24.5),
    'Tripura': (91.1, 22.9, 92.7, 24.5),
    'Sikkim': (88.0, 27.0, 88.9, 28.1),
    'West Bengal (North Bengal)': (87.8, 26.0, 89.9, 27.2),
}

def calculate_tile_area_km2(ymin: float, ymax: float, xmin: float, xmax: float) -> float:
    R = 6371.0
    dlon = np.radians(xmax - xmin)
    lat1 = np.radians(ymin)
    lat2 = np.radians(ymax)
    return float(R**2 * dlon * (np.sin(lat2) - np.sin(lat1)))

def generate_90_tile_grid() -> list[dict]:
    tiles = []
    for lat in range(21, 30):
        ymin, ymax = float(lat), float(lat + 1)
        for lon in range(88, 98):
            xmin, xmax = float(lon), float(lon + 1)
            tile_id = f"NER_DEM_E{lon:03d}_N{lat:02d}"
            filename = f"{tile_id}.tif"
            
            # Check states
            covered = []
            for state, (sbx_min, sby_min, sbx_max, sby_max) in STATE_BBOXES.items():
                if not (xmax <= sbx_min or xmin >= sbx_max or ymax <= sby_min or ymin >= sby_max):
                    covered.append(state)
            if not covered:
                if ymin < 24 and xmin < 92:
                    covered.append("Bangladesh (Border Region)")
                elif xmin >= 95 and ymin < 26:
                    covered.append("Myanmar (Border Region)")
                elif ymax >= 28 and xmin >= 92:
                    covered.append("China / Tibet (Border Region)")
                else:
                    covered.append("Neighboring / International Border")
                    
            tiles.append({
                "tile_id": tile_id,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "filename": filename,
                "states": ", ".join(covered),
                "area_km2": round(calculate_tile_area_km2(ymin, ymax, xmin, xmax), 1)
            })
    return tiles

def validate_raster(file_path: str) -> dict:
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
        return {"valid": False, "error": "File missing or smaller than 1KB"}

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
                    "width": int(src.width),
                    "height": int(src.height),
                    "bounds": [float(src.bounds.left), float(src.bounds.bottom), float(src.bounds.right), float(src.bounds.top)],
                    "nodata": float(nodata) if nodata is not None else -32768.0,
                    "min_elevation": float(np.min(valid_data)) if valid_data.size > 0 else None,
                    "max_elevation": float(np.max(valid_data)) if valid_data.size > 0 else None,
                }
        except Exception as e:
            pass

    try:
        im = Image.open(file_path)
        arr = np.array(im)
        width, height = im.size
        nodata = None
        tiepoint = None
        scale = None
        if hasattr(im, "tag_v2"):
            nodata = im.tag_v2.get(42113, None)
            tiepoint = im.tag_v2.get(33922, None)
            scale = im.tag_v2.get(33550, None)
            
        left = tiepoint[3] if tiepoint else 0.0
        top = tiepoint[4] if tiepoint else 0.0
        res_x = scale[0] if scale else 0.0002777777777778146
        res_y = scale[1] if scale else 0.0002777777777778146
        right = left + width * res_x
        bottom = top - height * res_y
        
        nd_val = float(nodata) if nodata is not None else -32768.0
        valid_mask = (arr != nd_val) & (~np.isnan(arr))
        valid_data = arr[valid_mask]
        
        return {
            "valid": True,
            "crs": "EPSG:4326",
            "resolution": [res_x, res_y],
            "width": width,
            "height": height,
            "bounds": [left, bottom, right, top],
            "nodata": nd_val,
            "min_elevation": float(np.min(valid_data)) if valid_data.size > 0 else None,
            "max_elevation": float(np.max(valid_data)) if valid_data.size > 0 else None,
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

def build_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def run_pipeline(dry_run: bool = False, force: bool = False):
    os.makedirs(RAW_DEM_DIR, exist_ok=True)
    api_key = os.getenv("OPENTOPOGRAPHY_API_KEY", "").strip()
    
    grid = generate_90_tile_grid()
    session = build_session() if not dry_run else None
    
    print("==========================================================")
    print("    Northeast India 90-Tile SRTM GL1 Acquisition Pipeline ")
    print("==========================================================")
    print(f"Total Planned Grid Tiles : {len(grid)} (88.0°E-98.0°E, 21.0°N-30.0°N)")
    print(f"API Key Configured       : {'YES' if api_key else 'NO (Missing/Empty)'}")
    print(f"Execution Mode           : {'DRY RUN' if dry_run else 'LIVE PIPELINE'}")
    print(f"Force Overwrite          : {force}")
    print("==========================================================\n")

    manifest_records = []
    existing_test_filepath = os.path.join(RAW_DEM_DIR, EXISTING_TEST_FILE)

    for i, tile in enumerate(grid, 1):
        tile_id = tile["tile_id"]
        target_file = os.path.join(RAW_DEM_DIR, tile["filename"])
        is_test_tile = (tile_id == EXISTING_TEST_TILE_ID)
        
        record = {
            "tile_id": tile_id,
            "xmin": tile["xmin"],
            "ymin": tile["ymin"],
            "xmax": tile["xmax"],
            "ymax": tile["ymax"],
            "approximate_area_km2": tile["area_km2"],
            "filename": tile["filename"],
            "status": "PENDING",
            "file_size": 0,
            "downloaded_at": None,
            "validation_status": "UNTESTED",
            "crs": "EPSG:4326",
            "resolution": [0.0002777777777778146, 0.0002777777777778146],
            "bounds": [tile["xmin"], tile["ymin"], tile["xmax"], tile["ymax"]],
            "min_elevation": None,
            "max_elevation": None,
            "nodata": -32768.0
        }

        # Check existing raw test tile (output_SRTMGL1.tif)
        if is_test_tile and os.path.exists(existing_test_filepath) and not force:
            insp = validate_raster(existing_test_filepath)
            record["status"] = "SKIPPED_EXISTING_TEST_TILE"
            record["filename"] = EXISTING_TEST_FILE
            record["file_size"] = os.path.getsize(existing_test_filepath)
            record["downloaded_at"] = datetime.now(timezone.utc).isoformat()
            if insp.get("valid"):
                record["validation_status"] = "VALID"
                record["crs"] = insp.get("crs")
                record["resolution"] = insp.get("resolution")
                record["bounds"] = insp.get("bounds")
                record["nodata"] = insp.get("nodata")
                record["min_elevation"] = insp.get("min_elevation")
                record["max_elevation"] = insp.get("max_elevation")
            manifest_records.append(record)
            continue

        # Check existing target tile
        if os.path.exists(target_file) and not force:
            insp = validate_raster(target_file)
            if insp.get("valid"):
                record["status"] = "SKIPPED_EXISTS"
                record["file_size"] = os.path.getsize(target_file)
                record["downloaded_at"] = datetime.now(timezone.utc).isoformat()
                record["validation_status"] = "VALID"
                record["crs"] = insp.get("crs")
                record["resolution"] = insp.get("resolution")
                record["bounds"] = insp.get("bounds")
                record["nodata"] = insp.get("nodata")
                record["min_elevation"] = insp.get("min_elevation")
                record["max_elevation"] = insp.get("max_elevation")
                manifest_records.append(record)
                continue

        if dry_run:
            record["status"] = "SKIPPED_DRY_RUN"
            record["validation_status"] = "SKIPPED"
            manifest_records.append(record)
            continue

        if not api_key:
            record["status"] = "FAILED_NO_API_KEY"
            record["validation_status"] = "INVALID"
            manifest_records.append(record)
            continue

        # Live Download Attempt
        params = {
            "demtype": "SRTMGL1",
            "south": tile["ymin"],
            "north": tile["ymax"],
            "west": tile["xmin"],
            "east": tile["xmax"],
            "outputFormat": "GTiff",
            "API_Key": api_key
        }

        print(f"[{i:02d}/90] Downloading {tile_id} ({tile['xmin']}°E-{tile['xmax']}°E, {tile['ymin']}°N-{tile['ymax']}°N)...")
        try:
            start_t = time.time()
            resp = session.get(OPENTOPOGRAPHY_API_URL, params=params, timeout=300)
            elapsed = time.time() - start_t

            if resp.status_code != 200:
                print(f"  [{tile_id}] ERROR: HTTP {resp.status_code} ({elapsed:.1f}s)")
                record["status"] = f"FAILED_HTTP_{resp.status_code}"
                record["validation_status"] = "FAILED_HTTP"
                manifest_records.append(record)
                continue

            if len(resp.content) < 1000:
                print(f"  [{tile_id}] ERROR: Zero-byte / small payload ({len(resp.content)} bytes)")
                record["status"] = "FAILED_CORRUPTED_PAYLOAD"
                record["validation_status"] = "INVALID_CORRUPT"
                manifest_records.append(record)
                continue

            with open(target_file, "wb") as f:
                f.write(resp.content)

            # Rasterio Validation
            insp = validate_raster(target_file)
            if not insp.get("valid"):
                print(f"  [{tile_id}] ERROR: Invalid raster structure ({insp.get('error')})")
                if os.path.exists(target_file):
                    os.remove(target_file) # Remove corrupted download
                record["status"] = "FAILED_INVALID_RASTER"
                record["validation_status"] = "INVALID_CORRUPT"
                manifest_records.append(record)
                continue

            # Valid Download
            actual_size = os.path.getsize(target_file)
            print(f"  [{tile_id}] SUCCESS: Verified ({actual_size:,} bytes in {elapsed:.1f}s)")
            record["status"] = "COMPLETED"
            record["file_size"] = actual_size
            record["downloaded_at"] = datetime.now(timezone.utc).isoformat()
            record["validation_status"] = "VALID"
            record["crs"] = insp.get("crs")
            record["resolution"] = insp.get("resolution")
            record["bounds"] = insp.get("bounds")
            record["nodata"] = insp.get("nodata")
            record["min_elevation"] = insp.get("min_elevation")
            record["max_elevation"] = insp.get("max_elevation")
            manifest_records.append(record)

        except Exception as e:
            print(f"  [{tile_id}] EXCEPTION: {e}")
            record["status"] = f"FAILED_EXCEPTION_{type(e).__name__}"
            record["validation_status"] = "FAILED_EXCEPTION"
            manifest_records.append(record)

    # Save manifest JSON
    manifest_data = {
        "manifest_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "opentopography_dataset": "SRTMGL1",
        "output_format": "GTiff",
        "total_planned_tiles": len(grid),
        "existing_test_tile": EXISTING_TEST_TILE_ID,
        "api_key_configured": bool(api_key),
        "is_dry_run": dry_run,
        "tiles": manifest_records
    }
    
    with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, indent=2)
    print(f"\nSaved download manifest: {MANIFEST_PATH}")

    # Summary Stats
    completed_or_existing = [r for r in manifest_records if r["validation_status"] == "VALID"]
    newly_downloaded = [r for r in manifest_records if r["status"] == "COMPLETED"]
    existing_tiles = [r for r in manifest_records if r["status"] in ("SKIPPED_EXISTING_TEST_TILE", "SKIPPED_EXISTS")]
    failed_tiles = [r for r in manifest_records if "FAILED" in r["status"]]
    missing_tiles = [r for r in manifest_records if r["validation_status"] != "VALID"]
    total_size_bytes = sum(r.get("file_size", 0) for r in manifest_records)
    cov_pct = (len(completed_or_existing) / len(grid)) * 100.0

    # Save Markdown Report
    os.makedirs(os.path.dirname(DOC_REPORT_PATH), exist_ok=True)
    with open(DOC_REPORT_PATH, "w", encoding="utf-8") as rf:
        rf.write("# Northeast India 90-Tile SRTM GL1 Acquisition Report\n\n")
        rf.write("## Overview\n")
        rf.write("This report documents the status of the 90-tile SRTM GL1 30 m DEM acquisition pipeline for Northeast India ($88.0^\\circ\\text{E} - 98.0^\\circ\\text{E}, 21.0^\\circ\\text{N} - 30.0^\\circ\\text{N}$).\n\n")
        
        rf.write("## Executive Summary Statistics\n\n")
        rf.write(f"- **Total Planned Grid Tiles**: `{len(grid)}`\n")
        rf.write(f"- **Existing Valid Tiles**: `{len(existing_tiles)}` (including test tile `{EXISTING_TEST_TILE_ID}`)\n")
        rf.write(f"- **Newly Downloaded Tiles**: `{len(newly_downloaded)}`\n")
        rf.write(f"- **Failed Tiles**: `{len(failed_tiles)}`\n")
        rf.write(f"- **Missing Tiles**: `{len(missing_tiles)}`\n")
        rf.write(f"- **Total DEM File Size**: `{total_size_bytes / (1024*1024):,.2f} MB` ({total_size_bytes:,} bytes)\n")
        rf.write(f"- **Study Area Coverage**: `{cov_pct:.2f}%` ({len(completed_or_existing)} / {len(grid)} tiles)\n\n")

        rf.write("## Detailed 90-Tile Manifest Table\n\n")
        rf.write("| Tile ID | Lon Range | Lat Range | Area (km²) | Download Status | Validation Status | File Size | Filename |\n")
        rf.write("|---|---|---|---|---|---|---|---|\n")
        for r in manifest_records:
            rf.write(f"| `{r['tile_id']}` | {r['xmin']:.1f}°-{r['xmax']:.1f}°E | {r['ymin']:.1f}°-{r['ymax']:.1f}°N | {r['approximate_area_km2']:,} | **{r['status']}** | **{r['validation_status']}** | {r['file_size']:,} B | `{r['filename']}` |\n")

    print(f"Saved download report: {DOC_REPORT_PATH}")

    # Terminal Output
    print("\n================ ACQUISITION PIPELINE SUMMARY ================")
    print(f"Total Planned Grid Tiles : {len(grid)}")
    print(f"Existing Valid Tiles     : {len(existing_tiles)}")
    print(f"Newly Downloaded Tiles   : {len(newly_downloaded)}")
    print(f"Failed Tiles             : {len(failed_tiles)}")
    print(f"Missing Tiles            : {len(missing_tiles)}")
    print(f"Total Size on Disk       : {total_size_bytes / (1024*1024):,.2f} MB")
    print(f"Coverage Percentage      : {cov_pct:.2f}%")
    print("==============================================================")

def main():
    parser = argparse.ArgumentParser(description="Acquire 90 1x1 degree SRTM GL1 DEM tiles for Northeast India")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode without downloading")
    parser.add_argument("--force", action="store_true", help="Force re-download of existing tiles")
    args = parser.parse_args()
    
    run_pipeline(dry_run=args.dry_run, force=args.force)

if __name__ == "__main__":
    main()
