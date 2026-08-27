"""
NER-SAGE — Feature Engineering Pipeline
Prepares raw location, terrain, and weather data for XGBoost inference.
"""

from typing import Any

import pandas as pd


def extract_features(location: dict[str, Any], weather: dict[str, Any]) -> pd.DataFrame:
    """
    Transforms raw dictionaries into a 1-row DataFrame of features.
    In production, terrain/geology features are pulled from the GIS store.
    Here we extract from properties or mock them for the demo.
    """
    props = location.get("properties", {})

    # 1. Topographic Features
    slope_deg = props.get("slope_deg", 35.0)  # default steep slope
    elevation_m = props.get("elevation_m", 1200.0)
    aspect_deg = props.get("aspect_deg", 180.0)

    # 2. Weather Triggers
    rainfall_24h = weather.get("rainfall_24h_mm", 0.0)
    rainfall_72h = weather.get("rainfall_72h_mm", 0.0)

    # 3. Geological/Vulnerability
    soil_type_idx = props.get("soil_type_idx", 2.0)  # Categorical index
    distance_to_fault_km = props.get("distance_to_fault_km", 5.5)

    # 4. Computed Indexes
    # API (Antecedent Precipitation Index) approximation
    api_score = rainfall_24h + (0.5 * rainfall_72h)

    features = {
        "slope_deg": slope_deg,
        "elevation_m": elevation_m,
        "aspect_deg": aspect_deg,
        "rainfall_24h": rainfall_24h,
        "rainfall_72h": rainfall_72h,
        "api_score": api_score,
        "soil_type_idx": soil_type_idx,
        "distance_to_fault_km": distance_to_fault_km,
    }

    return pd.DataFrame([features])
