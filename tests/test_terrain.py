"""Automated tests for the NER terrain/DEM pipeline."""

import os
import json
import numpy as np
import rasterio
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "terrain"
RAW_DEM_DIR = PROJECT_ROOT / "data" / "raw" / "terrain" / "dem"
SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"

STATE_BBOXES = {
    'Arunachal Pradesh': (91.5, 26.6, 97.5, 29.5),
    'Assam': (89.7, 24.1, 96.0, 28.0),
    'Meghalaya': (89.8, 25.0, 92.8, 26.2),
    'Nagaland': (93.3, 25.2, 95.3, 27.0),
    'Manipur': (93.0, 23.8, 94.8, 25.7),
    'Mizoram': (92.2, 21.9, 93.4, 24.5),
    'Tripura': (91.1, 22.9, 92.7, 24.5),
    'Sikkim': (88.0, 27.0, 88.9, 28.1),
}


def get_required_tiles():
    required = []
    for lat in range(21, 30):
        ymin, ymax = float(lat), float(lat + 1)
        for lon in range(88, 98):
            xmin, xmax = float(lon), float(lon + 1)
            tile_id = f"NER_DEM_E{lon:03d}_N{lat:02d}"
            for state, (sbx_min, sby_min, sbx_max, sby_max) in STATE_BBOXES.items():
                if not (xmax <= sbx_min or xmin >= sbx_max or ymax <= sby_min or ymin >= sby_max):
                    required.append(tile_id)
                    break
    return required


def tile_filepath(tile_id):
    if tile_id == "NER_DEM_E092_N24":
        return RAW_DEM_DIR / "output_SRTMGL1.tif"
    return RAW_DEM_DIR / f"{tile_id}.tif"


class TestRequiredCellCompleteness:
    def test_required_count_is_57(self):
        required = get_required_tiles()
        assert len(required) == 57

    def test_minimum_valid_tiles(self):
        required = get_required_tiles()
        valid = 0
        for tile_id in required:
            fp = tile_filepath(tile_id)
            if fp.exists():
                try:
                    with rasterio.open(fp) as ds:
                        if ds.count >= 1 and ds.width >= 100:
                            valid += 1
                except Exception:
                    pass
        assert valid >= 24, f"Expected >= 24 valid tiles, got {valid}"


