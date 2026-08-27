# Automated OpenTopography SRTM GL1 DEM Acquisition Plan

## Executive Summary
This document defines the automated acquisition strategy for retrieving NASA SRTM GL1 30 m Digital Elevation Model (DEM) rasters across the Northeast India (NER) study region using the official OpenTopography Global Datasets REST API.

---

## 1. Region Extents & Request Limits

- **Target Study Region Bounding Box**:
  - **West ($x_{\min}$)**: `88.0° E`
  - **South ($y_{\min}$)**: `21.0° N`
  - **East ($x_{\max}$)**: `98.0° E`
  - **North ($y_{\max}$)**: `30.0° N`
- **OpenTopography Single Request Safety Cap**: `450,000 km²` per API query.
- **Partitioning Rationale**: To ensure every API call stays well below the 450,000 km² query limit, the $10^\circ \text{ Lon} \times 9^\circ \text{ Lat}$ region is partitioned into 4 large composite grid tiles ($5^\circ \text{ Lon} \times 4-5^\circ \text{ Lat}$).

---

## 2. 4-Tile Grid Specification & Safety Audit

| Tile ID | Lon Range (°E) | Lat Range (°N) | Approx. Area (km²) | OpenTopography Limit Cap | Safety Margin | Overlaps Test Tile (92-93E, 24-25N)? | Planned Output Filename |
|---|---|---|---|---|---|---|---|
| **Tile_A** | `88.0° – 93.0° E` | `21.0° – 25.0° N` | **227,582.0 km²** | `450,000 km²` | **50.6% of limit (PASS)** | **YES** | `srtm_tile_A_88_21_93_25.tif` |
| **Tile_B** | `93.0° – 98.0° E` | `21.0° – 25.0° N` | **227,582.0 km²** | `450,000 km²` | **50.6% of limit (PASS)** | **NO** | `srtm_tile_B_93_21_98_25.tif` |
| **Tile_C** | `88.0° – 93.0° E` | `25.0° – 30.0° N` | **274,095.0 km²** | `450,000 km²` | **60.9% of limit (PASS)** | **NO** | `srtm_tile_C_88_25_93_30.tif` |
| **Tile_D** | `93.0° – 98.0° E` | `25.0° – 30.0° N` | **274,095.0 km²** | `450,000 km²` | **60.9% of limit (PASS)** | **NO** | `srtm_tile_D_93_25_98_30.tif` |

---

## 3. Existing Test Tile Overlap Analysis

- **Existing Raw Test File**: `data/raw/terrain/dem/output_SRTMGL1.tif`
- **Extents**: $92.0^\circ - 93.0^\circ\text{E}, 24.0^\circ - 25.0^\circ\text{N}$
- **Overlap Audit**:
  - **Tile_A**: Overlaps the existing test tile. The test tile represents a $1^\circ \times 1^\circ$ subset within Tile_A's $5^\circ \times 4^\circ$ spatial footprint.
  - **Tile_B, Tile_C, Tile_D**: Zero spatial overlap with the existing test tile.
- **Preservation Policy**: Raw files `data/raw/terrain/dem/output_SRTMGL1.tif` and `rasters_SRTMGL1.tar.gz` remain intact and will **never** be overwritten or modified.

---

## 4. API Key Security & Compliance

- **Environment Variable**: `OPENTOPOGRAPHY_API_KEY`
- **Storage**: Defined inside local `.env` file (`OPENTOPOGRAPHY_API_KEY=your_key`).
- **Security Mandates**:
  - Key is NEVER hardcoded in script source files.
  - Key is NEVER printed to terminal, logs, or reports.
  - Key is excluded from version control (`.env` listed in `.gitignore`).

---

## 5. Script & Pipeline Architecture

The automated download pipeline is implemented in [`scripts/download_ner_srtm.py`](file:///c:/Users/siddh/Music/ner%20landslide%20project/scripts/download_ner_srtm.py).

### Core Features
- Uses `requests` with automated exponential backoff retries (`HTTP 429, 500, 502, 503, 504`).
- Validates HTTP response status (`200 OK`) and payload size ($> 1000$ bytes).
- Creates `data/raw/terrain/dem/` automatically if missing.
- Prevents redundant downloads if valid raster files already exist (override with `--force`).
- Generates JSON manifest schema compliance at [`data/schemas/srtm_download_manifest.json`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/schemas/srtm_download_manifest.json).

---

## 6. CLI Usage Instructions

### Run Dry-Run (No network downloads)
```bash
python scripts/download_ner_srtm.py --dry-run
```

### Run Live Download Pipeline
```bash
python scripts/download_ner_srtm.py
```

### Force Overwrite Existing Files
```bash
python scripts/download_ner_srtm.py --force
```
