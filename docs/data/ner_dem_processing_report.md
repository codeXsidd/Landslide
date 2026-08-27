# Northeast India SRTM GL1 DEM Tile Inventory & Processing Audit Report

## Executive Summary
This document provides a comprehensive inventory and processing audit of the NASA SRTM GL1 30 m Digital Elevation Model (DEM) tiles located in `data/raw/terrain/dem/`, matched against the official acquisition plan ([`docs/data/ner_dem_tile_plan.md`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_dem_tile_plan.md)).

> [!WARNING]
> **Mosaic Status**: **PAUSED / DEFERRED**  
> As mandated by project requirements (*"Do not mosaic yet if any required tile is missing"*), full-region mosaicing and derived raster generation (`elevation.tif`, `slope.tif`, `aspect.tif`, `terrain_ruggedness.tif`) are **paused** because 89 out of the 90 planned tiles are missing from the raw directory. Raw files have been kept 100% intact.

---

## 1. Grid & Inventory Audit Summary

| Audit Item | Status / Findings |
|---|---|
| **Total Planned Tiles** | `90` tiles ($88.0^\circ\text{E} - 98.0^\circ\text{E}, 21.0^\circ\text{N} - 30.0^\circ\text{N}$) |
| **Present Tiles** | `1` tile (`NER_DEM_E092_N24`, file `output_SRTMGL1.tif`) |
| **Missing Tiles** | `89` tiles (`NER_DEM_E088_N21` through `NER_DEM_E097_N29`, excluding `NER_DEM_E092_N24`) |
| **CRS Consistency** | **EPSG:4326** (WGS 84 Geographic) |
| **Spatial Resolution** | `0.0002777777777778° x 0.0002777777777778°` (~30.8 m / 1 arc-second) |
| **NoData Value** | `-32768` (0 NoData pixels in present tile, 12,960,000 / 12,960,000 valid pixels) |
| **Overlaps** | **None** (No overlapping tiles in current raw folder) |
| **Gaps** | **EXTENSIVE** (89 out of 90 planned $1^\circ \times 1^\circ$ tile slots are missing) |
| **Duplicate Tiles** | **None** (0 duplicates found) |
| **Mosaic Status** | **NOT CREATED** (Gated on downloading remaining 89 tiles) |

---

## 2. Present Tile Specification

| Attribute | Tile `NER_DEM_E092_N24` |
|---|---|
| **Raw File Name** | `output_SRTMGL1.tif` (Archive: `rasters_SRTMGL1.tar.gz`) |
| **Bounding Box** | **West**: `91.999861° E`<br>**South**: `24.000139° N`<br>**East**: `92.999861° E`<br>**North**: `25.000139° N` |
| **CRS** | `EPSG:4326` (WGS 84) |
| **Resolution** | `1 arc-second` (~30 m per pixel) |
| **Dimensions** | `3,600 x 3,600` pixels |
| **Elevation Range** | `-38 m` to `1,254 m` above MSL |
| **States Covered** | Southern Assam (Cachar, Hailakandi, Karimganj, Dima Hasao), Mizoram, Tripura |

---

## 3. Missing Tiles Breakdown (89 Tiles)

The following 89 planned grid cells are absent from `data/raw/terrain/dem/`:

- **Latitude Band 21°N**: `NER_DEM_E088_N21` to `NER_DEM_E097_N21` (10 tiles)
- **Latitude Band 22°N**: `NER_DEM_E088_N22` to `NER_DEM_E097_N22` (10 tiles)
- **Latitude Band 23°N**: `NER_DEM_E088_N23` to `NER_DEM_E097_N23` (10 tiles)
- **Latitude Band 24°N**: `NER_DEM_E088_N24` to `NER_DEM_E091_N24` and `NER_DEM_E093_N24` to `NER_DEM_E097_N24` (9 tiles)
- **Latitude Band 25°N**: `NER_DEM_E088_N25` to `NER_DEM_E097_N25` (10 tiles)
- **Latitude Band 26°N**: `NER_DEM_E088_N26` to `NER_DEM_E097_N26` (10 tiles)
- **Latitude Band 27°N**: `NER_DEM_E088_N27` to `NER_DEM_E097_N27` (10 tiles)
- **Latitude Band 28°N**: `NER_DEM_E088_N28` to `NER_DEM_E097_N28` (10 tiles)
- **Latitude Band 29°N**: `NER_DEM_E088_N29` to `NER_DEM_E097_N29` (10 tiles)

---

## 4. Single-Tile Preview Visualizations

Elevation and slope previews were generated for the verified present tile `NER_DEM_E092_N24` (`output_SRTMGL1.tif`):

### Elevation Preview
Saved to [`docs/data/ner_elevation_preview.png`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_elevation_preview.png)
![Elevation Preview](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_elevation_preview.png)

### Slope Preview
Saved to [`docs/data/ner_slope_preview.png`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_slope_preview.png)
![Slope Preview](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_slope_preview.png)

---

## 5. Next Action Items
1. Download remaining 89 tiles specified in [`docs/data/ner_dem_tile_plan.md`](file:///c:/Users/siddh/Music/ner%20landslide%20project/docs/data/ner_dem_tile_plan.md).
2. Once all 90 tiles exist in `data/raw/terrain/dem/`, execute GDAL mosaic and clip to produce:
   - `data/processed/terrain/ner_dem.tif`
   - `data/processed/terrain/elevation.tif`
   - `data/processed/terrain/slope.tif`
   - `data/processed/terrain/aspect.tif`
   - `data/processed/terrain/terrain_ruggedness.tif`
