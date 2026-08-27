# NASA SRTM GL1 30m DEM GeoTIFF Tile Validation Report

## Executive Summary
This document provides a comprehensive technical audit of raw SRTM GL1 30 m Digital Elevation Model (DEM) GeoTIFF rasters stored in `data/raw/terrain/dem/`. Non-raster archive files (e.g., `rasters_SRTMGL1.tar.gz`) have been explicitly excluded from raster analysis in accordance with validation directives.

> [!IMPORTANT]
> - Raw DEM rasters in `data/raw/terrain/dem/` remain **100% unmodified and intact**.
> - Mosaicing, slope calculations, and ML model training remain **unexecuted** as mandated.

---

## 1. Single-Raster Detailed Technical Audit

### Raster 1: `output_SRTMGL1.tif`

| Parameter | Inspection Result / Value | Status |
|---|---|---|
| **1. File Name** | `output_SRTMGL1.tif` (Archive: `rasters_SRTMGL1.tar.gz` excluded) | Valid |
| **2. Readability** | **PASS** (100% readable; 12,960,000 / 12,960,000 pixels verified without I/O or header corruption) | **PASS** |
| **3. Band Count** | `1` band (32-bit signed integer terrain elevation) | **PASS** |
| **4. Coordinate Reference System (CRS)** | **EPSG:4326** (WGS 84 / Geographic latitude-longitude) | **PASS** |
| **5. Spatial Resolution** | `0.0002777777777778° x 0.0002777777777778°`<br>(1 arc-second / ~30.8 m at center latitude $24.5^\circ\text{N}$) | **PASS** |
| **6. Width (Columns)** | `3,600` pixels | **PASS** |
| **7. Height (Rows)** | `3,600` pixels | **PASS** |
| **8. Bounding Box (WGS84)** | - **West ($x_{\min}$)**: `91.999861° E`<br>- **South ($y_{\min}$)**: `24.000139° N`<br>- **East ($x_{\max}$)**: `92.999861° E`<br>- **North ($y_{\max}$)**: `25.000139° N` | **PASS** |
| **9. NoData Value** | `-32768` (GDAL NoData Tag 42113; 0 NoData pixels present in tile) | **PASS** |
| **10. Minimum Elevation** | `-38` meters MSL | **PASS** |
| **11. Maximum Elevation** | `1,254` meters MSL | **PASS** |
| **12. Overlap with Other Tiles** | Overlaps the southwest quadrant of composite **Tile_A** ($88^\circ - 93^\circ\text{E}, 21^\circ - 25^\circ\text{N}$). Zero overlap conflicts with existing raw files (single file present). | **PASS** |

---

## 2. Spatial Coverage & Multi-Tile Relationship

A visual coverage map displaying the study extent ($88.0^\circ-98.0^\circ\text{E}, 21.0^\circ-30.0^\circ\text{N}$), the validated raw GeoTIFF `output_SRTMGL1.tif`, and the 4 composite download tiles (Tile A, B, C, D) has been generated:

👉 [`docs/data/ner_srtm_tile_coverage.png`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_srtm_tile_coverage.png)

![SRTM DEM Coverage Map](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_srtm_tile_coverage.png)

---

## 3. Excluded Non-Raster Archives

- **File**: `rasters_SRTMGL1.tar.gz` (Size: `11,597,212 bytes`)
- **Reason for Exclusion**: Compressed archive container; excluded from direct GeoTIFF raster parameter auditing as instructed.

---

## 4. Summary & Operational Status

- **Raster Readability**: **100% PASS**
- **CRS & Grid Alignment**: **Compliant (EPSG:4326, 1 arc-sec)**
- **Raw File Preservation**: **100% Intact**
- **Mosaicing & ML Training**: **DEFERRED**
