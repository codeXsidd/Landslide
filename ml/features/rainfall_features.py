"""
NER-LDI Rainfall Feature Engineering Module
Computes rolling rainfall aggregates and anomaly indicators.
Only creates features when source data exists. Never fabricates values.
"""
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAINFALL_PATH = PROJECT_ROOT / "data" / "processed" / "rainfall" / "rainfall_daily.parquet"

FEATURE_WINDOWS = {
    "rainfall_1d": 1,
    "rainfall_3d": 3,
    "rainfall_7d": 7,
    "rainfall_15d": 15,
    "rainfall_30d": 30,
}


def load_rainfall():
    if not RAINFALL_PATH.exists():
        return None
    return pd.read_parquet(RAINFALL_PATH)


def get_rainfall_at_point(df, lat, lon, date, tolerance_deg=0.1):
    """Get rainfall time series for nearest grid cell."""
    dist = np.sqrt((df.latitude - lat)**2 + (df.longitude - lon)**2)
    nearest_idx = dist.groupby(df.date).idxmin()
    mask = dist <= tolerance_deg
    if not mask.any():
        return None
    cell_lat = df.loc[mask.idxmax(), "latitude"]
    cell_lon = df.loc[mask.idxmax(), "longitude"]
    cell_data = df[(df.latitude == cell_lat) & (df.longitude == cell_lon)].sort_values("date")
    return cell_data


def compute_rainfall_features(lat, lon, target_date, df=None):
    """Compute rainfall features for a point and date. Returns dict with available features only."""
    if df is None:
        df = load_rainfall()
    if df is None:
        return {"_status": "NO_RAINFALL_DATA"}

    dist = np.sqrt((df.latitude - lat)**2 + (df.longitude - lon)**2)
    min_dist = dist.min()
    if min_dist > 0.15:
        return {"_status": "NO_NEARBY_CELL", "_min_distance_deg": float(min_dist)}

    nearest_mask = dist == min_dist
    sample = df[nearest_mask].iloc[0]
    cell_lat, cell_lon = sample.latitude, sample.longitude
    cell_data = df[(df.latitude == cell_lat) & (df.longitude == cell_lon)].sort_values("date").copy()

    if isinstance(target_date, str):
        target_date = pd.Timestamp(target_date)
    target_date = pd.Timestamp(target_date)

    features = {"_status": "OK", "_cell_lat": float(cell_lat), "_cell_lon": float(cell_lon)}
    available_dates = cell_data.date.max()

    for feat_name, window in FEATURE_WINDOWS.items():
        end_date = min(target_date, available_dates)
        start_date = end_date - pd.Timedelta(days=window - 1)
        window_data = cell_data[(cell_data.date >= start_date) & (cell_data.date <= end_date)]
        if len(window_data) > 0:
            features[feat_name] = float(window_data.precipitation_mm_day.sum())
        else:
            features[feat_name] = None

    # Rolling max
    if len(cell_data) >= 3:
        features["rolling_max_3d"] = float(cell_data.precipitation_mm_day.rolling(3, min_periods=1).max().iloc[-1])
    if len(cell_data) >= 7:
        features["rolling_max_7d"] = float(cell_data.precipitation_mm_day.rolling(7, min_periods=1).max().iloc[-1])

    # Antecedent Rainfall Index (exponential decay, k=0.85)
    k = 0.85
    precip = cell_data.precipitation_mm_day.values
    if len(precip) > 1:
        api = 0.0
        for p in precip[:-1]:
            api = k * api + p
        features["antecedent_rainfall_index"] = float(api)

    # Anomaly: ratio to mean
    mean_precip = cell_data.precipitation_mm_day.mean()
    if mean_precip > 0 and features.get("rainfall_1d") is not None:
        features["rainfall_anomaly"] = float(features["rainfall_1d"] / mean_precip)

    # Forecast placeholders (not available without forecast data)
    features["forecast_rainfall_6h"] = None
    features["forecast_rainfall_24h"] = None
    features["forecast_rainfall_72h"] = None

    return features


def compute_batch_rainfall_features(locations_df, date_col="date"):
    """Compute rainfall features for a DataFrame of locations with dates."""
    rainfall_df = load_rainfall()
    if rainfall_df is None:
        return pd.DataFrame()

    results = []
    for _, row in locations_df.iterrows():
        feats = compute_rainfall_features(row.latitude, row.longitude, row[date_col], rainfall_df)
        feats_clean = {k: v for k, v in feats.items() if not k.startswith("_")}
        results.append(feats_clean)

    return pd.DataFrame(results)
