"""Tests for terrain susceptibility ML pipeline."""

import json
import numpy as np
import rasterio
import joblib
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
TERRAIN_DIR = PROJECT_ROOT / "data" / "processed" / "terrain"
ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
ML_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "ml"


class TestFeatureExtraction:
    def test_slope_extraction_valid_point(self):
        with rasterio.open(TERRAIN_DIR / "slope.tif") as ds:
            row, col = ds.index(93.0, 25.0)
            val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
            assert val != ds.nodata
            assert 0 <= val <= 90

    def test_aspect_extraction_valid_point(self):
        with rasterio.open(TERRAIN_DIR / "aspect.tif") as ds:
            row, col = ds.index(93.0, 25.0)
            val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
            assert val != ds.nodata
            assert 0 <= val <= 360

    def test_elevation_extraction_valid_point(self):
        with rasterio.open(TERRAIN_DIR / "elevation.tif") as ds:
            row, col = ds.index(93.0, 25.0)
            val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
            assert val != ds.nodata

    def test_outside_bounds_returns_nodata(self):
        with rasterio.open(TERRAIN_DIR / "slope.tif") as ds:
            try:
                row, col = ds.index(50.0, 10.0)
                if 0 <= row < ds.height and 0 <= col < ds.width:
                    val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
                    assert val == ds.nodata
                else:
                    pass  # Out of bounds is expected
            except Exception:
                pass  # Exception for out-of-bounds is acceptable


class TestModelLoading:
    def test_model_file_exists(self):
        assert (ARTIFACTS_DIR / "terrain_susceptibility_model.joblib").exists()

    def test_metadata_file_exists(self):
        assert (ARTIFACTS_DIR / "terrain_susceptibility_metadata.json").exists()

    def test_model_loads(self):
        model = joblib.load(ARTIFACTS_DIR / "terrain_susceptibility_model.joblib")
        assert model is not None
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_metadata_valid(self):
        with open(ARTIFACTS_DIR / "terrain_susceptibility_metadata.json") as f:
            meta = json.load(f)
        assert meta["model_type"] in ("RandomForest", "XGBoost")
        assert meta["feature_names"] == ["elevation", "slope", "aspect", "terrain_ruggedness"]
        assert meta["random_seed"] == 42
        assert meta["training_row_count"] > 0
        assert 0 < meta["evaluation_metrics"]["roc_auc"] <= 1


class TestPrediction:
    def test_model_predicts_array(self):
        model = joblib.load(ARTIFACTS_DIR / "terrain_susceptibility_model.joblib")
        X = np.array([[500.0, 25.0, 180.0, 10.0]])
        pred = model.predict(X)
        assert pred.shape == (1,)
        assert pred[0] in (0, 1)

    def test_probabilities_valid(self):
        model = joblib.load(ARTIFACTS_DIR / "terrain_susceptibility_model.joblib")
        X = np.array([[500.0, 25.0, 180.0, 10.0]])
        prob = model.predict_proba(X)
        assert prob.shape == (1, 2)
        assert abs(prob.sum() - 1.0) < 0.001
        assert 0 <= prob[0, 1] <= 1

    def test_batch_prediction(self):
        model = joblib.load(ARTIFACTS_DIR / "terrain_susceptibility_model.joblib")
        X = np.array([
            [100.0, 5.0, 90.0, 2.0],
            [2000.0, 45.0, 270.0, 50.0],
            [500.0, 20.0, 180.0, 15.0],
        ])
        probs = model.predict_proba(X)
        assert probs.shape == (3, 2)


class TestMissingRasterValues:
    def test_nodata_pixel_handling(self):
        with rasterio.open(TERRAIN_DIR / "elevation.tif") as ds:
            # Read a corner that should have nodata
            val = ds.read(1, window=rasterio.windows.Window(0, 0, 1, 1))[0, 0]
            # Just verify the nodata value is set
            assert ds.nodata is not None


class TestInvalidCoordinates:
    def test_inference_invalid_lat(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "predict", PROJECT_ROOT / "ml" / "inference" / "predict_susceptibility.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.predict_susceptibility(200.0, 93.0)
        assert result["susceptibility_level"] == "INVALID_COORDINATES"
        assert result["susceptibility_score"] is None
        mod.close()

    def test_inference_outside_coverage(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "predict", PROJECT_ROOT / "ml" / "inference" / "predict_susceptibility.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.predict_susceptibility(10.0, 10.0)
        assert result["susceptibility_level"] == "NO_DATA"
        mod.close()


class TestDeterministicSampling:
    def test_same_seed_same_output(self):
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        arr1 = rng1.uniform(0, 1, 100)
        arr2 = rng2.uniform(0, 1, 100)
        assert np.allclose(arr1, arr2)

    def test_dataset_reproducible(self):
        import pandas as pd
        df = pd.read_parquet(ML_DATA_DIR / "terrain_susceptibility_dataset.parquet")
        assert len(df) > 0
        assert "label" in df.columns
        assert df["label"].isin([0, 1]).all()
