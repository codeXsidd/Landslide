"""
Complete NER Terrain/DEM Pipeline
Downloads missing SRTM GL1 tiles, creates mosaic, generates terrain derivatives,
validates outputs, and creates reports/previews.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import datetime
import numpy as np
import rasterio
import rasterio.windows
from rasterio.merge import merge
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DEM_DIR = PROJECT_ROOT / "data" / "raw" / "terrain" / "dem"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "terrain"
DOCS_DIR = PROJECT_ROOT / "docs" / "data"
SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"

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

API_BASE = "https://portal.opentopography.org/API/globaldem"


def get_api_key():
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    key = os.environ.get("OPENTOPOGRAPHY_API_KEY", "")
    if not key:
        raise RuntimeError("OPENTOPOGRAPHY_API_KEY not found in .env")
    return key


def get_required_tiles():
    required = []
    for lat in range(21, 30):
        ymin, ymax = float(lat), float(lat + 1)
        for lon in range(88, 98):
            xmin, xmax = float(lon), float(lon + 1)
            tile_id = f"NER_DEM_E{lon:03d}_N{lat:02d}"
            for state, (sbx_min, sby_min, sbx_max, sby_max) in STATE_BBOXES.items():
                if not (xmax <= sbx_min or xmin >= sbx_max or ymax <= sby_min or ymin >= sby_max):
                    required.append({
                        "tile_id": tile_id,
                        "xmin": xmin, "ymin": ymin,
                        "xmax": xmax, "ymax": ymax,
                    })
                    break
    return required


def tile_filepath(tile_id):
    if tile_id == "NER_DEM_E092_N24":
        return RAW_DEM_DIR / "output_SRTMGL1.tif"
    return RAW_DEM_DIR / f"{tile_id}.tif"


def validate_tile(filepath):
    try:
        with rasterio.open(filepath) as ds:
            if ds.count < 1:
                return False, "No bands"
            if ds.width < 100 or ds.height < 100:
                return False, "Too small"
            data = ds.read(1)
            valid = data[data != ds.nodata] if ds.nodata is not None else data
            if len(valid) == 0:
                return False, "All NoData"
            return True, "OK"
    except Exception as e:
        return False, str(e)


def download_tile(tile, api_key, max_retries=3):
    filepath = RAW_DEM_DIR / f"{tile['tile_id']}.tif"
    if filepath.exists():
        valid, msg = validate_tile(filepath)
        if valid:
            return "SKIPPED_EXISTS", str(filepath)

    params = (
        f"?demtype=SRTMGL1"
        f"&south={tile['ymin']}&north={tile['ymax']}"
        f"&west={tile['xmin']}&east={tile['xmax']}"
        f"&outputFormat=GTiff"
        f"&API_Key={api_key}"
    )
    url = API_BASE + params

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "NER-LDI-Pipeline/1.0")
            with urllib.request.urlopen(req, timeout=300) as response:
                data = response.read()
                if len(data) < 1000:
                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    return "FAILED_EMPTY", f"Response too small ({len(data)} bytes)"

                with open(filepath, "wb") as f:
                    f.write(data)

                valid, msg = validate_tile(filepath)
                if valid:
                    return "DOWNLOADED", str(filepath)
                else:
                    os.remove(filepath)
                    return "FAILED_INVALID", msg

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            if e.code == 429 or (e.code == 401 and "rate limit" in body.lower()):
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code in (500, 502, 503, 504):
                time.sleep(10 * (attempt + 1))
            else:
                return f"FAILED_HTTP_{e.code}", str(e)
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return "FAILED_NETWORK", str(e)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                return "FAILED_ERROR", str(e)

    return "FAILED_RETRIES", "Max retries exceeded"


def phase1_inventory():
    print("=" * 60)
    print("PHASE 1: INVENTORY EXISTING DEM")
    print("=" * 60)

    required = get_required_tiles()
    valid_tiles = []
    missing_tiles = []

    for tile in required:
        fp = tile_filepath(tile["tile_id"])
        if fp.exists():
            ok, msg = validate_tile(fp)
            if ok:
                valid_tiles.append(tile)
            else:
                missing_tiles.append(tile)
                print(f"  INVALID: {tile['tile_id']} - {msg}")
        else:
            missing_tiles.append(tile)

    print(f"  Required: {len(required)}")
    print(f"  Valid: {len(valid_tiles)}")
    print(f"  Missing: {len(missing_tiles)}")
    return required, valid_tiles, missing_tiles


def phase2_download(missing_tiles):
    print("\n" + "=" * 60)
    print("PHASE 2: DOWNLOAD MISSING TILES")
    print("=" * 60)

    if not missing_tiles:
        print("  No missing tiles - skipping download.")
        return [], []

    api_key = get_api_key()
    downloaded = []
    failed = []

    for i, tile in enumerate(missing_tiles):
        print(f"  [{i+1}/{len(missing_tiles)}] Downloading {tile['tile_id']}...")
        status, detail = download_tile(tile, api_key)
        print(f"    -> {status}")

        if status in ("DOWNLOADED", "SKIPPED_EXISTS"):
            downloaded.append(tile)
        else:
            failed.append({"tile_id": tile["tile_id"], "status": status, "detail": detail})

        if status == "DOWNLOADED":
            time.sleep(2)

    print(f"\n  Downloaded: {len(downloaded)}")
    print(f"  Failed: {len(failed)}")
    return downloaded, failed


def phase3_validate(required):
    print("\n" + "=" * 60)
    print("PHASE 3: COMPLETE COVERAGE VALIDATION")
    print("=" * 60)

    results = []
    for tile in required:
        fp = tile_filepath(tile["tile_id"])
        if fp.exists():
            ok, msg = validate_tile(fp)
            if ok:
                with rasterio.open(fp) as ds:
                    data = ds.read(1)
                    valid_data = data[data != ds.nodata] if ds.nodata is not None else data
                    results.append({
                        "tile_id": tile["tile_id"],
                        "status": "VALID",
                        "crs": str(ds.crs),
                        "resolution": ds.res,
                        "bounds": list(ds.bounds),
                        "nodata": ds.nodata,
                        "min_elev": float(valid_data.min()),
                        "max_elev": float(valid_data.max()),
                        "shape": ds.shape,
                    })
            else:
                results.append({"tile_id": tile["tile_id"], "status": "INVALID", "error": msg})
        else:
            results.append({"tile_id": tile["tile_id"], "status": "MISSING"})

    valid = [r for r in results if r["status"] == "VALID"]
    invalid = [r for r in results if r["status"] == "INVALID"]
    missing = [r for r in results if r["status"] == "MISSING"]

    print(f"  Valid: {len(valid)}/57")
    print(f"  Invalid: {len(invalid)}")
    print(f"  Missing: {len(missing)}")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / "ner_srtm_complete_validation.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# NER SRTM Complete Validation Report\n\n")
        f.write(f"**Generated**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Required cells: 57\n")
        f.write(f"- Valid cells: {len(valid)}\n")
        f.write(f"- Invalid cells: {len(invalid)}\n")
        f.write(f"- Missing cells: {len(missing)}\n")
        f.write(f"- Coverage: {len(valid)/57*100:.1f}%\n\n")

        if valid:
            f.write("## Valid Tiles\n\n")
            f.write("| Tile ID | CRS | Resolution | Bounds (W/S/E/N) | NoData | Elev Min | Elev Max |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in valid:
                b = r["bounds"]
                f.write(f"| {r['tile_id']} | {r['crs']} | {r['resolution'][0]:.7f} | "
                        f"{b[0]:.2f}/{b[1]:.2f}/{b[2]:.2f}/{b[3]:.2f} | "
                        f"{r['nodata']} | {r['min_elev']:.0f} | {r['max_elev']:.0f} |\n")

        if missing:
            f.write("\n## Missing Tiles\n\n")
            for r in missing:
                f.write(f"- `{r['tile_id']}`\n")

        if invalid:
            f.write("\n## Invalid Tiles\n\n")
            for r in invalid:
                f.write(f"- `{r['tile_id']}`: {r['error']}\n")

    print(f"  Report: {report_path}")
    return valid, missing, invalid


def phase4_mosaic(valid_results):
    print("\n" + "=" * 60)
    print("PHASE 4: CREATE DEM MOSAIC")
    print("=" * 60)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "ner_dem.tif"

    src_files = []
    for r in valid_results:
        fp = tile_filepath(r["tile_id"])
        src_files.append(fp)

    print(f"  Merging {len(src_files)} tiles...")

    datasets = []
    for fp in src_files:
        datasets.append(rasterio.open(fp))

    mosaic, mosaic_transform = merge(datasets, nodata=-32768)

    profile = datasets[0].profile.copy()
    profile.update(
        driver="GTiff",
        height=mosaic.shape[1],
        width=mosaic.shape[2],
        transform=mosaic_transform,
        count=1,
        dtype="int16",
        nodata=-32768,
        compress="deflate",
        tiled=True,
        blockxsize=512,
        blockysize=512,
    )

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(mosaic)

    for ds in datasets:
        ds.close()

    with rasterio.open(output_path) as ds:
        print(f"  Output: {output_path}")
        print(f"  CRS: {ds.crs}")
        print(f"  Shape: {ds.shape}")
        print(f"  Bounds: {ds.bounds}")
        data = ds.read(1)
        valid_data = data[data != -32768]
        print(f"  Elevation range: {valid_data.min()} to {valid_data.max()}")

    report_path = DOCS_DIR / "ner_dem_mosaic_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        with rasterio.open(output_path) as ds:
            data = ds.read(1)
            valid_data = data[data != -32768]
            f.write("# NER DEM Mosaic Report\n\n")
            f.write(f"**Generated**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n\n")
            f.write("## Mosaic Properties\n\n")
            f.write(f"- **Source tiles**: {len(src_files)}\n")
            f.write(f"- **CRS**: {ds.crs}\n")
            f.write(f"- **Resolution**: {ds.res[0]:.10f} degrees (~30m)\n")
            f.write(f"- **Dimensions**: {ds.width} x {ds.height}\n")
            f.write(f"- **Bounds**: W={ds.bounds.left:.4f}, S={ds.bounds.bottom:.4f}, E={ds.bounds.right:.4f}, N={ds.bounds.top:.4f}\n")
            f.write(f"- **NoData**: {ds.nodata}\n")
            f.write(f"- **Elevation range**: {valid_data.min()} to {valid_data.max()} m\n")
            f.write(f"- **Valid pixels**: {len(valid_data):,}\n")
            f.write(f"- **NoData pixels**: {(data == -32768).sum():,}\n")
            f.write(f"- **Output file**: `data/processed/terrain/ner_dem.tif`\n")
            f.write(f"- **Compression**: DEFLATE\n")
            f.write(f"- **Tiled**: Yes (512x512)\n")

    print(f"  Mosaic report: {report_path}")
    return output_path


def compute_tri_vectorized(dem):
    """Vectorized TRI computation using shifted arrays."""
    h, w = dem.shape
    padded = np.pad(dem, 1, mode='constant', constant_values=np.nan)
    sum_sq_diff = np.zeros_like(dem)
    count = np.zeros_like(dem)

    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            neighbor = padded[1+di:1+di+h, 1+dj:1+dj+w]
            valid = ~np.isnan(neighbor) & ~np.isnan(dem)
            diff_sq = np.where(valid, (neighbor - dem)**2, 0.0)
            sum_sq_diff += diff_sq
            count += valid.astype(np.float32)

    with np.errstate(divide='ignore', invalid='ignore'):
        tri = np.sqrt(sum_sq_diff / count)
    tri[count == 0] = np.nan
    tri[np.isnan(dem)] = np.nan
    return tri


def phase5_derivatives_chunked(mosaic_path):
    """Memory-efficient chunked derivative computation with vectorized TRI."""
    print("\n" + "=" * 60)
    print("PHASE 5: TERRAIN DERIVATIVES (chunked)")
    print("=" * 60)

    with rasterio.open(mosaic_path) as src:
        profile = src.profile.copy()
        nodata_val = src.nodata
        res_x = src.res[0]
        res_y = src.res[1]
        bounds = src.bounds
        height = src.height
        width = src.width
        center_lat = (bounds.bottom + bounds.top) / 2.0

    deg_to_m_x = res_x * 111320.0 * np.cos(np.radians(center_lat))
    deg_to_m_y = res_y * 110540.0

    out_profile = profile.copy()
    out_profile.update(dtype="float32", nodata=-9999.0, compress="deflate",
                       tiled=True, blockxsize=512, blockysize=512)

    elev_path = PROCESSED_DIR / "elevation.tif"
    slope_path = PROCESSED_DIR / "slope.tif"
    aspect_path = PROCESSED_DIR / "aspect.tif"
    tri_path = PROCESSED_DIR / "terrain_ruggedness.tif"

    elev_dst = rasterio.open(elev_path, "w", **out_profile)
    slope_dst = rasterio.open(slope_path, "w", **out_profile)
    aspect_dst = rasterio.open(aspect_path, "w", **out_profile)
    tri_dst = rasterio.open(tri_path, "w", **out_profile)

    chunk_size = 4096
    pad = 1

    src = rasterio.open(mosaic_path)

    total_chunks = ((height + chunk_size - 1) // chunk_size) * ((width + chunk_size - 1) // chunk_size)
    chunk_count = 0

    for row_start in range(0, height, chunk_size):
        for col_start in range(0, width, chunk_size):
            chunk_count += 1
            if chunk_count % 5 == 0 or chunk_count == 1:
                print(f"  Processing chunk {chunk_count}/{total_chunks}...")

            row_end = min(row_start + chunk_size, height)
            col_end = min(col_start + chunk_size, width)

            pad_row_start = max(0, row_start - pad)
            pad_col_start = max(0, col_start - pad)
            pad_row_end = min(height, row_end + pad)
            pad_col_end = min(width, col_end + pad)

            window = rasterio.windows.Window(
                pad_col_start, pad_row_start,
                pad_col_end - pad_col_start,
                pad_row_end - pad_row_start
            )
            dem_chunk = src.read(1, window=window).astype(np.float32)

            nodata_mask_chunk = dem_chunk == nodata_val
            dem_chunk[nodata_mask_chunk] = np.nan

            r_off = row_start - pad_row_start
            c_off = col_start - pad_col_start
            actual_h = row_end - row_start
            actual_w = col_end - col_start

            elev_out = dem_chunk[r_off:r_off+actual_h, c_off:c_off+actual_w].copy()
            elev_nodata = np.isnan(elev_out)
            elev_out[elev_nodata] = -9999.0

            out_window = rasterio.windows.Window(col_start, row_start, actual_w, actual_h)
            elev_dst.write(elev_out.reshape(1, actual_h, actual_w), window=out_window)

            dz_dy, dz_dx = np.gradient(dem_chunk, deg_to_m_y, deg_to_m_x)
            dz_dx_crop = dz_dx[r_off:r_off+actual_h, c_off:c_off+actual_w]
            dz_dy_crop = dz_dy[r_off:r_off+actual_h, c_off:c_off+actual_w]

            slope_rad = np.arctan(np.sqrt(dz_dx_crop**2 + dz_dy_crop**2))
            slope_deg = np.degrees(slope_rad)
            slope_deg[elev_nodata] = -9999.0
            slope_dst.write(slope_deg.reshape(1, actual_h, actual_w), window=out_window)

            aspect_rad = np.arctan2(-dz_dx_crop, dz_dy_crop)
            aspect_deg = np.degrees(aspect_rad)
            aspect_deg = np.where(aspect_deg < 0, aspect_deg + 360, aspect_deg)
            aspect_deg[elev_nodata] = -9999.0
            aspect_dst.write(aspect_deg.reshape(1, actual_h, actual_w), window=out_window)

            # Vectorized TRI
            tri_chunk = compute_tri_vectorized(dem_chunk)
            tri_out = tri_chunk[r_off:r_off+actual_h, c_off:c_off+actual_w].copy()
            tri_out[elev_nodata] = -9999.0
            tri_out[np.isnan(tri_out)] = -9999.0
            tri_dst.write(tri_out.reshape(1, actual_h, actual_w), window=out_window)

    src.close()
    elev_dst.close()
    slope_dst.close()
    aspect_dst.close()
    tri_dst.close()

    print(f"  -> {elev_path}")
    print(f"  -> {slope_path}")
    print(f"  -> {aspect_path}")
    print(f"  -> {tri_path}")

    return elev_path, slope_path, aspect_path, tri_path


def phase6_validate_outputs():
    print("\n" + "=" * 60)
    print("PHASE 6: VALIDATE ALL TERRAIN OUTPUTS")
    print("=" * 60)

    files = {
        "ner_dem.tif": PROCESSED_DIR / "ner_dem.tif",
        "elevation.tif": PROCESSED_DIR / "elevation.tif",
        "slope.tif": PROCESSED_DIR / "slope.tif",
        "aspect.tif": PROCESSED_DIR / "aspect.tif",
        "terrain_ruggedness.tif": PROCESSED_DIR / "terrain_ruggedness.tif",
    }

    results = {}
    for name, path in files.items():
        print(f"  Validating {name}...")
        if not path.exists():
            results[name] = {"status": "MISSING"}
            print(f"    MISSING!")
            continue

        try:
            with rasterio.open(path) as ds:
                data = ds.read(1)
                nodata = ds.nodata
                if nodata is not None:
                    valid_data = data[data != nodata]
                else:
                    valid_data = data.flatten()

                finite_valid = valid_data[np.isfinite(valid_data)]
                results[name] = {
                    "status": "VALID",
                    "crs": str(ds.crs),
                    "resolution": ds.res,
                    "shape": ds.shape,
                    "bounds": list(ds.bounds),
                    "bands": ds.count,
                    "nodata": nodata,
                    "dtype": str(ds.dtypes[0]),
                    "min": float(finite_valid.min()) if len(finite_valid) > 0 else None,
                    "max": float(finite_valid.max()) if len(finite_valid) > 0 else None,
                    "valid_pixels": int(len(valid_data)),
                    "nodata_pixels": int((data == nodata).sum()) if nodata is not None else 0,
                    "finite_pixels": int(len(finite_valid)),
                }
                print(f"    OK: {ds.shape}, range [{results[name]['min']:.1f}, {results[name]['max']:.1f}]")
        except Exception as e:
            results[name] = {"status": "ERROR", "error": str(e)}
            print(f"    ERROR: {e}")

    report_path = DOCS_DIR / "terrain_derivatives_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Terrain Derivatives Validation Report\n\n")
        f.write(f"**Generated**: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n\n")
        f.write("## Output Files\n\n")
        f.write("| File | Status | CRS | Resolution | Dimensions | Min | Max | Valid Pixels |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for name, r in results.items():
            if r["status"] == "VALID":
                f.write(f"| `{name}` | VALID | {r['crs']} | {r['resolution'][0]:.7f} | "
                        f"{r['shape'][1]}x{r['shape'][0]} | {r['min']:.1f} | {r['max']:.1f} | "
                        f"{r['valid_pixels']:,} |\n")
            else:
                f.write(f"| `{name}` | {r['status']} | - | - | - | - | - | - |\n")

        f.write("\n## Detailed Properties\n\n")
        for name, r in results.items():
            if r["status"] != "VALID":
                continue
            f.write(f"### {name}\n\n")
            f.write(f"- **Path**: `data/processed/terrain/{name}`\n")
            f.write(f"- **CRS**: {r['crs']}\n")
            f.write(f"- **Resolution**: {r['resolution'][0]:.10f} deg\n")
            f.write(f"- **Dimensions**: {r['shape'][1]} x {r['shape'][0]}\n")
            f.write(f"- **Bounds**: W={r['bounds'][0]:.4f}, S={r['bounds'][1]:.4f}, E={r['bounds'][2]:.4f}, N={r['bounds'][3]:.4f}\n")
            f.write(f"- **Bands**: {r['bands']}\n")
            f.write(f"- **NoData**: {r['nodata']}\n")
            f.write(f"- **Data type**: {r['dtype']}\n")
            f.write(f"- **Value range**: [{r['min']:.2f}, {r['max']:.2f}]\n")
            f.write(f"- **Valid pixels**: {r['valid_pixels']:,}\n")
            f.write(f"- **NoData pixels**: {r['nodata_pixels']:,}\n\n")

    print(f"  Report: {report_path}")
    return results


def phase6_previews():
    print("\n  Generating preview images...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    previews = {
        "ner_dem_preview.png": ("ner_dem.tif", "NER DEM Elevation (m)", "terrain"),
        "slope_preview.png": ("slope.tif", "Slope (degrees)", "YlOrRd"),
        "aspect_preview.png": ("aspect.tif", "Aspect (degrees)", "hsv"),
        "terrain_ruggedness_preview.png": ("terrain_ruggedness.tif", "Terrain Ruggedness Index", "magma"),
    }

    for preview_name, (src_name, title, cmap) in previews.items():
        src_path = PROCESSED_DIR / src_name
        out_path = DOCS_DIR / preview_name
        if not src_path.exists():
            continue

        with rasterio.open(src_path) as ds:
            data = ds.read(1, out_shape=(min(2000, ds.height), min(2000, ds.width)))
            nodata = ds.nodata

        plot_data = data.astype(np.float32)
        if nodata is not None:
            plot_data[plot_data == nodata] = np.nan

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        im = ax.imshow(plot_data, cmap=cmap, aspect="equal")
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        plt.tight_layout()
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"    -> {out_path}")


def phase7_manifest(valid_results, missing_results):
    print("\n" + "=" * 60)
    print("PHASE 7: TERRAIN DATASET MANIFEST")
    print("=" * 60)

    SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = SCHEMAS_DIR / "terrain_dataset_manifest.json"

    tile_filenames = []
    for r in valid_results:
        fp = tile_filepath(r["tile_id"])
        tile_filenames.append(fp.name)

    mosaic_bounds = None
    mosaic_crs = None
    if (PROCESSED_DIR / "ner_dem.tif").exists():
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            mosaic_bounds = list(ds.bounds)
            mosaic_crs = str(ds.crs)

    manifest = {
        "source": "SRTM GL1",
        "resolution_m": 30,
        "resolution_deg": 0.0002777777777778146,
        "provider": "OpenTopography / NASA SRTM",
        "dataset": "SRTMGL1",
        "required_tile_count": 57,
        "valid_tile_count": len(valid_results),
        "missing_tile_count": len(missing_results),
        "input_tile_filenames": sorted(tile_filenames),
        "missing_tile_ids": [r["tile_id"] for r in missing_results],
        "final_dem_path": "data/processed/terrain/ner_dem.tif",
        "derivative_paths": {
            "elevation": "data/processed/terrain/elevation.tif",
            "slope": "data/processed/terrain/slope.tif",
            "aspect": "data/processed/terrain/aspect.tif",
            "terrain_ruggedness": "data/processed/terrain/terrain_ruggedness.tif",
        },
        "crs": mosaic_crs,
        "bounds": mosaic_bounds,
        "processing_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validation_status": "COMPLETE" if len(missing_results) == 0 else "PARTIAL",
        "provenance": {
            "data_source": "NASA Shuttle Radar Topography Mission (SRTM) Global 1 arc-second",
            "access_method": "OpenTopography Global Datasets API",
            "horizontal_datum": "WGS84",
            "vertical_datum": "EGM96 geoid",
            "acquisition_year": "2000",
            "posting": "1 arc-second (~30m)",
        },
        "limitations": [
            "SRTM data may contain voids in steep terrain",
            "Elevation values represent surface elevation (DSM), not bare earth (DTM)",
            "Horizontal accuracy: ~20m, Vertical accuracy: ~16m (90% confidence)",
            f"{len(missing_results)} tiles could not be downloaded due to API authentication issues" if missing_results else None,
        ],
    }
    manifest["limitations"] = [x for x in manifest["limitations"] if x is not None]

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"  Manifest: {manifest_path}")
    return manifest_path


def phase8_tests():
    print("\n" + "=" * 60)
    print("PHASE 8: AUTOMATED TESTS")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0
    failures = []

    def assert_test(name, condition, detail=""):
        nonlocal tests_passed, tests_failed
        if condition:
            tests_passed += 1
            print(f"  PASS: {name}")
        else:
            tests_failed += 1
            failures.append(f"{name}: {detail}")
            print(f"  FAIL: {name} - {detail}")

    # Test 1: Required cell inventory
    required = get_required_tiles()
    assert_test("Required cells count = 57", len(required) == 57, f"Got {len(required)}")

    # Test 2: Valid tiles on disk
    valid_count = 0
    for tile in required:
        fp = tile_filepath(tile["tile_id"])
        if fp.exists():
            ok, _ = validate_tile(fp)
            if ok:
                valid_count += 1
    assert_test("Valid tiles >= 24", valid_count >= 24, f"Got {valid_count}")

    # Test 3: DEM mosaic exists and is readable
    mosaic_path = PROCESSED_DIR / "ner_dem.tif"
    mosaic_exists = mosaic_path.exists()
    assert_test("DEM mosaic exists", mosaic_exists)

    if mosaic_exists:
        with rasterio.open(mosaic_path) as ds:
            # Test 4: CRS
            assert_test("Mosaic CRS is EPSG:4326", str(ds.crs) == "EPSG:4326", str(ds.crs))
            # Test 5: Resolution ~30m
            assert_test("Mosaic resolution ~30m",
                        abs(ds.res[0] - 0.000277778) < 0.0001,
                        f"Got {ds.res[0]}")
            # Test 6: NoData
            assert_test("Mosaic NoData = -32768", ds.nodata == -32768, str(ds.nodata))

    # Test 7-10: Derivatives exist
    for name in ["elevation.tif", "slope.tif", "aspect.tif", "terrain_ruggedness.tif"]:
        path = PROCESSED_DIR / name
        assert_test(f"{name} exists", path.exists())

    # Test 11: Slope values in valid range
    slope_path = PROCESSED_DIR / "slope.tif"
    if slope_path.exists():
        with rasterio.open(slope_path) as ds:
            data = ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert_test("Slope values >= 0", valid.min() >= 0, f"Min={valid.min()}")
                assert_test("Slope values <= 90", valid.max() <= 90, f"Max={valid.max()}")

    # Test 12: Aspect values in valid range
    aspect_path = PROCESSED_DIR / "aspect.tif"
    if aspect_path.exists():
        with rasterio.open(aspect_path) as ds:
            data = ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert_test("Aspect values >= 0", valid.min() >= 0, f"Min={valid.min()}")
                assert_test("Aspect values <= 360", valid.max() <= 360, f"Max={valid.max()}")

    # Test 13: TRI values >= 0
    tri_path = PROCESSED_DIR / "terrain_ruggedness.tif"
    if tri_path.exists():
        with rasterio.open(tri_path) as ds:
            data = ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert_test("TRI values >= 0", valid.min() >= 0, f"Min={valid.min()}")

    # Test 14: NoData propagation - check that nodata in DEM = nodata in derivatives
    if mosaic_exists and slope_path.exists():
        with rasterio.open(mosaic_path) as dem_ds:
            dem_sample = dem_ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
        with rasterio.open(slope_path) as slope_ds:
            slope_sample = slope_ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
        dem_nodata = dem_sample == -32768
        slope_nodata = slope_sample == -9999.0
        nodata_match = np.all(dem_nodata == slope_nodata)
        assert_test("NoData propagation (DEM->slope)", nodata_match,
                    f"Mismatch at {(~nodata_match).sum()} pixels" if not nodata_match else "")

    # Test 15: Manifest exists
    manifest_path = SCHEMAS_DIR / "terrain_dataset_manifest.json"
    assert_test("Terrain manifest exists", manifest_path.exists())

    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed, failures


def main():
    print("NER TERRAIN/DEM PIPELINE - COMPLETE EXECUTION")
    print("=" * 60)
    print(f"Started: {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print()

    # Phase 1
    required, valid_tiles, missing_tiles = phase1_inventory()

    # Phase 2
    downloaded, failed_downloads = phase2_download(missing_tiles)

    # Phase 3
    valid_results, still_missing, invalid = phase3_validate(required)

    # Check if we can proceed
    if len(valid_results) < 24:
        print("\nFATAL: Fewer than 24 valid tiles. Cannot proceed.")
        sys.exit(1)

    # Phase 4
    mosaic_path = phase4_mosaic(valid_results)

    # Phase 5
    paths = phase5_derivatives_chunked(mosaic_path)

    # Phase 6
    results = phase6_validate_outputs()
    phase6_previews()

    # Phase 7
    phase7_manifest(valid_results, still_missing)

    # Phase 8
    passed, failed, failures = phase8_tests()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Required DEM cells: {len(required)}/57")
    print(f"Valid DEM cells: {len(valid_results)}/57")
    print(f"Missing DEM cells: {len(still_missing)}")
    print(f"DEM mosaic: {'PASS' if (PROCESSED_DIR / 'ner_dem.tif').exists() else 'FAIL'}")
    print(f"Elevation: {'PASS' if results.get('elevation.tif', {}).get('status') == 'VALID' else 'FAIL'}")
    print(f"Slope: {'PASS' if results.get('slope.tif', {}).get('status') == 'VALID' else 'FAIL'}")
    print(f"Aspect: {'PASS' if results.get('aspect.tif', {}).get('status') == 'VALID' else 'FAIL'}")
    print(f"Ruggedness: {'PASS' if results.get('terrain_ruggedness.tif', {}).get('status') == 'VALID' else 'FAIL'}")
    print(f"Terrain tests: {passed}/{passed+failed} passed")
    if still_missing:
        print(f"Still missing tiles: {[r['tile_id'] for r in still_missing]}")
    if failures:
        print(f"Test failures: {failures}")


if __name__ == "__main__":
    main()
