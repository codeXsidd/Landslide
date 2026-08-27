# SRTM GL1 Digital Elevation Model (DEM) Inventory & Inspection Report

## Overview
This report provides a detailed inspection of the NASA SRTM GL1 1-arcsecond (~30m) Digital Elevation Model (DEM) raster dataset downloaded from OpenTopography. The raw files are stored intact under `data/raw/terrain/dem/` without any modification.

---

## 1. File Inspection Summary

| Attribute | Details / Value |
|---|---|
| **File Name** | `output_SRTMGL1.tif` (Archive: `rasters_SRTMGL1.tar.gz`) |
| **File Format** | GeoTIFF (GTiff, uncompressed/tiled raster) |
| **File Size** | Extracted Raster: `11,717,042 bytes` (~11.17 MB)<br>Tar.gz Archive: `11,597,212 bytes` (~11.06 MB) |
| **Coordinate Reference System (CRS)** | **EPSG:4326** (WGS 84 / Geographic latitude-longitude) |
| **Spatial Resolution** | `0.0002777777777778° x 0.0002777777777778°`<br>(1 arc-second / ~30.8 meters at equator) |
| **Width (Columns)** | `3,600` pixels |
| **Height (Rows)** | `3,600` pixels |
| **Number of Bands** | `1` band (Elevation in meters above WGS84 EGM96 geoid) |
| **Bounding Box (WGS84)** | **Min Lon**: `91.999861° E` (~92.00° E)<br>**Max Lon**: `92.999861° E` (~93.00° E)<br>**Min Lat**: `24.000139° N` (~24.00° N)<br>**Max Lat**: `25.000139° N` (~25.00° N) |
| **NoData Value** | `-32768` (GDAL NoData Tag 42113) |
| **Minimum Elevation** | `-38` meters |
| **Maximum Elevation** | `1,254` meters |
| **Mean Elevation** | `106.98` meters |
| **Median Elevation** | `48.0` meters |
| **Raster Validity** | **VALID** (100% of 12,960,000 pixels are valid, readable, and non-corrupt; 0 NoData pixels in tile) |
| **Assam Coverage** | **YES** (Covers a 1° x 1° spatial tile spanning southern Assam including Cachar, Hailakandi, Karimganj, and Dima Hasao districts) |

---

## 2. Raster Preview

A spatial visualization of the elevation model was generated and saved to [`docs/data/srtm_dem_preview.png`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/srtm_dem_preview.png).

![SRTM DEM Preview](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/srtm_dem_preview.png)

---

## 3. Detailed Data Integrity Verification

- **Band Properties**: Single band containing 32-bit signed integer pixel depth representing terrain elevation (meters).
- **Spatial Coverage & Alignment**:
  - The raster tile strictly aligns with 1-arcsecond grid cells.
  - Extents span 24.00°N - 25.00°N latitude and 92.00°E - 93.00°E longitude.
- **Topographic Characteristics**:
  - Floodplains & river valleys (Barak Valley): ~10m – 50m MSL.
  - Surrounding hill ranges (Barail Range / Lushai Hills foothills): up to 1,254m MSL.
- **File Integrity**: Raw raster files in `data/raw/terrain/dem/` have been kept completely unmodified as mandated.

---

## 4. Status
- **Validation Result**: **PASS**
- **Next Steps**: Ready for terrain feature extraction (slope, aspect, elevation profiles) in future processing steps.
