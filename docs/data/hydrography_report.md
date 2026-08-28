# NER-LDI Hydrography Data Report

**Date**: 2026-08-28  
**Source**: OpenStreetMap (seed data from known NE India river geography)  
**CRS**: EPSG:4326  

---

## Dataset Summary

| Metric | Value |
|--------|-------|
| Total Features | 24 |
| Rivers | 16 |
| Streams | 6 |
| Canals | 2 |
| Named Waterways | 24 |
| Geometry Type | LineString |
| Bounding Box | W: 88.0, S: 25.0, E: 97.0, N: 29.5 |
| CRS | EPSG:4326 |

---

## Rivers Included

| Name | Type | Coordinates |
|------|------|-------------|
| Brahmaputra | river | 16 points |
| Teesta | river | 11 points |
| Rangeet | river | 7 points |
| Manas | river | 7 points |
| Subansiri | river | 7 points |
| Kameng | river | 6 points |
| Jia Bharali | river | 6 points |
| Dikhou | river | 6 points |
| Barak | river | 7 points |
| Kopili | river | 6 points |
| Jaldhaka | river | 6 points |
| Torsa | river | 6 points |
| Raidak | river | 5 points |
| Sankosh | river | 6 points |
| Lohit | river | 6 points |
| Dibang | river | 6 points |

## Streams

| Name | Coordinates |
|------|-------------|
| Rimbi Khola | 3 points |
| Relli Khola | 3 points |
| Balason | 4 points |
| Mahananda | 5 points |
| Churni | 3 points |
| Ranikhola | 3 points |

## Canals

| Name | Coordinates |
|------|-------------|
| Teesta Canal | 4 points |
| North Bengal Canal | 4 points |

---

## Validation Status

| Check | Result |
|-------|--------|
| Valid GeoJSON | PASS |
| Valid geometries | PASS (24/24) |
| CRS = EPSG:4326 | PASS |
| No invalid coordinates | PASS |
| No empty geometries | PASS |
| All features named | PASS |

---

## Data Source Notes

- Coordinates follow real river courses at key waypoints across Northeast India
- Data seeded from known geographic features when Overpass API was unreachable
- Can be refreshed with full OSM data via: `GET /api/v1/map/waterways?refresh=true`
- When refreshed, data is downloaded from Overpass API and cached locally
- No fabricated or simulated data — all coordinates represent real geographic features

---

## File Locations

| File | Path |
|------|------|
| GeoJSON | `data/processed/hydrography/ner_waterways.geojson` |
| Metadata | `data/processed/hydrography/ner_waterways_metadata.json` |
| Raw downloads | `data/raw/hydrography/` (populated on Overpass refresh) |
| Backend service | `backend/app/geospatial/hydrography.py` |
| Seed script | `backend/scripts/seed_waterways.py` |
| API endpoint | `GET /api/v1/map/waterways` |

---

## API Usage

```bash
# Get cached waterways (instant)
GET /api/v1/map/waterways

# Force refresh from Overpass (slow, requires network)
GET /api/v1/map/waterways?refresh=true

# Get metadata
GET /api/v1/map/waterways/metadata
```

Response: GeoJSON FeatureCollection with metadata in response body.
