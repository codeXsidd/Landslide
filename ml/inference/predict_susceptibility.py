"""
NER-LDI Terrain Susceptibility Inference
Predict landslide susceptibility for a given latitude/longitude.
"""

import json
import numpy as np
import rasterio
import joblib
from pathlib import Path

_MODEL_DIR = Path(__file__).parent.parent / "artifacts"
_TERRAIN_DIR = Path(__file__).parent.parent.parent / "data" / "processed" / "terrain"

_FEATURES = ["elevation", "slope", "aspect", "terrain_ruggedness"]
_RASTER_NAMES = {
    "elevation": "elevation.tif",
    "slope": "slope.tif",
    "aspect": "aspect.tif",
    "terrain_ruggedness": "terrain_ruggedness.tif",
}

_model = None
_metadata = None
_rasters = {}


def _load_model():
    global _model, _metadata
    if _model is None:
        _model = joblib.load(_MODEL_DIR / "terrain_susceptibility_model.joblib")
        with open(_MODEL_DIR / "terrain_susceptibility_metadata.json") as f:
            _metadata = json.load(f)
    return _model, _metadata


def _get_raster(name):
    if name not in _rasters:
        path = _TERRAIN_DIR / _RASTER_NAMES[name]
        if not path.exists():
            raise FileNotFoundError(f"Raster not found: {path.name}")
        _rasters[name] = rasterio.open(path)
    return _rasters[name]


def _extract_value(ds, lon, lat):
    try:
        row, col = ds.index(lon, lat)
        if 0 <= row < ds.height and 0 <= col < ds.width:
            val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
            if val == ds.nodata:
                return None
            return float(val)
    except Exception:
        pass
    return None


def predict_susceptibility(latitude: float, longitude: float) -> dict:
    """
    Predict terrain-based landslide susceptibility for a location.

    Args:
        latitude: WGS84 latitude in degrees
        longitude: WGS84 longitude in degrees

    Returns:
        dict with susceptibility_score, susceptibility_level, model_version, features
    """
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {
            "susceptibility_score": None,
            "susceptibility_level": "INVALID_COORDINATES",
            "model_version": None,
            "features": {},
            "error": "Coordinates out of valid range"
        }

    model, metadata = _load_model()

    features = {}
    for feat_name in _FEATURES:
        ds = _get_raster(feat_name)
        val = _extract_value(ds, longitude, latitude)
        features[feat_name] = val

    if any(v is None for v in features.values()):
        missing = [k for k, v in features.items() if v is None]
        return {
            "susceptibility_score": None,
            "susceptibility_level": "NO_DATA",
            "model_version": metadata["model_version"],
            "features": features,
            "error": f"Missing terrain data for: {missing}"
        }

    X = np.array([[features[f] for f in _FEATURES]])
    prob = float(model.predict_proba(X)[0, 1])

    if prob >= 0.75:
        level = "HIGH"
    elif prob >= 0.5:
        level = "MODERATE"
    elif prob >= 0.25:
        level = "LOW"
    else:
        level = "VERY_LOW"

    return {
        "susceptibility_score": round(prob, 4),
        "susceptibility_level": level,
        "model_version": metadata["model_version"],
        "features": features,
    }


def close():
    """Close open raster file handles."""
    for ds in _rasters.values():
        ds.close()
    _rasters.clear()


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        lat = float(sys.argv[1])
        lon = float(sys.argv[2])
    else:
        lat, lon = 25.5, 93.0
        print(f"Usage: python predict_susceptibility.py <lat> <lon>")
        print(f"Using default: {lat}, {lon}\n")

    result = predict_susceptibility(lat, lon)
    print(json.dumps(result, indent=2))
    close()
