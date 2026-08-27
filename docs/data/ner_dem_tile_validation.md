# SRTM GL1 30m DEM Tile Inventory & Validation Report

## Executive Summary
This report presents the rigorous multi-parameter validation of raw SRTM GL1 30 m Digital Elevation Model (DEM) tiles located in `data/raw/terrain/dem/`, evaluated against the target acquisition grid for Northeast India ($88.0^\circ\text{E} - 98.0^\circ\text{E}, 21.0^\circ\text{N} - 30.0^\circ\text{N}$). 

> [!IMPORTANT]
> - Raw DEM files in `data/raw/terrain/dem/` remain **100% unmodified and intact**.
> - Mosaicing, clipping, slope calculations, and ML model training remain **unexecuted** as mandated.

---

## 1. Multi-Parameter Audit Checklist (Criteria 1–10)

| Validation Parameter | Status / Result | Detailed Findings |
|---|---|---|
| **1. Number of DEM Files** | **1 Present / 89 Missing** | 1 raster tile (`output_SRTMGL1.tif`) is present out of 90 planned $1^\circ \times 1^\circ$ tiles. |
| **2. CRS Consistency** | **EPSG:4326 (WGS 84)** | Geographic Coordinate System, WGS 84 Datum. Consistent with project requirements. |
| **3. Resolution Consistency** | **1 arc-second (~30m)** | Pixel Scale: `0.0002777777777778° x 0.0002777777777778°` ($3,600 \times 3,600$ pixels per tile). |
| **4. Bounds of Every Tile** | **Validated** | `output_SRTMGL1.tif` (`NER_DEM_E092_N24`):<br>- **West ($x_{\min}$)**: `91.999861° E`<br>- **South ($y_{\min}$)**: `24.000139° N`<br>- **East ($x_{\max}$)**: `92.999861° E`<br>- **North ($y_{\max}$)**: `25.000139° N` |
| **5. Overlapping Tiles** | **None** | Single tile present; zero spatial overlap conflicts detected among raw files. |
| **6. Gaps Between Tiles** | **89 Missing Tiles** | Significant spatial gaps across 89 grid cells ($88.0^\circ-92.0^\circ\text{E}$ and $93.0^\circ-98.0^\circ\text{E}$ across $21.0^\circ-30.0^\circ\text{N}$). |
| **7. Corrupt Files** | **None (0 Corrupt)** | `output_SRTMGL1.tif` is 100% valid; all 12,960,000 pixels read successfully without I/O or header errors. |
| **8. NoData Values** | **-32768** | GDAL NoData attribute: `-32768`. Count of NoData pixels in `output_SRTMGL1.tif`: `0` (100% valid elevation data). |
| **9. Minimum Elevation** | **-38 meters** | Minimum elevation observed in valid data array. |
| **10. Maximum Elevation** | **1,254 meters** | Maximum elevation observed in valid data array. |

---

## 2. Spatial Coverage Map

A visual coverage map displaying the full 90-tile study grid, highlighting present vs. missing tiles, has been generated:

👉 [`docs/data/ner_dem_tile_coverage.png`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_dem_tile_coverage.png)

![SRTM DEM Coverage Map](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_dem_tile_coverage.png)

---

## 3. Present vs. Missing Tile Inventory Summary

### Present & Validated Tile (1 Tile)
- **`NER_DEM_E092_N24`** (`output_SRTMGL1.tif`): Covers $92.0^\circ - 93.0^\circ\text{E}, 24.0^\circ - 25.0^\circ\text{N}$ (Southern Assam, Mizoram, Tripura).

### Missing Tiles (89 Tiles)
- **$21^\circ\text{N}$ Band**: `NER_DEM_E088_N21` to `NER_DEM_E097_N21` (10 tiles)
- **$22^\circ\text{N}$ Band**: `NER_DEM_E088_N22` to `NER_DEM_E097_N22` (10 tiles)
- **$23^\circ\text{N}$ Band**: `NER_DEM_E088_N23` to `NER_DEM_E097_N23` (10 tiles)
- **$24^\circ\text{N}$ Band**: `NER_DEM_E088_N24` to `NER_DEM_E091_N24` & `NER_DEM_E093_N24` to `NER_DEM_E097_N24` (9 tiles)
- **$25^\circ\text{N}$ Band**: `NER_DEM_E088_N25` to `NER_DEM_E097_N25` (10 tiles)
- **$26^\circ\text{N}$ Band**: `NER_DEM_E088_N26` to `NER_DEM_E097_N26` (10 tiles)
- **$27^\circ\text{N}$ Band**: `NER_DEM_E088_N27` to `NER_DEM_E097_N27` (10 tiles)
- **$28^\circ\text{N}$ Band**: `NER_DEM_E088_N28` to `NER_DEM_E097_N28` (10 tiles)
- **$29^\circ\text{N}$ Band**: `NER_DEM_E088_N29` to `NER_DEM_E097_N29` (10 tiles)

---

## 4. Operational Status & Next Steps
- **Validation Status**: **PASS (Single Tile Verified; Full Grid Pending Tile Downloads)**
- **Mosaicing Status**: **GATED / PAUSED** (Mosaicing will be executed once the remaining 89 missing tiles are downloaded).
- **Processing Status**: Slope, aspect, terrain ruggedness, and ML training remain deferred.
