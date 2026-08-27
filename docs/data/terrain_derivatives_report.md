# Terrain Derivatives Calculation & Validation Report

## Executive Summary
This report documents the calculation and technical validation of digital terrain derivatives generated from the NASA SRTM GL1 30 m Digital Elevation Model (`data/processed/terrain/ner_dem.tif`). All output rasters are stored under `data/processed/terrain/` as standardized 32-bit floating-point GeoTIFF rasters.

---

## 1. Geospatial Calculation Methodology

### Base DEM
- **Input File**: [`data/processed/terrain/ner_dem.tif`](file:///c:/Users/siddh/Music/ner%20landslide%20project/data/processed/terrain/ner_dem.tif)
- **Spatial Resolution**: 1 arc-second (~30.8 m $\times$ 28.1 m at center latitude $24.5^\circ\text{N}$).

---

### A. Elevation (`elevation.tif`)
- **Formula**: Direct 32-bit floating-point extraction of terrain height above MSL (WGS84 EGM96 geoid).
- **NoData Encoding**: `-9999.0`

---

### B. Slope (`slope.tif`)
- **Geospatial Method**: Horn's 2nd-order central finite differences ($3 \times 3$ stencil) with latitude-adjusted metric grid cell scaling:
  $$\Delta y = R \cdot \Delta\text{lat} \approx 30.870\text{ m}$$
  $$\Delta x(\phi) = R \cdot \cos(\phi) \cdot \Delta\text{lon} \approx 28.090\text{ m (at } \phi = 24.5^\circ\text{)}$$
- **Gradients**:
  $$g_x = \frac{(Z_{i-1, j+1} + 2Z_{i, j+1} + Z_{i+1, j+1}) - (Z_{i-1, j-1} + 2Z_{i, j-1} + Z_{i+1, j-1})}{8 \Delta x}$$
  $$g_y = \frac{(Z_{i-1, j-1} + 2Z_{i-1, j} + Z_{i-1, j+1}) - (Z_{i+1, j-1} + 2Z_{i+1, j} + Z_{i+1, j+1})}{8 \Delta y}$$
- **Slope Angle**:
  $$\text{Slope} = \arctan\left(\sqrt{g_x^2 + g_y^2}\right) \cdot \frac{180^\circ}{\pi} \quad (\text{units: degrees, } 0^\circ - 90^\circ)$$

---

### C. Aspect (`aspect.tif`)
- **Geospatial Method**: Direction of maximum downhill gradient:
  $$\text{Aspect} = \text{mod}\left(90^\circ - \text{atan2}(g_y, -g_x) \cdot \frac{180^\circ}{\pi}, 360^\circ\right)$$
- **Flat Surface Convention**: Flat terrain ($\text{Slope} < 0.01^\circ$) is encoded as `-1.0^\circ`.

---

### D. Terrain Ruggedness Index (`terrain_ruggedness.tif`)
- **Geospatial Method**: Riley et al. (1999) Terrain Ruggedness Index (TRI), quantifying localized elevation heterogeneity across a $3 \times 3$ neighborhood:
  $$\text{TRI} = \sqrt{\frac{1}{8} \sum_{k=1}^{8} (Z_0 - Z_k)^2} \quad (\text{units: meters})$$
  where $Z_0$ is the central pixel elevation and $Z_k$ are the 8 neighboring elevations.

---

## 2. Multi-Raster Validation Matrix

| Parameter | `ner_dem.tif` | `elevation.tif` | `slope.tif` | `aspect.tif` | `terrain_ruggedness.tif` |
|---|---|---|---|---|---|
| **CRS** | **EPSG:4326** | **EPSG:4326** | **EPSG:4326** | **EPSG:4326** | **EPSG:4326** |
| **Dimensions** | `3,600 x 3,600` | `3,600 x 3,600` | `3,600 x 3,600` | `3,600 x 3,600` | `3,600 x 3,600` |
| **Resolution** | `0.00027778°` | `0.00027778°` | `0.00027778°` | `0.00027777°` | `0.00027777°` |
| **West Bound** | `91.999861° E` | `91.999861° E` | `91.999861° E` | `91.999861° E` | `91.999861° E` |
| **South Bound** | `24.000139° N` | `24.000139° N` | `24.000139° N` | `24.000139° N` | `24.000139° N` |
| **East Bound** | `92.999861° E` | `92.999861° E` | `92.999861° E` | `92.999861° E` | `92.999861° E` |
| **North Bound** | `25.000139° N` | `25.000139° N` | `25.000139° N` | `25.000139° N` | `25.000139° N` |
| **NoData Value** | `-32768` | `-9999.0` | `-9999.0` | `-9999.0` | `-9999.0` |
| **Min Value** | `-38.00 m` | `-38.00 m` | `0.00°` | `-1.00°` (flat) | `0.00 m` |
| **Max Value** | `1,254.00 m` | `1,254.00 m` | `72.69°` | `359.77°` | `101.15 m` |
| **Mean Value** | `106.98 m` | `106.98 m` | `8.18°` | `174.97°` | `4.35 m` |
| **File Size** | `11.72 MB` | `51.84 MB` | `51.84 MB` | `51.84 MB` | `51.84 MB` |

---

## 3. Operational Status
- **Validation Status**: **PASS (All 5 terrain rasters verified and compliant)**
- **ML Training Status**: **DEFERRED** (Ready for feature engineering integration).
