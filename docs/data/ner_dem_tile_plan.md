# Northeast India SRTM GL1 DEM Tile Acquisition Plan

## Executive Summary
This document details the complete tile grid for acquiring the 30 m NASA SRTM GL1 Digital Elevation Model (DEM) across the Northeast India (NER) study region ($88.0^\circ\text{E} - 98.0^\circ\text{E}, 21.0^\circ\text{N} - 30.0^\circ\text{N}$). Each query tile is $1.0^\circ \times 1.0^\circ$ (~$10,760 - 11,500\text{ km}^2$), safely within OpenTopography single-request query limits.

> [!NOTE]
> Existing raw test tile `NER_DEM_E092_N24` ($92.0^\circ-93.0^\circ\text{E}, 24.0^\circ-25.0^\circ\text{N}$) in `data/raw/terrain/dem/output_SRTMGL1.tif` is already downloaded (**Needs Download = NO**). No duplicate download is requested.

## Target Region Bounding Box
- **West ($x_{\min}$)**: `88.0° E`
- **South ($y_{\min}$)**: `21.0° N`
- **East ($x_{\max}$)**: `98.0° E`
- **North ($y_{\max}$)**: `30.0° N`
- **Total Extent**: $10^\circ$ Longitude $\times$ $9^\circ$ Latitude (90 tiles)

## OpenTopography Query Limits & Safeguards
- Max Query Limit per API Call: $100,000\text{ km}^2$
- Planned Tile Area: ~$11,000\text{ km}^2$ per tile (11% of safety cap)
- Resolution: 1 arc-second (~30 m / $3,600 \times 3,600$ pixels per tile)

## Complete 90-Tile Master Plan