class TestDEMValidation:
    def test_mosaic_exists(self):
        assert (PROCESSED_DIR / "ner_dem.tif").exists()

    def test_mosaic_crs(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert str(ds.crs) == "EPSG:4326"

    def test_mosaic_resolution(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert abs(ds.res[0] - 0.000277778) < 0.0001

    def test_mosaic_nodata(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert ds.nodata == -32768

    def test_mosaic_has_valid_data(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            data = ds.read(1, window=rasterio.windows.Window(0, 0, 100, 100))
            valid = data[data != ds.nodata]
            assert len(valid) > 0

    def test_mosaic_elevation_range(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            data = ds.read(1, window=rasterio.windows.Window(1000, 1000, 1000, 1000))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert valid.min() >= -500
                assert valid.max() <= 9000


class TestMosaic:
    def test_mosaic_single_band(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert ds.count == 1

    def test_mosaic_dtype(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert ds.dtypes[0] == "int16"

    def test_mosaic_bounds_within_study_area(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as ds:
            assert ds.bounds.left >= 87
            assert ds.bounds.right <= 99
            assert ds.bounds.bottom >= 20
            assert ds.bounds.top <= 30


class TestSlope:
    def test_slope_exists(self):
        assert (PROCESSED_DIR / "slope.tif").exists()

    def test_slope_range(self):
        with rasterio.open(PROCESSED_DIR / "slope.tif") as ds:
            data = ds.read(1, window=rasterio.windows.Window(1000, 1000, 500, 500))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert valid.min() >= 0
                assert valid.max() <= 90

    def test_slope_crs_matches_dem(self):
        with rasterio.open(PROCESSED_DIR / "slope.tif") as ds:
            assert str(ds.crs) == "EPSG:4326"

    def test_slope_dimensions_match_dem(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem:
            dem_shape = dem.shape
        with rasterio.open(PROCESSED_DIR / "slope.tif") as slope:
            assert slope.shape == dem_shape


class TestAspect:
    def test_aspect_exists(self):
        assert (PROCESSED_DIR / "aspect.tif").exists()

    def test_aspect_range(self):
        with rasterio.open(PROCESSED_DIR / "aspect.tif") as ds:
            data = ds.read(1, window=rasterio.windows.Window(1000, 1000, 500, 500))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert valid.min() >= 0
                assert valid.max() <= 360

    def test_aspect_crs_matches_dem(self):
        with rasterio.open(PROCESSED_DIR / "aspect.tif") as ds:
            assert str(ds.crs) == "EPSG:4326"

    def test_aspect_dimensions_match_dem(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem:
            dem_shape = dem.shape
        with rasterio.open(PROCESSED_DIR / "aspect.tif") as aspect:
            assert aspect.shape == dem_shape


class TestRuggedness:
    def test_ruggedness_exists(self):
        assert (PROCESSED_DIR / "terrain_ruggedness.tif").exists()

    def test_ruggedness_non_negative(self):
        with rasterio.open(PROCESSED_DIR / "terrain_ruggedness.tif") as ds:
            data = ds.read(1, window=rasterio.windows.Window(1000, 1000, 500, 500))
            valid = data[data != ds.nodata]
            if len(valid) > 0:
                assert valid.min() >= 0

    def test_ruggedness_crs_matches_dem(self):
        with rasterio.open(PROCESSED_DIR / "terrain_ruggedness.tif") as ds:
            assert str(ds.crs) == "EPSG:4326"

    def test_ruggedness_dimensions_match_dem(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem:
            dem_shape = dem.shape
        with rasterio.open(PROCESSED_DIR / "terrain_ruggedness.tif") as tri:
            assert tri.shape == dem_shape


class TestNoDataPropagation:
    def test_nodata_dem_to_slope(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem_ds:
            dem = dem_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        with rasterio.open(PROCESSED_DIR / "slope.tif") as slope_ds:
            slope = slope_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        dem_nodata = dem == -32768
        slope_nodata = slope == -9999.0
        assert np.all(dem_nodata == slope_nodata)

    def test_nodata_dem_to_aspect(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem_ds:
            dem = dem_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        with rasterio.open(PROCESSED_DIR / "aspect.tif") as aspect_ds:
            aspect = aspect_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        dem_nodata = dem == -32768
        aspect_nodata = aspect == -9999.0
        assert np.all(dem_nodata == aspect_nodata)

    def test_nodata_dem_to_tri(self):
        with rasterio.open(PROCESSED_DIR / "ner_dem.tif") as dem_ds:
            dem = dem_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        with rasterio.open(PROCESSED_DIR / "terrain_ruggedness.tif") as tri_ds:
            tri = tri_ds.read(1, window=rasterio.windows.Window(0, 0, 200, 200))
        dem_nodata = dem == -32768
        tri_nodata = tri == -9999.0
        assert np.all(dem_nodata == tri_nodata)


class TestManifest:
    def test_manifest_exists(self):
        assert (SCHEMAS_DIR / "terrain_dataset_manifest.json").exists()

    def test_manifest_valid_json(self):
        with open(SCHEMAS_DIR / "terrain_dataset_manifest.json") as f:
            data = json.load(f)
        assert data["source"] == "SRTM GL1"
        assert data["resolution_m"] == 30
        assert data["required_tile_count"] == 57
        assert data["crs"] == "EPSG:4326"

    def test_manifest_paths_exist(self):
        with open(SCHEMAS_DIR / "terrain_dataset_manifest.json") as f:
            data = json.load(f)
        assert (PROJECT_ROOT / data["final_dem_path"]).exists()
        for key, path in data["derivative_paths"].items():
            assert (PROJECT_ROOT / path).exists(), f"{key} at {path} missing"
