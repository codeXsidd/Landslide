"""
Automated NASA SRTM GL1 30m DEM Acquisition Pipeline
Using official OpenTopography Global Datasets API.

Target Bounding Box: West=88.0, South=21.0, East=98.0, North=30.0
OpenTopography Request Safety Cap: 450,000 km² per single request.
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

# Try loading rasterio for inspection; fall back to PIL if needed
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

# Load environment variables from .env
load_dotenv()

RAW_DEM_DIR = "data/raw/terrain/dem"
MANIFEST_PATH = "data/processed/terrain/srtm_download_manifest.json"
OPENTOPOGRAPHY_API_URL = "https://portal.opentopography.org/API/globaldem"
SINGLE_REQUEST_LIMIT_KM2 = 450000.0

# Existing raw test tile bounds (92-93E, 24-25N)
EXISTING_TEST_TILE_BBOX = {"xmin": 92.0, "ymin": 24.0, "xmax": 93.0, "ymax": 25.0}

# 4-Tile Grid Definition (5-deg lon x 4/5-deg lat)
PLANNED_TILES = [
    {
        "tile_id": "Tile_A",
        "xmin": 88.0,
        "ymin": 21.0,
        "xmax": 93.0,
        "ymax": 25.0,
        "filename": "srtm_tile_A_88_21_93_25.tif",
        "description": "Southwest NER (Assam, Meghalaya, Tripura, Mizoram, Bangladesh border)",
    },
    {
        "tile_id": "Tile_B",
        "xmin": 93.0,
        "ymin": 21.0,
        "xmax": 98.0,
        "ymax": 25.0,
        "filename": "srtm_tile_B_93_21_98_25.tif",
        "description": "Southeast NER (Manipur, Mizoram, Nagaland, Myanmar border)",
    },
    {
        "tile_id": "Tile_C",
        "xmin": 88.0,
        "ymin": 25.0,
        "xmax": 93.0,
        "ymax": 30.0,
        "filename": "srtm_tile_C_88_25_93_30.tif",
        "description": "Northwest NER (Sikkim, West Bengal, Assam, Western Arunachal Pradesh)",
    },
    {
        "tile_id": "Tile_D",
        "xmin": 93.0,
        "ymin": 25.0,
        "xmax": 98.0,
        "ymax": 30.0,
        "filename": "srtm_tile_D_93_25_98_30.tif",
        "description": "Northeast NER (Arunachal Pradesh, Nagaland, Eastern Assam)",
    },
]


def calculate_tile_area_km2(ymin: float, ymax: float, xmin: float, xmax: float) -> float:
    """Calculate geodesic surface area of spherical bounding box in km²."""
    R = 6371.0
    dlon = np.radians(xmax - xmin)
    lat1 = np.radians(ymin)
    lat2 = np.radians(ymax)
    return float(R**2 * dlon * (np.sin(lat2) - np.sin(lat1)))


def check_bbox_overlap(b1: dict, b2: dict) -> bool:
    """Check if bounding box b1 overlaps bounding box b2."""
    if b1["xmax"] <= b2["xmin"] or b1["xmin"] >= b2["xmax"]:
        return False
    if b1["ymax"] <= b2["ymin"] or b1["ymin"] >= b2["ymax"]:
        return False
    return True


def inspect_raster_file(file_path: str) -> dict:
    """Inspect and validate downloaded GeoTIFF raster using rasterio or PIL."""
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
                    "resolution": (float(src.res[0]), float(src.res[1])),
                    "width": int(src.width),
                    "height": int(src.height),
                    "bounds": (float(src.bounds.left), float(src.bounds.bottom), float(src.bounds.right), float(src.bounds.top)),
                    "nodata": float(nodata) if nodata is not None else None,
                    "min_elevation": float(np.min(valid_data)) if valid_data.size > 0 else None,
                    "max_elevation": float(np.max(valid_data)) if valid_data.size > 0 else None,
                }
        except Exception as e:
            pass

    # Fallback to PIL inspection
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
            "resolution": (res_x, res_y),
            "width": width,
            "height": height,
            "bounds": (left, bottom, right, top),
            "nodata": nd_val,
            "min_elevation": float(np.min(valid_data)) if valid_data.size > 0 else None,
            "max_elevation": float(np.max(valid_data)) if valid_data.size > 0 else None,
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def build_session_with_retries() -> requests.Session:
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


def download_tile(
    tile: dict,
    api_key: str,
    out_dir: str,
    force: bool = False,
    session: requests.Session = None,
) -> dict:
    if session is None:
        session = requests.Session()

    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, tile["filename"])
    meta_path = os.path.join(out_dir, tile["filename"].replace(".tif", "_metadata.json"))
    area_km2 = calculate_tile_area_km2(tile["ymin"], tile["ymax"], tile["xmin"], tile["xmax"])
    overlaps = check_bbox_overlap(tile, EXISTING_TEST_TILE_BBOX)

    record = {
        "tile_id": tile["tile_id"],
        "xmin": tile["xmin"],
        "ymin": tile["ymin"],
        "xmax": tile["xmax"],
        "ymax": tile["ymax"],
        "approximate_area_km2": round(area_km2, 1),
        "dataset": "SRTMGL1",
        "output_format": "GTiff",
        "filename": tile["filename"],
        "filepath": file_path,
        "overlaps_existing_test_tile": overlaps,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "PENDING",
        "file_size": 0,
        "raster_metadata": {},
    }

    if os.path.exists(file_path) and not force:
        size = os.path.getsize(file_path)
        if size > 1000:
            insp = inspect_raster_file(file_path)
            if insp.get("valid"):
                print(f"  [{tile['tile_id']}] Valid file exists ({size:,} bytes). Skipping (use --force to overwrite).")
                record["status"] = "SKIPPED_EXISTS"
                record["file_size"] = size
                record["raster_metadata"] = insp
                with open(meta_path, "w", encoding="utf-8") as mf:
                    json.dump(record, mf, indent=2)
                return record

    params = {
        "demtype": "SRTMGL1",
        "south": tile["ymin"],
        "north": tile["ymax"],
        "west": tile["xmin"],
        "east": tile["xmax"],
        "outputFormat": "GTiff",
        "API_Key": api_key,
    }

    print(f"  [{tile['tile_id']}] Querying OpenTopography API ({area_km2:,.1f} km²)...")
    start_t = time.time()
    try:
        response = session.get(OPENTOPOGRAPHY_API_URL, params=params, timeout=300)
        elapsed = time.time() - start_t

        if response.status_code != 200:
            print(f"  [{tile['tile_id']}] ERROR: HTTP Status {response.status_code} ({elapsed:.1f}s)")
            record["status"] = f"FAILED_HTTP_{response.status_code}"
            return record

        content_len = len(response.content)
        if content_len < 1000:
            err_msg = response.content.decode("utf-8", errors="ignore")[:200]
            print(f"  [{tile['tile_id']}] ERROR: Invalid/small response ({content_len} bytes): {err_msg}")
            record["status"] = "FAILED_INVALID_RESPONSE"
            return record

        with open(file_path, "wb") as f:
            f.write(response.content)

        actual_size = os.path.getsize(file_path)
        insp = inspect_raster_file(file_path)
        record["raster_metadata"] = insp

        if not insp.get("valid"):
            print(f"  [{tile['tile_id']}] ERROR: Raster inspection failed: {insp.get('error')}")
            record["status"] = "FAILED_INVALID_RASTER"
            return record

        print(f"  [{tile['tile_id']}] SUCCESS: Downloaded & verified ({actual_size:,} bytes in {elapsed:.1f}s)")
        print(f"    - CRS       : {insp.get('crs')}")
        print(f"    - Dimensions: {insp.get('width')} x {insp.get('height')}")
        print(f"    - Elevation : [{insp.get('min_elevation')}m, {insp.get('max_elevation')}m]")
        record["status"] = "COMPLETED"
        record["file_size"] = actual_size

        # Save per-tile metadata JSON
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(record, mf, indent=2)
        print(f"  [{tile['tile_id']}] Saved metadata: {meta_path}")

    except Exception as e:
        print(f"  [{tile['tile_id']}] EXCEPTION: {e}")
        record["status"] = f"FAILED_EXCEPTION_{type(e).__name__}"

    return record


def run_pipeline(dry_run: bool = False, force: bool = False, out_dir: str = RAW_DEM_DIR, manifest_path: str = MANIFEST_PATH):
    print("==========================================================")
    print("      OpenTopography SRTM GL1 DEM Acquisition Pipeline    ")
    print("==========================================================")
    print(f"Target Bounding Box : West=88.0, South=21.0, East=98.0, North=30.0")
    print(f"OpenTopography Cap  : {SINGLE_REQUEST_LIMIT_KM2:,.0f} km² max per request")
    print(f"Output Directory    : {out_dir}")
    print(f"Mode                : {'DRY RUN (No network calls)' if dry_run else 'LIVE DOWNLOAD'}")
    print(f"Force Overwrite     : {force}")
    print("==========================================================\n")

    api_key = os.getenv("OPENTOPOGRAPHY_API_KEY", "").strip()

    if not dry_run and not api_key:
        raise ValueError(
            "CRITICAL: OPENTOPOGRAPHY_API_KEY is missing or empty in .env!\n"
            "Please add your key to .env file as: OPENTOPOGRAPHY_API_KEY=your_key_here\n"
            "Get your key at: https://portal.opentopography.org/"
        )

    if dry_run and not api_key:
        print("[DRY-RUN NOTICE] OPENTOPOGRAPHY_API_KEY is not set in .env (not required for dry-run mode).\n")

    manifest_records = []
    session = build_session_with_retries() if not dry_run else None

    for tile in PLANNED_TILES:
        area_km2 = calculate_tile_area_km2(tile["ymin"], tile["ymax"], tile["xmin"], tile["xmax"])
        below_limit = area_km2 < SINGLE_REQUEST_LIMIT_KM2
        overlaps = check_bbox_overlap(tile, EXISTING_TEST_TILE_BBOX)
        target_file = os.path.join(out_dir, tile["filename"])
        file_exists = os.path.exists(target_file)

        print(f"--- Tile: {tile['tile_id']} ---")
        print(f"  Description       : {tile['description']}")
        print(f"  Coordinates       : Lon [{tile['xmin']}°E, {tile['xmax']}°E], Lat [{tile['ymin']}°N, {tile['ymax']}°N]")
        print(f"  Approximate Area  : {area_km2:,.1f} km² ({(area_km2 / SINGLE_REQUEST_LIMIT_KM2)*100:.1f}% of limit)")
        print(f"  Safety Limit Check: {'PASS (Below 450,000 km² limit)' if below_limit else 'FAIL (Exceeds limit)'}")
        print(f"  Overlaps Test Tile: {'YES (Contains 92-93°E, 24-25°N region)' if overlaps else 'NO'}")
        print(f"  Output Path       : {target_file}")
        print(f"  Existing File     : {'EXISTS' if file_exists else 'NEW (Not downloaded yet)'}")

        if dry_run:
            status = "SKIPPED_DRY_RUN"
            if file_exists:
                status = "SKIPPED_EXISTS"
            rec = {
                "tile_id": tile["tile_id"],
                "xmin": tile["xmin"],
                "ymin": tile["ymin"],
                "xmax": tile["xmax"],
                "ymax": tile["ymax"],
                "approximate_area_km2": round(area_km2, 1),
                "dataset": "SRTMGL1",
                "output_format": "GTiff",
                "filename": tile["filename"],
                "filepath": target_file,
                "overlaps_existing_test_tile": overlaps,
                "download_timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "file_size": os.path.getsize(target_file) if file_exists else 0,
                "raster_metadata": inspect_raster_file(target_file) if file_exists else {},
            }
            manifest_records.append(rec)
            print(f"  Dry-Run Status    : {status}\n")
        else:
            rec = download_tile(tile, api_key, out_dir, force=force, session=session)
            manifest_records.append(rec)
            print()

    # Write Manifest JSON
    successful = [r for r in manifest_records if r["status"] in ("COMPLETED", "SKIPPED_EXISTS")]
    failed = [r for r in manifest_records if r not in successful]
    total_size = sum(r.get("file_size", 0) for r in manifest_records)

    manifest = {
        "manifest_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "opentopography_dataset": "SRTMGL1",
        "output_format": "GTiff",
        "total_tiles_planned": len(PLANNED_TILES),
        "total_tiles_successful": len(successful),
        "total_tiles_failed": len(failed),
        "total_bytes_downloaded": total_size,
        "is_dry_run": dry_run,
        "tiles": manifest_records,
    }

    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)
    print(f"Saved download manifest to: {manifest_path}")

    # Terminal Summary Report
    print("\n================ FINAL ACQUISITION REPORT ================")
    print(f"Successful Downloads: {len(successful)} / {len(PLANNED_TILES)}")
    print(f"Failed Downloads    : {len(failed)}")
    print(f"Total Size          : {total_size / (1024*1024):,.2f} MB ({total_size:,} bytes)")
    print(f"Tile Coverage       : 88.0°E to 98.0°E, 21.0°N to 30.0°N")
    print(f"Test Tile Overlaps  : Tile_A overlaps existing test tile (92-93°E, 24-25°N)")
    print(f"Internal Gaps       : None (Tiles A, B, C, D seamlessly cover the entire 10°x9° box)")
    print("\nPer-Tile Details:")
    for r in manifest_records:
        meta = r.get("raster_metadata", {})
        print(f"  [{r['tile_id']}] File: {r['filename']} | Status: {r['status']} | Size: {r['file_size']:,} bytes")
        if meta.get("valid"):
            print(f"    - Dimensions: {meta.get('width')}x{meta.get('height')} | CRS: {meta.get('crs')} | Elevation: [{meta.get('min_elevation')}m, {meta.get('max_elevation')}m]")
    print("==========================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Download SRTM GL1 30m DEM tiles from OpenTopography API")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry-run checks without sending API requests")
    parser.add_argument("--force", action="store_true", help="Overwrite existing valid tile files")
    parser.add_argument("--out-dir", default=RAW_DEM_DIR, help="Directory to save raw DEM rasters")
    parser.add_argument("--manifest", default=MANIFEST_PATH, help="Path to save download manifest JSON")
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run, force=args.force, out_dir=args.out_dir, manifest_path=args.manifest)


if __name__ == "__main__":
    main()