| Tile ID | Xmin (°E) | Ymin (°N) | Xmax (°E) | Ymax (°N) | Est. Area (km²) | Already Covered by Raw DEM? | Needs Download? | Covered States / Region |
|---|---|---|---|---|---|---|---|---|
| `NER_DEM_E088_N21` | 88.0 | 21.0 | 89.0 | 22.0 | 11,503.8 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E089_N21` | 89.0 | 21.0 | 90.0 | 22.0 | 11,503.8 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E090_N21` | 90.0 | 21.0 | 91.0 | 22.0 | 11,503.8 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E091_N21` | 91.0 | 21.0 | 92.0 | 22.0 | 11,503.8 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E092_N21` | 92.0 | 21.0 | 93.0 | 22.0 | 11,503.8 | **NO** | **YES** | Mizoram |
| `NER_DEM_E093_N21` | 93.0 | 21.0 | 94.0 | 22.0 | 11,503.8 | **NO** | **YES** | Mizoram |
| `NER_DEM_E094_N21` | 94.0 | 21.0 | 95.0 | 22.0 | 11,503.8 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E095_N21` | 95.0 | 21.0 | 96.0 | 22.0 | 11,503.8 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E096_N21` | 96.0 | 21.0 | 97.0 | 22.0 | 11,503.8 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E097_N21` | 97.0 | 21.0 | 98.0 | 22.0 | 11,503.8 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E088_N22` | 88.0 | 22.0 | 89.0 | 23.0 | 11,423.0 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E089_N22` | 89.0 | 22.0 | 90.0 | 23.0 | 11,423.0 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E090_N22` | 90.0 | 22.0 | 91.0 | 23.0 | 11,423.0 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E091_N22` | 91.0 | 22.0 | 92.0 | 23.0 | 11,423.0 | **NO** | **YES** | Tripura |
| `NER_DEM_E092_N22` | 92.0 | 22.0 | 93.0 | 23.0 | 11,423.0 | **NO** | **YES** | Mizoram, Tripura |
| `NER_DEM_E093_N22` | 93.0 | 22.0 | 94.0 | 23.0 | 11,423.0 | **NO** | **YES** | Mizoram |
| `NER_DEM_E094_N22` | 94.0 | 22.0 | 95.0 | 23.0 | 11,423.0 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E095_N22` | 95.0 | 22.0 | 96.0 | 23.0 | 11,423.0 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E096_N22` | 96.0 | 22.0 | 97.0 | 23.0 | 11,423.0 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E097_N22` | 97.0 | 22.0 | 98.0 | 23.0 | 11,423.0 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E088_N23` | 88.0 | 23.0 | 89.0 | 24.0 | 11,338.7 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E089_N23` | 89.0 | 23.0 | 90.0 | 24.0 | 11,338.7 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E090_N23` | 90.0 | 23.0 | 91.0 | 24.0 | 11,338.7 | **NO** | **YES** | Bangladesh (Border Region) |
| `NER_DEM_E091_N23` | 91.0 | 23.0 | 92.0 | 24.0 | 11,338.7 | **NO** | **YES** | Tripura |
| `NER_DEM_E092_N23` | 92.0 | 23.0 | 93.0 | 24.0 | 11,338.7 | **NO** | **YES** | Mizoram, Tripura |
| `NER_DEM_E093_N23` | 93.0 | 23.0 | 94.0 | 24.0 | 11,338.7 | **NO** | **YES** | Manipur, Mizoram |
| `NER_DEM_E094_N23` | 94.0 | 23.0 | 95.0 | 24.0 | 11,338.7 | **NO** | **YES** | Manipur |
| `NER_DEM_E095_N23` | 95.0 | 23.0 | 96.0 | 24.0 | 11,338.7 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E096_N23` | 96.0 | 23.0 | 97.0 | 24.0 | 11,338.7 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E097_N23` | 97.0 | 23.0 | 98.0 | 24.0 | 11,338.7 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E088_N24` | 88.0 | 24.0 | 89.0 | 25.0 | 11,250.9 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E089_N24` | 89.0 | 24.0 | 90.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam |
| `NER_DEM_E090_N24` | 90.0 | 24.0 | 91.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam |
| `NER_DEM_E091_N24` | 91.0 | 24.0 | 92.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam, Tripura |
| `NER_DEM_E092_N24` | 92.0 | 24.0 | 93.0 | 25.0 | 11,250.9 | **YES** | **NO** | Assam, Mizoram, Tripura |
| `NER_DEM_E093_N24` | 93.0 | 24.0 | 94.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam, Manipur, Mizoram |
| `NER_DEM_E094_N24` | 94.0 | 24.0 | 95.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam, Manipur |
| `NER_DEM_E095_N24` | 95.0 | 24.0 | 96.0 | 25.0 | 11,250.9 | **NO** | **YES** | Assam |
| `NER_DEM_E096_N24` | 96.0 | 24.0 | 97.0 | 25.0 | 11,250.9 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E097_N24` | 97.0 | 24.0 | 98.0 | 25.0 | 11,250.9 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E088_N25` | 88.0 | 25.0 | 89.0 | 26.0 | 11,159.7 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E089_N25` | 89.0 | 25.0 | 90.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Meghalaya |
| `NER_DEM_E090_N25` | 90.0 | 25.0 | 91.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Meghalaya |
| `NER_DEM_E091_N25` | 91.0 | 25.0 | 92.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Meghalaya |
| `NER_DEM_E092_N25` | 92.0 | 25.0 | 93.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Meghalaya |
| `NER_DEM_E093_N25` | 93.0 | 25.0 | 94.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Nagaland, Manipur |
| `NER_DEM_E094_N25` | 94.0 | 25.0 | 95.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Nagaland, Manipur |
| `NER_DEM_E095_N25` | 95.0 | 25.0 | 96.0 | 26.0 | 11,159.7 | **NO** | **YES** | Assam, Nagaland |
| `NER_DEM_E096_N25` | 96.0 | 25.0 | 97.0 | 26.0 | 11,159.7 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E097_N25` | 97.0 | 25.0 | 98.0 | 26.0 | 11,159.7 | **NO** | **YES** | Myanmar (Border Region) |
| `NER_DEM_E088_N26` | 88.0 | 26.0 | 89.0 | 27.0 | 11,065.1 | **NO** | **YES** | West Bengal (North Bengal) |
| `NER_DEM_E089_N26` | 89.0 | 26.0 | 90.0 | 27.0 | 11,065.1 | **NO** | **YES** | Assam, Meghalaya, West Bengal (North Bengal) |
| `NER_DEM_E090_N26` | 90.0 | 26.0 | 91.0 | 27.0 | 11,065.1 | **NO** | **YES** | Assam, Meghalaya |
| `NER_DEM_E091_N26` | 91.0 | 26.0 | 92.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh, Assam, Meghalaya |
| `NER_DEM_E092_N26` | 92.0 | 26.0 | 93.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh, Assam, Meghalaya |
| `NER_DEM_E093_N26` | 93.0 | 26.0 | 94.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh, Assam, Nagaland |
| `NER_DEM_E094_N26` | 94.0 | 26.0 | 95.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh, Assam, Nagaland |
| `NER_DEM_E095_N26` | 95.0 | 26.0 | 96.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh, Assam, Nagaland |
| `NER_DEM_E096_N26` | 96.0 | 26.0 | 97.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E097_N26` | 97.0 | 26.0 | 98.0 | 27.0 | 11,065.1 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E088_N27` | 88.0 | 27.0 | 89.0 | 28.0 | 10,967.1 | **NO** | **YES** | Sikkim, West Bengal (North Bengal) |
| `NER_DEM_E089_N27` | 89.0 | 27.0 | 90.0 | 28.0 | 10,967.1 | **NO** | **YES** | Assam, West Bengal (North Bengal) |
| `NER_DEM_E090_N27` | 90.0 | 27.0 | 91.0 | 28.0 | 10,967.1 | **NO** | **YES** | Assam |
| `NER_DEM_E091_N27` | 91.0 | 27.0 | 92.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh, Assam |
| `NER_DEM_E092_N27` | 92.0 | 27.0 | 93.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh, Assam |
| `NER_DEM_E093_N27` | 93.0 | 27.0 | 94.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh, Assam |
| `NER_DEM_E094_N27` | 94.0 | 27.0 | 95.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh, Assam |
| `NER_DEM_E095_N27` | 95.0 | 27.0 | 96.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh, Assam |
| `NER_DEM_E096_N27` | 96.0 | 27.0 | 97.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E097_N27` | 97.0 | 27.0 | 98.0 | 28.0 | 10,967.1 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E088_N28` | 88.0 | 28.0 | 89.0 | 29.0 | 10,865.8 | **NO** | **YES** | Sikkim |
| `NER_DEM_E089_N28` | 89.0 | 28.0 | 90.0 | 29.0 | 10,865.8 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E090_N28` | 90.0 | 28.0 | 91.0 | 29.0 | 10,865.8 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E091_N28` | 91.0 | 28.0 | 92.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E092_N28` | 92.0 | 28.0 | 93.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E093_N28` | 93.0 | 28.0 | 94.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E094_N28` | 94.0 | 28.0 | 95.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E095_N28` | 95.0 | 28.0 | 96.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E096_N28` | 96.0 | 28.0 | 97.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E097_N28` | 97.0 | 28.0 | 98.0 | 29.0 | 10,865.8 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E088_N29` | 88.0 | 29.0 | 89.0 | 30.0 | 10,761.2 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E089_N29` | 89.0 | 29.0 | 90.0 | 30.0 | 10,761.2 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E090_N29` | 90.0 | 29.0 | 91.0 | 30.0 | 10,761.2 | **NO** | **YES** | Neighboring / International Border |
| `NER_DEM_E091_N29` | 91.0 | 29.0 | 92.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E092_N29` | 92.0 | 29.0 | 93.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E093_N29` | 93.0 | 29.0 | 94.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E094_N29` | 94.0 | 29.0 | 95.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E095_N29` | 95.0 | 29.0 | 96.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E096_N29` | 96.0 | 29.0 | 97.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |
| `NER_DEM_E097_N29` | 97.0 | 29.0 | 98.0 | 30.0 | 10,761.2 | **NO** | **YES** | Arunachal Pradesh |

## Summary Statistics
- **Total Planned Tiles**: 90
- **Already Covered Tiles**: 1 (`NER_DEM_E092_N24`)
- **Tiles Still Needing Download**: 89
