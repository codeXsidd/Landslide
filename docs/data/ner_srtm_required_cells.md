# Northeast India Required SRTM Cells Acquisition Plan

## Administrative Boundary Dataset Status
> [!WARNING]
> The project currently **does not contain any official administrative boundary dataset** (such as a Shapefile, GeoJSON, or GeoPackage) in `data/` for Northeast India. State bounding boxes have been used instead to compute intersection mapping.

## Executive Summary

- **Total Required SRTM Cells (Intersecting NER States)**: `57`
- **Existing Coverage Cells (Valid on Disk)**: `24`
- **Missing Cells**: `33`
- **Cells Outside NER Bounding Box (Excluded)**: `33`

## State Boundary Intersections & Cell Inventory

| Tile ID | Extent (W/S/E/N) | Intersecting States | Area (km²) | Existing Coverage | Missing Coverage | Required for NER |
|---|---|---|---|---|---|---|
| `NER_DEM_E088_N21` | 88.0° / 21.0° / 89.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E089_N21` | 89.0° / 21.0° / 90.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E090_N21` | 90.0° / 21.0° / 91.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E091_N21` | 91.0° / 21.0° / 92.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E092_N21` | 92.0° / 21.0° / 93.0° / 22.0° | Mizoram | 11,503.8 | **True** | **False** | **True** |
| `NER_DEM_E093_N21` | 93.0° / 21.0° / 94.0° / 22.0° | Mizoram | 11,503.8 | **True** | **False** | **True** |
| `NER_DEM_E094_N21` | 94.0° / 21.0° / 95.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E095_N21` | 95.0° / 21.0° / 96.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E096_N21` | 96.0° / 21.0° / 97.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E097_N21` | 97.0° / 21.0° / 98.0° / 22.0° | None (Outside NER) | 11,503.8 | **True** | **False** | **False** |
| `NER_DEM_E088_N22` | 88.0° / 22.0° / 89.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E089_N22` | 89.0° / 22.0° / 90.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E090_N22` | 90.0° / 22.0° / 91.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E091_N22` | 91.0° / 22.0° / 92.0° / 23.0° | Tripura | 11,423.0 | **True** | **False** | **True** |
| `NER_DEM_E092_N22` | 92.0° / 22.0° / 93.0° / 23.0° | Mizoram, Tripura | 11,423.0 | **True** | **False** | **True** |
| `NER_DEM_E093_N22` | 93.0° / 22.0° / 94.0° / 23.0° | Mizoram | 11,423.0 | **True** | **False** | **True** |
| `NER_DEM_E094_N22` | 94.0° / 22.0° / 95.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E095_N22` | 95.0° / 22.0° / 96.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E096_N22` | 96.0° / 22.0° / 97.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E097_N22` | 97.0° / 22.0° / 98.0° / 23.0° | None (Outside NER) | 11,423.0 | **True** | **False** | **False** |
| `NER_DEM_E088_N23` | 88.0° / 23.0° / 89.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E089_N23` | 89.0° / 23.0° / 90.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E090_N23` | 90.0° / 23.0° / 91.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E091_N23` | 91.0° / 23.0° / 92.0° / 24.0° | Tripura | 11,338.7 | **True** | **False** | **True** |
| `NER_DEM_E092_N23` | 92.0° / 23.0° / 93.0° / 24.0° | Mizoram, Tripura | 11,338.7 | **True** | **False** | **True** |
| `NER_DEM_E093_N23` | 93.0° / 23.0° / 94.0° / 24.0° | Manipur, Mizoram | 11,338.7 | **True** | **False** | **True** |
| `NER_DEM_E094_N23` | 94.0° / 23.0° / 95.0° / 24.0° | Manipur | 11,338.7 | **True** | **False** | **True** |
| `NER_DEM_E095_N23` | 95.0° / 23.0° / 96.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E096_N23` | 96.0° / 23.0° / 97.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E097_N23` | 97.0° / 23.0° / 98.0° / 24.0° | None (Outside NER) | 11,338.7 | **True** | **False** | **False** |
| `NER_DEM_E088_N24` | 88.0° / 24.0° / 89.0° / 25.0° | None (Outside NER) | 11,250.9 | **True** | **False** | **False** |
| `NER_DEM_E089_N24` | 89.0° / 24.0° / 90.0° / 25.0° | Assam | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E090_N24` | 90.0° / 24.0° / 91.0° / 25.0° | Assam | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E091_N24` | 91.0° / 24.0° / 92.0° / 25.0° | Assam, Tripura | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E092_N24` | 92.0° / 24.0° / 93.0° / 25.0° | Assam, Mizoram, Tripura | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E093_N24` | 93.0° / 24.0° / 94.0° / 25.0° | Assam, Manipur, Mizoram | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E094_N24` | 94.0° / 24.0° / 95.0° / 25.0° | Assam, Manipur | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E095_N24` | 95.0° / 24.0° / 96.0° / 25.0° | Assam | 11,250.9 | **True** | **False** | **True** |
| `NER_DEM_E096_N24` | 96.0° / 24.0° / 97.0° / 25.0° | None (Outside NER) | 11,250.9 | **True** | **False** | **False** |
| `NER_DEM_E097_N24` | 97.0° / 24.0° / 98.0° / 25.0° | None (Outside NER) | 11,250.9 | **True** | **False** | **False** |
| `NER_DEM_E088_N25` | 88.0° / 25.0° / 89.0° / 26.0° | None (Outside NER) | 11,159.7 | **True** | **False** | **False** |
| `NER_DEM_E089_N25` | 89.0° / 25.0° / 90.0° / 26.0° | Assam, Meghalaya | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E090_N25` | 90.0° / 25.0° / 91.0° / 26.0° | Assam, Meghalaya | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E091_N25` | 91.0° / 25.0° / 92.0° / 26.0° | Assam, Meghalaya | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E092_N25` | 92.0° / 25.0° / 93.0° / 26.0° | Assam, Meghalaya | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E093_N25` | 93.0° / 25.0° / 94.0° / 26.0° | Assam, Nagaland, Manipur | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E094_N25` | 94.0° / 25.0° / 95.0° / 26.0° | Assam, Nagaland, Manipur | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E095_N25` | 95.0° / 25.0° / 96.0° / 26.0° | Assam, Nagaland | 11,159.7 | **True** | **False** | **True** |
| `NER_DEM_E096_N25` | 96.0° / 25.0° / 97.0° / 26.0° | None (Outside NER) | 11,159.7 | **True** | **False** | **False** |
| `NER_DEM_E097_N25` | 97.0° / 25.0° / 98.0° / 26.0° | None (Outside NER) | 11,159.7 | **True** | **False** | **False** |
| `NER_DEM_E088_N26` | 88.0° / 26.0° / 89.0° / 27.0° | None (Outside NER) | 11,065.1 | **True** | **False** | **False** |
| `NER_DEM_E089_N26` | 89.0° / 26.0° / 90.0° / 27.0° | Assam, Meghalaya | 11,065.1 | **True** | **False** | **True** |
| `NER_DEM_E090_N26` | 90.0° / 26.0° / 91.0° / 27.0° | Assam, Meghalaya | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E091_N26` | 91.0° / 26.0° / 92.0° / 27.0° | Arunachal Pradesh, Assam, Meghalaya | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E092_N26` | 92.0° / 26.0° / 93.0° / 27.0° | Arunachal Pradesh, Assam, Meghalaya | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E093_N26` | 93.0° / 26.0° / 94.0° / 27.0° | Arunachal Pradesh, Assam, Nagaland | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E094_N26` | 94.0° / 26.0° / 95.0° / 27.0° | Arunachal Pradesh, Assam, Nagaland | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E095_N26` | 95.0° / 26.0° / 96.0° / 27.0° | Arunachal Pradesh, Assam, Nagaland | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E096_N26` | 96.0° / 26.0° / 97.0° / 27.0° | Arunachal Pradesh | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E097_N26` | 97.0° / 26.0° / 98.0° / 27.0° | Arunachal Pradesh | 11,065.1 | **False** | **True** | **True** |
| `NER_DEM_E088_N27` | 88.0° / 27.0° / 89.0° / 28.0° | Sikkim | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E089_N27` | 89.0° / 27.0° / 90.0° / 28.0° | Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E090_N27` | 90.0° / 27.0° / 91.0° / 28.0° | Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E091_N27` | 91.0° / 27.0° / 92.0° / 28.0° | Arunachal Pradesh, Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E092_N27` | 92.0° / 27.0° / 93.0° / 28.0° | Arunachal Pradesh, Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E093_N27` | 93.0° / 27.0° / 94.0° / 28.0° | Arunachal Pradesh, Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E094_N27` | 94.0° / 27.0° / 95.0° / 28.0° | Arunachal Pradesh, Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E095_N27` | 95.0° / 27.0° / 96.0° / 28.0° | Arunachal Pradesh, Assam | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E096_N27` | 96.0° / 27.0° / 97.0° / 28.0° | Arunachal Pradesh | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E097_N27` | 97.0° / 27.0° / 98.0° / 28.0° | Arunachal Pradesh | 10,967.1 | **False** | **True** | **True** |
| `NER_DEM_E088_N28` | 88.0° / 28.0° / 89.0° / 29.0° | Sikkim | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E089_N28` | 89.0° / 28.0° / 90.0° / 29.0° | None (Outside NER) | 10,865.8 | **False** | **True** | **False** |
| `NER_DEM_E090_N28` | 90.0° / 28.0° / 91.0° / 29.0° | None (Outside NER) | 10,865.8 | **False** | **True** | **False** |
| `NER_DEM_E091_N28` | 91.0° / 28.0° / 92.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E092_N28` | 92.0° / 28.0° / 93.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E093_N28` | 93.0° / 28.0° / 94.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E094_N28` | 94.0° / 28.0° / 95.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E095_N28` | 95.0° / 28.0° / 96.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E096_N28` | 96.0° / 28.0° / 97.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E097_N28` | 97.0° / 28.0° / 98.0° / 29.0° | Arunachal Pradesh | 10,865.8 | **False** | **True** | **True** |
| `NER_DEM_E088_N29` | 88.0° / 29.0° / 89.0° / 30.0° | None (Outside NER) | 10,761.2 | **False** | **True** | **False** |
| `NER_DEM_E089_N29` | 89.0° / 29.0° / 90.0° / 30.0° | None (Outside NER) | 10,761.2 | **False** | **True** | **False** |
| `NER_DEM_E090_N29` | 90.0° / 29.0° / 91.0° / 30.0° | None (Outside NER) | 10,761.2 | **False** | **True** | **False** |
| `NER_DEM_E091_N29` | 91.0° / 29.0° / 92.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E092_N29` | 92.0° / 29.0° / 93.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E093_N29` | 93.0° / 29.0° / 94.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E094_N29` | 94.0° / 29.0° / 95.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E095_N29` | 95.0° / 29.0° / 96.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E096_N29` | 96.0° / 29.0° / 97.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
| `NER_DEM_E097_N29` | 97.0° / 29.0° / 98.0° / 30.0° | Arunachal Pradesh | 10,761.2 | **False** | **True** | **True** |
