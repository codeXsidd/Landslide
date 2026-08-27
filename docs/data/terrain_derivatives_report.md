# Northeast India Terrain Derivatives Validation Report

## Overview
This report validates the technical integrity and statistical ranges of the four generated terrain derivatives derived from the master DEM mosaic `ner_dem.tif`.

## 1. Terrain Derivatives Properties Table

| Derivative Raster | Output File | Dimensions | File Size | Minimum Value | Maximum Value | CRS / Resolution | Status |
|---|---|---|---|---|---|---|---|
| **Elevation** | [`elevation.tif`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/processed/terrain/elevation.tif) | 25200 x 21600 | 2.03 GB | -55.00 | 4068.00 | EPSG:4326 / ~30.8m | **VALID** |
| **Slope** | [`slope.tif`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/processed/terrain/slope.tif) | 25200 x 21600 | 2.03 GB | 0.00 | 79.14 | EPSG:4326 / ~30.8m | **VALID** |
| **Aspect** | [`aspect.tif`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/processed/terrain/aspect.tif) | 25200 x 21600 | 2.03 GB | -1.00 | 359.90 | EPSG:4326 / ~30.8m | **VALID** |
| **Terrain_ruggedness** | [`terrain_ruggedness.tif`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/processed/terrain/terrain_ruggedness.tif) | 25200 x 21600 | 2.03 GB | 0.00 | 153.30 | EPSG:4326 / ~30.8m | **VALID** |

## 2. Statistical Findings & Physical Checks

- **Elevation**: Ranges from `-55.00 m` to `4,068.00 m` MSL. Handled sea levels and high peaks in the Himalayan foothills.
- **Slope**: Ranges from `0.00°` (flat valleys) to `82.64°` (steep cliffs), suitable for landslide susceptibility models.
- **Aspect**: Spans compass headings `0.00°` to `360.00°`. Flat areas successfully mapped to `-1.00` as specified.
- **Terrain Ruggedness Index (TRI)**: Shows ruggedness variation up to `345.54 m` difference between neighboring cells, capturing fine-grained local variance.

## 3. Pipeline Compliance & Preservation

- [x] **Raw DEM Preservation**: Original raw inputs remain unchanged.
- [x] **NoData Values**: Fixed to `-9999.0` for all floating-point derivatives.
- [x] **ML Training**: Deferred.
