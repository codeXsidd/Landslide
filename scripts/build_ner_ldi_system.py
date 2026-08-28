"""
NER-LDI Complete Decision Intelligence System Builder
Builds all phases of the system from existing validated components.
"""
import os, sys, json, datetime, shutil
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT = Path(__file__).parent.parent
SEED = 42
np.random.seed(SEED)
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

# ==============================================================
# PHASE 1: DATA SCHEMAS
# ==============================================================
def phase1_schemas():
    print("PHASE 1: Data Schemas")
    schemas_dir = PROJECT / "data" / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    schemas = {
        "risk_state.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Risk State",
            "type": "object",
            "required": ["location", "risk_score", "risk_level", "confidence", "uncertainty", "model_version", "timestamp"],
            "properties": {
                "location": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}, "location_id": {"type": "string"}}},
                "risk_score": {"type": "number", "minimum": 0, "maximum": 1},
                "risk_level": {"type": "string", "enum": ["VERY_LOW", "LOW", "MODERATE", "HIGH", "CRITICAL"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "uncertainty": {"type": "object", "properties": {"level": {"type": "string"}, "reasons": {"type": "array", "items": {"type": "string"}}, "data_completeness": {"type": "number"}}},
                "evidence_status": {"type": "string", "enum": ["KNOWN", "UNKNOWN", "UNCERTAIN", "CONFLICTING", "STALE"]},
                "major_factors": {"type": "array", "items": {"type": "object"}},
                "terrain_features": {"type": "object"},
                "rainfall_features": {"type": "object"},
                "road_blockage_probability": {"type": "number"},
                "village_isolation_probability": {"type": "number"},
                "population_exposed": {"type": "integer"},
                "silent_zone_status": {"type": "boolean"},
                "priority_score": {"type": "number"},
                "recommended_next_evidence": {"type": "object"},
                "recommended_actions": {"type": "array"},
                "human_approval_required": {"type": "boolean"},
                "model_version": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"}
            }
        },
        "evidence.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Evidence Item",
            "type": "object",
            "required": ["evidence_id", "source", "timestamp", "location", "evidence_type", "freshness", "reliability", "is_simulated"],
            "properties": {
                "evidence_id": {"type": "string"},
                "source": {"type": "string"},
                "source_type": {"type": "string", "enum": ["satellite", "rainfall_sensor", "citizen_report", "field_inspection", "official_report", "model_output", "historical"]},
                "timestamp": {"type": "string", "format": "date-time"},
                "location": {"type": "object", "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}}},
                "evidence_type": {"type": "string"},
                "value": {},
                "freshness": {"type": "string", "enum": ["FRESH", "RECENT", "STALE", "EXPIRED"]},
                "reliability": {"type": "number", "minimum": 0, "maximum": 1},
                "is_simulated": {"type": "boolean"},
                "provenance": {"type": "object", "properties": {"collected_by": {"type": "string"}, "method": {"type": "string"}, "instrument": {"type": "string"}}}
            }
        },
        "impact_prediction.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Impact Prediction",
            "type": "object",
            "required": ["location", "road_blockage_probability", "village_isolation_probability", "population_exposed"],
            "properties": {
                "location": {"type": "object"},
                "road_blockage_probability": {"type": "number"},
                "road_risk_level": {"type": "string"},
                "village_isolation_probability": {"type": "number"},
                "population_exposed": {"type": "integer"},
                "hospital_access_degraded": {"type": "boolean"},
                "alternative_routes": {"type": "array"},
                "cascade_level": {"type": "string", "enum": ["NONE", "MINOR", "MODERATE", "SEVERE", "CATASTROPHIC"]},
                "exposure_score": {"type": "number"},
                "assets_affected": {"type": "array"},
                "critical_assets": {"type": "array"}
            }
        },
        "decision.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Decision Record",
            "type": "object",
            "required": ["decision_id", "location", "risk_state", "recommended_actions", "human_approval_required", "timestamp"],
            "properties": {
                "decision_id": {"type": "string"},
                "location": {"type": "object"},
                "risk_state": {"type": "object"},
                "recommended_actions": {"type": "array"},
                "human_approval_required": {"type": "boolean"},
                "human_decision": {"type": "object", "properties": {"status": {"type": "string", "enum": ["PENDING", "APPROVED", "REJECTED", "MODIFIED"]}, "decided_by": {"type": "string"}, "reason": {"type": "string"}, "timestamp": {"type": "string"}}},
                "outcome": {"type": "object", "properties": {"actual_event": {"type": "boolean"}, "harm_realized": {"type": "number"}, "feedback_category": {"type": "string"}}},
                "audit_trail": {"type": "array"},
                "timestamp": {"type": "string", "format": "date-time"}
            }
        },
        "simulation.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Simulation Run",
            "type": "object",
            "required": ["simulation_id", "scenario_type", "baseline_state", "simulated_state", "timestamp"],
            "properties": {
                "simulation_id": {"type": "string"},
                "scenario_type": {"type": "string"},
                "input_changes": {"type": "object"},
                "baseline_state": {"type": "object"},
                "simulated_state": {"type": "object"},
                "delta": {"type": "object"},
                "timestamp": {"type": "string", "format": "date-time"},
                "is_simulated": {"type": "boolean", "const": True}
            }
        },
        "human_feedback.schema.json": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "NER-LDI Human Feedback",
            "type": "object",
            "required": ["feedback_id", "decision_id", "prediction_was", "human_action", "timestamp"],
            "properties": {
                "feedback_id": {"type": "string"},
                "decision_id": {"type": "string"},
                "prediction_was": {"type": "object"},
                "human_action": {"type": "string", "enum": ["APPROVED", "REJECTED", "MODIFIED", "ESCALATED"]},
                "reason": {"type": "string"},
                "outcome_observed": {"type": "object"},
                "feedback_category": {"type": "string", "enum": ["CORRECT", "OVER_CONSERVATIVE", "UNDER_ESTIMATED", "INSUFFICIENT_EVIDENCE", "WRONG_PRIORITY"]},
                "timestamp": {"type": "string", "format": "date-time"}
            }
        }
    }

    for name, schema in schemas.items():
        with open(schemas_dir / name, "w") as f:
            json.dump(schema, f, indent=2)
    print(f"  Created {len(schemas)} schemas")


# ==============================================================
# PHASE 2: RAINFALL FEATURES
# ==============================================================
def phase2_rainfall_features():
    print("\nPHASE 2: Rainfall Feature Engineering")
    features_dir = PROJECT / "ml" / "features"
    features_dir.mkdir(parents=True, exist_ok=True)

    # Write the rainfall features module
    module_code = '''"""
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
'''
    with open(features_dir / "rainfall_features.py", "w") as f:
        f.write(module_code)

    # Also ensure __init__.py exists
    (features_dir / "__init__.py").touch()

    # Create rainfall features parquet from available data
    ml_dir = PROJECT / "data" / "processed" / "ml"
    ml_dir.mkdir(parents=True, exist_ok=True)

    df_rain = pd.read_parquet(PROJECT / "data" / "processed" / "rainfall" / "rainfall_daily.parquet")
    # Create grid-level features for last available date
    last_date = df_rain.date.max()
    grid_points = df_rain[df_rain.date == last_date][["latitude", "longitude"]].drop_duplicates()

    sys.path.insert(0, str(features_dir.parent))
    # Save metadata about what we have
    meta = {
        "source": "NASA GPM IMERG Final V07B",
        "date_coverage": f"{df_rain.date.min().isoformat()} to {df_rain.date.max().isoformat()}",
        "days_available": int(df_rain.date.nunique()),
        "spatial_resolution_deg": 0.1,
        "units": "mm/day",
        "limitations": [
            "Only 7 days of test data available (2024-06-01 to 2024-06-07)",
            "Insufficient for multi-year antecedent rainfall computation",
            "Dynamic model training marked INCOMPLETE",
            "Features computed from available data only"
        ],
        "features_supported": list(FEATURE_WINDOWS := {"rainfall_1d": 1, "rainfall_3d": 3, "rainfall_7d": 7}),
        "features_unavailable_due_to_insufficient_data": ["rainfall_15d", "rainfall_30d", "forecast_rainfall_6h", "forecast_rainfall_24h", "forecast_rainfall_72h"],
        "generated": NOW
    }
    with open(ml_dir / "rainfall_features_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"  Rainfall features module: ml/features/rainfall_features.py")
    print(f"  Metadata: data/processed/ml/rainfall_features_metadata.json")
    print(f"  Available coverage: 7 days only - dynamic training INCOMPLETE")


# ==============================================================
# PHASE 3: SPATIAL-TEMPORAL FEATURE JOIN
# ==============================================================
def phase3_feature_join():
    print("\nPHASE 3: Spatial-Temporal Feature Join")
    sys.path.insert(0, str(PROJECT / "ml" / "features"))

    from rainfall_features import compute_rainfall_features, load_rainfall

    # Load landslide data
    ls_df = pd.read_csv(PROJECT / "data" / "processed" / "landslides" / "gsi_landslide_inventory_ner.csv")
    rain_df = load_rainfall()

    # Load terrain features from existing training dataset
    terrain_ds = pd.read_parquet(PROJECT / "data" / "processed" / "ml" / "terrain_susceptibility_dataset.parquet")
    positive_terrain = terrain_ds[terrain_ds.label == 1][["latitude", "longitude", "elevation", "slope", "aspect", "terrain_ruggedness"]].copy()

    # Assign a dummy date within rainfall range for feature computation
    rain_date = "2024-06-05"  # Mid-point of available rainfall

    records = []
    for _, row in positive_terrain.iterrows():
        rf = compute_rainfall_features(row.latitude, row.longitude, rain_date, rain_df)
        rec = {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "label": 1,
            "elevation": row.elevation,
            "slope": row.slope,
            "aspect": row.aspect,
            "terrain_ruggedness": row.terrain_ruggedness,
            "rainfall_1d": rf.get("rainfall_1d"),
            "rainfall_3d": rf.get("rainfall_3d"),
            "rainfall_7d": rf.get("rainfall_7d"),
            "rolling_max_3d": rf.get("rolling_max_3d"),
            "rolling_max_7d": rf.get("rolling_max_7d"),
            "antecedent_rainfall_index": rf.get("antecedent_rainfall_index"),
            "rainfall_anomaly": rf.get("rainfall_anomaly"),
        }
        records.append(rec)

    # Also add negative samples with rainfall
    negative_terrain = terrain_ds[terrain_ds.label == 0][["latitude", "longitude", "elevation", "slope", "aspect", "terrain_ruggedness"]].copy()
    for _, row in negative_terrain.iterrows():
        rf = compute_rainfall_features(row.latitude, row.longitude, rain_date, rain_df)
        rec = {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "label": 0,
            "elevation": row.elevation,
            "slope": row.slope,
            "aspect": row.aspect,
            "terrain_ruggedness": row.terrain_ruggedness,
            "rainfall_1d": rf.get("rainfall_1d"),
            "rainfall_3d": rf.get("rainfall_3d"),
            "rainfall_7d": rf.get("rainfall_7d"),
            "rolling_max_3d": rf.get("rolling_max_3d"),
            "rolling_max_7d": rf.get("rolling_max_7d"),
            "antecedent_rainfall_index": rf.get("antecedent_rainfall_index"),
            "rainfall_anomaly": rf.get("rainfall_anomaly"),
        }
        records.append(rec)

    dynamic_df = pd.DataFrame(records)
    out_path = PROJECT / "data" / "processed" / "ml" / "ner_dynamic_feature_dataset.parquet"
    dynamic_df.to_parquet(out_path, index=False)

    rainfall_cols = ["rainfall_1d", "rainfall_3d", "rainfall_7d", "rolling_max_3d", "rolling_max_7d", "antecedent_rainfall_index", "rainfall_anomaly"]
    missing = dynamic_df[rainfall_cols].isna().sum()
    print(f"  Dynamic dataset: {len(dynamic_df)} rows ({(dynamic_df.label==1).sum()} pos, {(dynamic_df.label==0).sum()} neg)")
    print(f"  Rainfall missingness:\n{missing.to_string()}")
    print(f"  Saved: {out_path.relative_to(PROJECT)}")
    return dynamic_df


# ==============================================================
# PHASE 4: DYNAMIC RISK MODEL
# ==============================================================
def phase4_dynamic_model(dynamic_df):
    print("\nPHASE 4: Dynamic Risk Model")
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, brier_score_loss
    import xgboost as xgb
    import joblib

    terrain_features = ["elevation", "slope", "aspect", "terrain_ruggedness"]
    rainfall_features = ["rainfall_1d", "rainfall_3d", "rainfall_7d", "antecedent_rainfall_index"]

    # Use only rows with complete rainfall
    complete = dynamic_df.dropna(subset=rainfall_features).copy()
    print(f"  Complete rows (terrain+rainfall): {len(complete)}/{len(dynamic_df)}")

    if len(complete) < 100:
        print("  INSUFFICIENT DATA - marking dynamic model INCOMPLETE")
        return None, "INCOMPLETE"

    all_features = terrain_features + rainfall_features
    X = complete[all_features].values
    y = complete["label"].values

    # Spatial block split
    grid_size = 0.5
    complete["block"] = (complete.longitude / grid_size).astype(int).astype(str) + "_" + (complete.latitude / grid_size).astype(int).astype(str)
    blocks = complete["block"].unique()
    rng = np.random.default_rng(SEED)
    shuffled = rng.permutation(blocks)
    n_test = max(1, int(len(blocks) * 0.25))
    test_blocks = set(shuffled[:n_test])

    train_mask = ~complete["block"].isin(test_blocks)
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[~train_mask], y[~train_mask]

    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")

    # Train models
    n_pos = y_train.sum()
    n_neg = (y_train == 0).sum()
    spw = n_neg / max(n_pos, 1)

    rf = RandomForestClassifier(n_estimators=200, max_depth=12, class_weight="balanced", random_state=SEED, n_jobs=-1)
    rf.fit(X_train, y_train)

    xgb_m = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, scale_pos_weight=spw, random_state=SEED, eval_metric="logloss", n_jobs=-1)
    xgb_m.fit(X_train, y_train)

    # Evaluate
    results = {}
    for name, model in [("RF", rf), ("XGB", xgb_m)]:
        prob = model.predict_proba(X_test)[:, 1]
        pred = model.predict(X_test)
        results[name] = {
            "roc_auc": roc_auc_score(y_test, prob),
            "pr_auc": average_precision_score(y_test, prob),
            "f1": f1_score(y_test, pred),
            "brier": brier_score_loss(y_test, prob),
        }
        print(f"  {name}: ROC-AUC={results[name]['roc_auc']:.4f} PR-AUC={results[name]['pr_auc']:.4f} F1={results[name]['f1']:.4f}")

    # Select best
    best_name = max(results, key=lambda k: results[k]["pr_auc"])
    best_model = rf if best_name == "RF" else xgb_m
    best_metrics = results[best_name]

    # Save
    artifacts_dir = PROJECT / "ml" / "artifacts"
    joblib.dump(best_model, artifacts_dir / "ner_dynamic_risk_model.joblib")

    metadata = {
        "model_type": "RandomForest" if best_name == "RF" else "XGBoost",
        "model_version": "2.0.0-dynamic-partial",
        "features": all_features,
        "terrain_features": terrain_features,
        "rainfall_features": rainfall_features,
        "training_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "positive_count": int(y_train.sum()),
        "negative_count": int((y_train == 0).sum()),
        "metrics": {k: float(v) for k, v in best_metrics.items()},
        "split_method": "spatial_block_0.5deg",
        "random_seed": SEED,
        "training_timestamp": NOW,
        "rainfall_coverage": "7 days only (2024-06-01 to 2024-06-07)",
        "terrain_coverage": "PARTIAL (24/57 cells)",
        "status": "INCOMPLETE - insufficient historical rainfall for production use",
        "limitations": [
            "Only 7 days of rainfall data used for features",
            "Temporal rainfall features lack multi-year context",
            "Model should be retrained when full IMERG archive is available",
            "Not suitable for operational deployment without complete rainfall history"
        ]
    }
    with open(artifacts_dir / "ner_dynamic_risk_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Best model: {best_name} saved")
    print(f"  STATUS: INCOMPLETE (7-day rainfall only)")
    return best_model, best_metrics


# ==============================================================
# PHASE 5: CALIBRATION
# ==============================================================
def phase5_calibration():
    print("\nPHASE 5: Probability Calibration")
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import brier_score_loss
    import joblib

    artifacts_dir = PROJECT / "ml" / "artifacts"
    model = joblib.load(artifacts_dir / "ner_dynamic_risk_model.joblib")

    # Load training data for calibration
    dynamic_df = pd.read_parquet(PROJECT / "data" / "processed" / "ml" / "ner_dynamic_feature_dataset.parquet")
    terrain_features = ["elevation", "slope", "aspect", "terrain_ruggedness"]
    rainfall_features = ["rainfall_1d", "rainfall_3d", "rainfall_7d", "antecedent_rainfall_index"]
    all_features = terrain_features + rainfall_features

    complete = dynamic_df.dropna(subset=rainfall_features)
    X = complete[all_features].values
    y = complete["label"].values

    # Use isotonic calibration with CV
    cal_model = CalibratedClassifierCV(model, method="isotonic", cv=3)
    cal_model.fit(X, y)

    # Compare
    uncal_prob = model.predict_proba(X)[:, 1]
    cal_prob = cal_model.predict_proba(X)[:, 1]

    brier_uncal = brier_score_loss(y, uncal_prob)
    brier_cal = brier_score_loss(y, cal_prob)

    joblib.dump(cal_model, artifacts_dir / "risk_calibrator.joblib")

    print(f"  Brier (uncalibrated): {brier_uncal:.4f}")
    print(f"  Brier (calibrated):   {brier_cal:.4f}")
    print(f"  Improvement: {(brier_uncal - brier_cal):.4f}")
    return brier_uncal, brier_cal


# ==============================================================
# PHASES 6-14: BACKEND ENGINES
# ==============================================================
def phase6_to_14_engines():
    print("\nPHASES 6-14: Backend Engines")

    evidence_dir = PROJECT / "backend" / "app" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Phase 6: Uncertainty Engine
    write_file(evidence_dir / "uncertainty_engine.py", '''"""NER-LDI Uncertainty Engine - separates risk, confidence, and uncertainty."""
import numpy as np
from typing import Optional


def compute_uncertainty(risk_score: float, features: dict, evidence_items: list,
                       model_version: str = "2.0.0-dynamic-partial") -> dict:
    """Compute uncertainty profile distinct from risk score."""
    reasons = []
    data_completeness = 1.0

    # Model ensemble disagreement (simulated with variance proxy)
    model_confidence = 0.85 if "dynamic" in model_version else 0.75
    if "partial" in model_version:
        model_confidence -= 0.1
        reasons.append("Model trained on partial terrain coverage")

    # Missing features penalty
    missing = [k for k, v in features.items() if v is None]
    missing_penalty = len(missing) * 0.08
    data_completeness -= len(missing) * 0.1
    if missing:
        reasons.append(f"Missing features: {missing}")

    # Evidence freshness
    fresh_count = sum(1 for e in evidence_items if e.get("freshness") == "FRESH")
    stale_count = sum(1 for e in evidence_items if e.get("freshness") in ("STALE", "EXPIRED"))
    freshness_factor = max(0.5, 1.0 - stale_count * 0.1)
    if stale_count > 0:
        reasons.append(f"{stale_count} stale/expired evidence sources")

    # Source reliability
    reliabilities = [e.get("reliability", 0.5) for e in evidence_items]
    avg_reliability = np.mean(reliabilities) if reliabilities else 0.5

    # Conflict detection
    conflict_penalty = 0.0
    sources_by_type = {}
    for e in evidence_items:
        t = e.get("evidence_type", "unknown")
        sources_by_type.setdefault(t, []).append(e)
    for t, items in sources_by_type.items():
        if len(items) > 1:
            values = [i.get("value") for i in items if i.get("value") is not None]
            if len(set(str(v) for v in values)) > 1:
                conflict_penalty += 0.1
                reasons.append(f"Conflicting {t} evidence")

    # Out-of-distribution check
    if features.get("elevation") is not None and features["elevation"] > 4000:
        reasons.append("Elevation beyond typical training range")
        model_confidence -= 0.05

    # Compute final confidence
    confidence = max(0.0, min(1.0,
        model_confidence * freshness_factor * avg_reliability - missing_penalty - conflict_penalty
    ))

    uncertainty_level = "LOW" if confidence > 0.75 else "MODERATE" if confidence > 0.5 else "HIGH" if confidence > 0.25 else "VERY_HIGH"

    return {
        "risk_score": risk_score,
        "confidence": round(confidence, 4),
        "uncertainty_level": uncertainty_level,
        "uncertainty_reasons": reasons,
        "data_completeness": round(max(0, data_completeness), 2),
        "model_version": model_version,
        "freshness_factor": round(freshness_factor, 3),
        "source_reliability": round(avg_reliability, 3),
        "conflict_penalty": round(conflict_penalty, 3),
    }
''')

    # Phase 7: Evidence Fusion
    write_file(evidence_dir / "evidence_fusion.py", '''"""NER-LDI Evidence Fusion - combines multiple evidence sources with provenance."""
from typing import List, Dict
from datetime import datetime, timezone, timedelta


SOURCE_RELIABILITY = {
    "satellite_sentinel": 0.92,
    "rainfall_sensor": 0.88,
    "official_report": 0.90,
    "field_inspection": 0.95,
    "citizen_report_verified": 0.80,
    "citizen_report_unverified": 0.45,
    "model_output": 0.75,
    "historical": 0.70,
    "synthetic": 0.30,
}

FRESHNESS_THRESHOLDS = {
    "satellite": timedelta(hours=48),
    "rainfall_sensor": timedelta(hours=6),
    "field_inspection": timedelta(hours=24),
    "citizen_report": timedelta(hours=12),
    "official_report": timedelta(hours=72),
}


def classify_freshness(source_type: str, timestamp: str) -> str:
    if not timestamp:
        return "EXPIRED"
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "EXPIRED"
    age = datetime.now(timezone.utc) - ts
    threshold = FRESHNESS_THRESHOLDS.get(source_type, timedelta(hours=24))
    if age < threshold:
        return "FRESH"
    elif age < threshold * 2:
        return "RECENT"
    elif age < threshold * 5:
        return "STALE"
    return "EXPIRED"


def fuse_evidence(evidence_items: List[Dict]) -> Dict:
    """Fuse multiple evidence sources into a unified assessment."""
    if not evidence_items:
        return {"status": "UNKNOWN", "known": [], "unknown": [], "uncertain": [], "conflicting": [], "stale": []}

    known, unknown, uncertain, conflicting, stale = [], [], [], [], []
    expected_types = {"rainfall", "terrain", "satellite", "historical", "road_status", "forecast"}
    present_types = set()

    for item in evidence_items:
        etype = item.get("evidence_type", "unknown")
        present_types.add(etype)
        freshness = item.get("freshness", classify_freshness(item.get("source_type", ""), item.get("timestamp", "")))
        reliability = item.get("reliability", SOURCE_RELIABILITY.get(item.get("source_type", ""), 0.5))

        if freshness in ("STALE", "EXPIRED"):
            stale.append(item)
        elif reliability < 0.5:
            uncertain.append(item)
        else:
            known.append(item)

    # Check for conflicts
    values_by_type = {}
    for item in known:
        t = item.get("evidence_type")
        values_by_type.setdefault(t, []).append(item)
    for t, items in values_by_type.items():
        if len(items) > 1:
            risk_levels = set(str(i.get("value", {}).get("risk_level", "")) for i in items)
            if len(risk_levels) > 1:
                conflicting.extend(items)
                known = [k for k in known if k not in items]

    # Missing types
    missing = expected_types - present_types
    for m in missing:
        unknown.append({"evidence_type": m, "status": "NOT_AVAILABLE"})

    overall = "KNOWN" if known and not conflicting and not stale else \
              "CONFLICTING" if conflicting else \
              "STALE" if stale and not known else \
              "UNCERTAIN" if uncertain else "UNKNOWN"

    return {
        "status": overall,
        "known": known,
        "unknown": unknown,
        "uncertain": uncertain,
        "conflicting": conflicting,
        "stale": stale,
        "coverage": len(present_types) / len(expected_types),
        "reliability_weighted_score": sum(i.get("reliability", 0.5) for i in known) / max(len(known), 1),
    }
''')

    # Phase 8: Contradiction Engine
    write_file(evidence_dir / "contradiction_engine.py", '''"""NER-LDI Contradiction Engine - detects conflicting evidence."""
from typing import List, Dict


def detect_contradictions(evidence_items: List[Dict]) -> Dict:
    """Detect and explain contradictions between evidence sources."""
    contradictions = []

    # Group by type
    by_type = {}
    for item in evidence_items:
        t = item.get("evidence_type", "unknown")
        by_type.setdefault(t, []).append(item)

    # Check rainfall vs satellite
    rainfall_items = by_type.get("rainfall", [])
    satellite_items = by_type.get("satellite", [])
    if rainfall_items and satellite_items:
        high_rain = any(i.get("value", {}).get("intensity", "") in ("HIGH", "EXTREME") for i in rainfall_items)
        low_sat_change = any(not i.get("value", {}).get("change_detected", True) for i in satellite_items)
        if high_rain and low_sat_change:
            contradictions.append({
                "type": "rainfall_vs_satellite",
                "severity": "MEDIUM",
                "explanation": "High rainfall detected but satellite shows no ground change. Possible: early stage, satellite stale, or false alarm.",
                "supporting_sources": [i.get("source") for i in rainfall_items],
                "conflicting_sources": [i.get("source") for i in satellite_items],
                "verification_required": True,
            })

    # Check citizen vs model
    citizen_items = by_type.get("citizen_report", [])
    model_items = by_type.get("model_output", [])
    if citizen_items and model_items:
        citizen_damage = any("damage" in str(i.get("value", "")).lower() or "slide" in str(i.get("value", "")).lower() for i in citizen_items)
        model_low = any(i.get("value", {}).get("risk_level") in ("VERY_LOW", "LOW") for i in model_items)
        if citizen_damage and model_low:
            contradictions.append({
                "type": "citizen_vs_model",
                "severity": "HIGH",
                "explanation": "Citizen reports damage/slide but model predicts low risk. Ground truth takes priority pending verification.",
                "supporting_sources": [i.get("source") for i in citizen_items],
                "conflicting_sources": ["risk_model"],
                "verification_required": True,
            })

    # Road status conflicts
    road_items = by_type.get("road_status", [])
    if len(road_items) > 1:
        statuses = set(str(i.get("value", {}).get("status", "")) for i in road_items)
        if len(statuses) > 1:
            contradictions.append({
                "type": "road_status_conflict",
                "severity": "HIGH",
                "explanation": f"Conflicting road status reports: {statuses}",
                "supporting_sources": [road_items[0].get("source")],
                "conflicting_sources": [i.get("source") for i in road_items[1:]],
                "verification_required": True,
            })

    return {
        "has_contradictions": len(contradictions) > 0,
        "contradiction_count": len(contradictions),
        "contradictions": contradictions,
        "evidence_status": "CONFLICTING" if contradictions else "CONSISTENT",
        "max_severity": max((c["severity"] for c in contradictions), default="NONE"),
    }
''')

    # Phase 9: Knowledge Gap Engine
    write_file(evidence_dir / "knowledge_gap_engine.py", '''"""NER-LDI Knowledge Gap Engine - identifies what the system does NOT know."""
from typing import List, Dict
from datetime import datetime, timezone, timedelta


EXPECTED_EVIDENCE = {
    "rainfall": {"max_age_hours": 6, "critical": True},
    "terrain": {"max_age_hours": 8760, "critical": True},
    "satellite": {"max_age_hours": 48, "critical": False},
    "historical": {"max_age_hours": 8760, "critical": False},
    "road_status": {"max_age_hours": 24, "critical": True},
    "forecast": {"max_age_hours": 12, "critical": True},
    "field_inspection": {"max_age_hours": 72, "critical": False},
}


def identify_knowledge_gaps(evidence_items: List[Dict], location: Dict = None) -> Dict:
    """Identify what the system doesn't know about a location."""
    now = datetime.now(timezone.utc)
    known, unknown, uncertain, stale, conflicting = [], [], [], [], []

    present_types = {}
    for item in evidence_items:
        etype = item.get("evidence_type", "unknown")
        present_types.setdefault(etype, []).append(item)

    for etype, config in EXPECTED_EVIDENCE.items():
        items = present_types.get(etype, [])
        if not items:
            unknown.append({
                "evidence_type": etype,
                "reason": f"No {etype} evidence available",
                "critical": config["critical"],
                "impact": f"Cannot assess {etype} contribution to risk"
            })
            continue

        # Check freshness
        latest = max(items, key=lambda x: x.get("timestamp", ""))
        try:
            ts = datetime.fromisoformat(latest.get("timestamp", "").replace("Z", "+00:00"))
            age_hours = (now - ts).total_seconds() / 3600
        except (ValueError, TypeError):
            age_hours = float("inf")

        if age_hours > config["max_age_hours"]:
            stale.append({
                "evidence_type": etype,
                "reason": f"{etype} evidence is {age_hours:.0f}h old (threshold: {config['max_age_hours']}h)",
                "critical": config["critical"],
                "last_update": latest.get("timestamp")
            })
        else:
            reliability = latest.get("reliability", 0.5)
            if reliability < 0.5:
                uncertain.append({"evidence_type": etype, "reason": f"Low reliability ({reliability:.2f})", "critical": config["critical"]})
            else:
                known.append({"evidence_type": etype, "reliability": reliability, "timestamp": latest.get("timestamp")})

    # Out-of-distribution check
    if location:
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        if lat > 27 or lat < 22:
            uncertain.append({"evidence_type": "spatial", "reason": "Location at edge of training coverage", "critical": False})

    return {
        "known_items": known,
        "unknown_items": unknown,
        "uncertain_items": uncertain,
        "stale_items": stale,
        "conflicting_items": conflicting,
        "total_gaps": len(unknown) + len(stale) + len(uncertain),
        "critical_gaps": sum(1 for i in unknown + stale if i.get("critical")),
        "knowledge_completeness": len(known) / max(len(EXPECTED_EVIDENCE), 1),
    }
''')

    # Phase 10: Next-Best-Evidence
    write_file(evidence_dir / "next_best_evidence.py", '''"""NER-LDI Next-Best-Evidence Engine - recommends most valuable observation to acquire."""
from typing import Dict, List
import math


CANDIDATE_ACTIONS = [
    {"action": "ROAD_STATUS_VERIFICATION", "base_cost": 0.3, "base_reliability": 0.90, "time_hours": 2},
    {"action": "FIELD_PHOTO", "base_cost": 0.2, "base_reliability": 0.75, "time_hours": 1},
    {"action": "FIELD_INSPECTION", "base_cost": 0.6, "base_reliability": 0.95, "time_hours": 4},
    {"action": "SATELLITE_REFRESH", "base_cost": 0.1, "base_reliability": 0.88, "time_hours": 12},
    {"action": "OFFICIAL_CONFIRMATION", "base_cost": 0.4, "base_reliability": 0.92, "time_hours": 6},
    {"action": "HISTORICAL_COMPARISON", "base_cost": 0.05, "base_reliability": 0.70, "time_hours": 0.5},
    {"action": "NO_ADDITIONAL_EVIDENCE", "base_cost": 0.0, "base_reliability": 0.0, "time_hours": 0},
]


def compute_next_best_evidence(risk_score: float, confidence: float, knowledge_gaps: Dict,
                                impact_data: Dict = None) -> Dict:
    """Recommend the most valuable next observation based on expected information gain."""
    uncertainty = 1.0 - confidence
    decision_importance = risk_score * (impact_data.get("population_exposed", 100) / 1000 if impact_data else 1.0)
    decision_importance = min(1.0, decision_importance)

    candidates = []
    critical_gaps = knowledge_gaps.get("unknown_items", []) + knowledge_gaps.get("stale_items", [])
    gap_types = set(g.get("evidence_type", "") for g in critical_gaps)

    for action in CANDIDATE_ACTIONS:
        if action["action"] == "NO_ADDITIONAL_EVIDENCE":
            if uncertainty < 0.2:
                candidates.append({**action, "information_value": 0.01, "reason": "Confidence already high"})
            continue

        # Base information value
        base_iv = uncertainty * action["base_reliability"]

        # Boost if fills a known gap
        gap_boost = 1.5 if any(g in action["action"].lower() for g in gap_types) else 1.0

        # Scale by decision importance
        iv = (base_iv * decision_importance * gap_boost) / max(action["base_cost"], 0.01)

        # Urgency
        urgency = "CRITICAL" if risk_score > 0.75 and uncertainty > 0.4 else \
                  "HIGH" if risk_score > 0.5 else "MEDIUM" if risk_score > 0.25 else "LOW"

        expected_reduction = uncertainty * action["base_reliability"] * 0.5

        candidates.append({
            "action": action["action"],
            "information_value": round(iv, 4),
            "expected_uncertainty_reduction": round(expected_reduction, 4),
            "cost": action["base_cost"],
            "time_hours": action["time_hours"],
            "urgency": urgency,
            "reason": f"Fills gap in {gap_types}" if gap_boost > 1 else "General uncertainty reduction",
        })

    candidates.sort(key=lambda x: x["information_value"], reverse=True)
    best = candidates[0] if candidates else {"action": "NO_ADDITIONAL_EVIDENCE", "reason": "No actionable options"}

    return {
        "recommended_observation": best["action"],
        "reason": best.get("reason", ""),
        "information_value": best.get("information_value", 0),
        "expected_uncertainty_reduction": best.get("expected_uncertainty_reduction", 0),
        "cost": best.get("cost", 0),
        "urgency": best.get("urgency", "LOW"),
        "all_candidates": candidates[:5],
    }
''')

    # Phase 11: Update Risk
    write_file(evidence_dir / "update_risk.py", '''"""NER-LDI Evidence Update Loop - updates risk after new evidence arrives."""
import uuid
from datetime import datetime, timezone
from typing import Dict, List


def update_risk_with_evidence(current_state: Dict, new_evidence: Dict) -> Dict:
    """Update risk prediction after new evidence is incorporated."""
    audit_entry = {
        "update_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_added": new_evidence.get("evidence_type"),
        "previous_risk": current_state.get("risk_score"),
        "previous_confidence": current_state.get("confidence"),
    }

    # Bayesian-style update
    prior_risk = current_state.get("risk_score", 0.5)
    prior_confidence = current_state.get("confidence", 0.5)
    evidence_reliability = new_evidence.get("reliability", 0.5)
    evidence_supports_risk = new_evidence.get("supports_risk", None)

    if evidence_supports_risk is True:
        # Evidence confirms risk
        posterior_risk = prior_risk + (1 - prior_risk) * evidence_reliability * 0.2
    elif evidence_supports_risk is False:
        # Evidence contradicts risk
        posterior_risk = prior_risk - prior_risk * evidence_reliability * 0.2
    else:
        posterior_risk = prior_risk

    posterior_risk = max(0.0, min(1.0, posterior_risk))

    # Confidence increases with new reliable evidence
    confidence_boost = evidence_reliability * 0.1
    posterior_confidence = min(1.0, prior_confidence + confidence_boost)

    # Update risk level
    if posterior_risk >= 0.8:
        risk_level = "CRITICAL"
    elif posterior_risk >= 0.6:
        risk_level = "HIGH"
    elif posterior_risk >= 0.4:
        risk_level = "MODERATE"
    elif posterior_risk >= 0.2:
        risk_level = "LOW"
    else:
        risk_level = "VERY_LOW"

    audit_entry["new_risk"] = posterior_risk
    audit_entry["new_confidence"] = posterior_confidence
    audit_entry["update_method"] = "bayesian_evidence_update"

    updated_state = {**current_state}
    updated_state["risk_score"] = round(posterior_risk, 4)
    updated_state["risk_level"] = risk_level
    updated_state["confidence"] = round(posterior_confidence, 4)
    updated_state.setdefault("audit_trail", []).append(audit_entry)
    updated_state["last_updated"] = audit_entry["timestamp"]

    return updated_state
''')

    # Phase 12: Citizen Verification
    write_file(evidence_dir / "citizen_verification.py", '''"""NER-LDI Citizen/Field Evidence Validation."""
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import hashlib


def verify_citizen_evidence(report: Dict) -> Dict:
    """Validate citizen-submitted evidence for reliability."""
    checks = []
    score = 0.5  # Start neutral

    lat = report.get("latitude")
    lon = report.get("longitude")
    timestamp = report.get("timestamp")
    description = report.get("description", "")
    has_image = bool(report.get("image_keys") or report.get("images"))
    has_video = bool(report.get("video_keys") or report.get("videos"))

    # Geographic consistency
    if lat and lon:
        if 21.0 <= lat <= 30.0 and 88.0 <= lon <= 98.0:
            checks.append({"check": "location_in_ner", "passed": True})
            score += 0.1
        else:
            checks.append({"check": "location_in_ner", "passed": False, "reason": "Outside NER bounds"})
            score -= 0.2

    # Timestamp plausibility
    if timestamp:
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - ts
            if age < timedelta(hours=0):
                checks.append({"check": "timestamp_future", "passed": False})
                score -= 0.3
            elif age < timedelta(hours=24):
                checks.append({"check": "timestamp_recent", "passed": True})
                score += 0.1
            else:
                checks.append({"check": "timestamp_aged", "passed": True, "age_hours": age.total_seconds()/3600})
        except (ValueError, TypeError):
            checks.append({"check": "timestamp_parse", "passed": False})

    # Media presence boosts reliability
    if has_image:
        score += 0.15
        checks.append({"check": "has_image", "passed": True})
    if has_video:
        score += 0.1
        checks.append({"check": "has_video", "passed": True})

    # Description quality
    if len(description) > 20:
        score += 0.05
        checks.append({"check": "description_length", "passed": True})

    # Landslide keywords
    keywords = ["slide", "landslide", "mud", "debris", "crack", "blocked", "collapse", "soil"]
    if any(k in description.lower() for k in keywords):
        score += 0.1
        checks.append({"check": "relevant_keywords", "passed": True})

    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        status = "LIKELY_VALID"
    elif score >= 0.5:
        status = "NEEDS_VERIFICATION"
    elif score >= 0.3:
        status = "LOW_CONFIDENCE"
    else:
        status = "LIKELY_INVALID"

    return {
        "reliability_score": round(score, 3),
        "validation_status": status,
        "detected_signals": checks,
        "reason": f"Score {score:.2f} based on {len(checks)} checks",
        "is_simulated": report.get("is_simulated", False),
    }
''')

    # Phase 13: Satellite Adapter
    write_file(evidence_dir / "satellite_adapter.py", '''"""NER-LDI Satellite Evidence Adapter - standardized interface for satellite data."""
from datetime import datetime, timezone
from typing import Dict, Optional
import uuid


def create_satellite_observation(source: str = "sentinel_2", lat: float = 0, lon: float = 0,
                                 change_detected: bool = False, ndvi_change: float = 0.0,
                                 coherence: float = 1.0, is_simulated: bool = True) -> Dict:
    """Create a standardized satellite evidence object."""
    return {
        "evidence_id": str(uuid.uuid4()),
        "source": source,
        "source_type": "satellite",
        "evidence_type": "satellite",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": {"latitude": lat, "longitude": lon},
        "value": {
            "change_detected": change_detected,
            "ndvi_change": ndvi_change,
            "coherence": coherence,
            "deformation_mm": None,
        },
        "freshness": "FRESH",
        "reliability": 0.88 if not is_simulated else 0.30,
        "is_simulated": is_simulated,
        "provenance": {
            "satellite": source,
            "method": "simulated_observation" if is_simulated else "automated_processing",
            "note": "SIMULATED - no real satellite data available" if is_simulated else "Real observation"
        }
    }
''')

    # Phase 14: Silent Zone Engine
    write_file(evidence_dir / "silent_zone_engine.py", '''"""NER-LDI Silent Zone Engine - identifies under-monitored high-risk areas."""
from typing import Dict, List
from datetime import datetime, timezone, timedelta


def detect_silent_zones(locations: List[Dict], evidence_by_location: Dict[str, List],
                        risk_scores: Dict[str, float] = None) -> List[Dict]:
    """Identify locations with high risk but low observation coverage."""
    silent_zones = []
    now = datetime.now(timezone.utc)

    for loc in locations:
        loc_id = loc.get("location_id", loc.get("name", "unknown"))
        evidence = evidence_by_location.get(loc_id, [])
        risk = risk_scores.get(loc_id, 0.5) if risk_scores else 0.5

        # Count recent evidence
        recent_count = 0
        for e in evidence:
            try:
                ts = datetime.fromisoformat(e.get("timestamp", "").replace("Z", "+00:00"))
                if (now - ts) < timedelta(hours=48):
                    recent_count += 1
            except (ValueError, TypeError):
                pass

        # Criteria for silent zone
        is_silent = (
            risk >= 0.4 and  # Moderate+ susceptibility
            recent_count < 2 and  # Very few recent observations
            loc.get("population", 0) > 0  # Has population exposure
        )

        if is_silent:
            priority = "CRITICAL" if risk > 0.7 else "HIGH" if risk > 0.5 else "MODERATE"
            silent_zones.append({
                "location_id": loc_id,
                "location": loc,
                "silent_zone_status": True,
                "reason": f"Risk={risk:.2f} but only {recent_count} recent observations",
                "monitoring_priority": priority,
                "risk_score": risk,
                "recent_observations": recent_count,
                "population_at_risk": loc.get("population", 0),
            })

    return sorted(silent_zones, key=lambda x: x["risk_score"], reverse=True)
''')

    # Touch __init__.py
    (evidence_dir / "__init__.py").touch()
    print("  Created: uncertainty_engine, evidence_fusion, contradiction_engine,")
    print("           knowledge_gap_engine, next_best_evidence, update_risk,")
    print("           citizen_verification, satellite_adapter, silent_zone_engine")


# ==============================================================
# PHASES 15-18: IMPACT ENGINES
# ==============================================================
def phase15_to_18_impact():
    print("\nPHASES 15-18: Impact Engines")
    impact_dir = PROJECT / "backend" / "app" / "impact"
    impact_dir.mkdir(parents=True, exist_ok=True)

    write_file(impact_dir / "road_impact.py", '''"""NER-LDI Road Network Impact Engine."""
import json
from pathlib import Path
from typing import Dict, List
import math

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ROADS_PATH = PROJECT_ROOT / "data" / "processed" / "roads" / "ner_roads.geojson"


def _load_roads():
    if not ROADS_PATH.exists():
        return []
    with open(ROADS_PATH) as f:
        data = json.load(f)
    return data.get("features", [])


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def compute_road_impact(lat: float, lon: float, risk_score: float, radius_km: float = 5.0) -> Dict:
    """Compute road impact for a landslide risk location."""
    roads = _load_roads()
    affected_roads = []

    for road in roads:
        props = road.get("properties", {})
        geom = road.get("geometry", {})
        coords = geom.get("coordinates", [])

        # Check if any road segment is within radius
        min_dist = float("inf")
        if geom.get("type") == "LineString":
            for c in coords:
                d = _haversine(lat, lon, c[1], c[0])
                min_dist = min(min_dist, d)
        elif geom.get("type") == "MultiLineString":
            for line in coords:
                for c in line:
                    d = _haversine(lat, lon, c[1], c[0])
                    min_dist = min(min_dist, d)

        if min_dist <= radius_km:
            blockage_prob = risk_score * max(0, 1.0 - min_dist / radius_km) * 0.8
            affected_roads.append({
                "road_id": props.get("road_id"),
                "name": props.get("name"),
                "road_type": props.get("road_type"),
                "distance_km": round(min_dist, 2),
                "blockage_probability": round(blockage_prob, 4),
                "is_critical": props.get("road_type") in ("NH", "SH"),
                "length_km": props.get("length_km", 0),
            })

    affected_roads.sort(key=lambda x: x["blockage_probability"], reverse=True)
    max_blockage = affected_roads[0]["blockage_probability"] if affected_roads else 0

    # Alternative routes
    alternatives = [r for r in affected_roads if r["blockage_probability"] < 0.3]

    return {
        "road_blockage_probability": round(max_blockage, 4),
        "road_risk_level": "HIGH" if max_blockage > 0.6 else "MODERATE" if max_blockage > 0.3 else "LOW",
        "affected_roads": affected_roads[:10],
        "critical_roads_at_risk": [r for r in affected_roads if r["is_critical"]],
        "alternative_routes": len(alternatives),
        "response_accessibility": "DEGRADED" if max_blockage > 0.5 else "NORMAL",
    }
''')

    write_file(impact_dir / "village_isolation.py", '''"""NER-LDI Village Connectivity and Isolation Engine."""
import json, math
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VILLAGES_PATH = PROJECT_ROOT / "data" / "processed" / "villages" / "ner_villages.geojson"
INFRA_PATH = PROJECT_ROOT / "data" / "processed" / "infrastructure" / "ner_infrastructure.geojson"


def _load_villages():
    if not VILLAGES_PATH.exists():
        return []
    with open(VILLAGES_PATH) as f:
        return json.load(f).get("features", [])


def _load_infrastructure():
    if not INFRA_PATH.exists():
        return []
    with open(INFRA_PATH) as f:
        return json.load(f).get("features", [])


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def compute_village_isolation(lat: float, lon: float, road_blockage_prob: float, radius_km: float = 10.0) -> Dict:
    """Compute village isolation risk from a potential road blockage."""
    villages = _load_villages()
    infrastructure = _load_infrastructure()
    affected_villages = []
    total_population = 0

    for v in villages:
        props = v.get("properties", {})
        geom = v.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])

        if dist <= radius_km:
            isolation_prob = road_blockage_prob * max(0, 1.0 - dist / radius_km)
            pop = props.get("population", 0)
            affected_villages.append({
                "village_id": props.get("village_id"),
                "name": props.get("name"),
                "distance_km": round(dist, 2),
                "population": pop,
                "isolation_probability": round(isolation_prob, 4),
                "has_health_facility": props.get("has_health_facility", False),
            })
            if isolation_prob > 0.3:
                total_population += pop

    # Hospital access
    hospitals_nearby = []
    for inf in infrastructure:
        props = inf.get("properties", {})
        if props.get("type") != "hospital":
            continue
        geom = inf.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])
        if dist <= radius_km * 2:
            hospitals_nearby.append({
                "name": props.get("name"),
                "distance_km": round(dist, 2),
                "beds": props.get("beds", 0),
                "access_degraded": dist <= radius_km and road_blockage_prob > 0.4
            })

    affected_villages.sort(key=lambda x: x["isolation_probability"], reverse=True)
    max_isolation = affected_villages[0]["isolation_probability"] if affected_villages else 0

    return {
        "village_isolation_probability": round(max_isolation, 4),
        "villages_at_risk": affected_villages[:10],
        "population_affected": total_population,
        "hospitals_nearby": hospitals_nearby,
        "hospital_access_degraded": any(h["access_degraded"] for h in hospitals_nearby),
        "emergency_access_loss": road_blockage_prob > 0.6,
        "alternate_route_available": road_blockage_prob < 0.8,
    }


def compute_infrastructure_exposure(lat: float, lon: float, risk_score: float, radius_km: float = 5.0) -> Dict:
    """Compute infrastructure exposure at risk location."""
    infrastructure = _load_infrastructure()
    villages = _load_villages()
    exposed = []
    critical = []

    for inf in infrastructure:
        props = inf.get("properties", {})
        geom = inf.get("geometry", {})
        if geom.get("type") != "Point":
            continue
        coords = geom["coordinates"]
        dist = _haversine(lat, lon, coords[1], coords[0])
        if dist <= radius_km:
            item = {"type": props.get("type"), "name": props.get("name"), "distance_km": round(dist, 2)}
            exposed.append(item)
            if props.get("type") in ("hospital", "school", "emergency_facility"):
                critical.append(item)

    pop_exposed = sum(v["properties"].get("population", 0) for v in villages
                      if v.get("geometry", {}).get("type") == "Point" and
                      _haversine(lat, lon, v["geometry"]["coordinates"][1], v["geometry"]["coordinates"][0]) <= radius_km)

    exposure_score = min(1.0, (len(critical) * 0.2 + pop_exposed / 10000) * risk_score)

    return {
        "exposure_score": round(exposure_score, 4),
        "assets_affected": exposed,
        "critical_assets": critical,
        "population_exposed": pop_exposed,
    }
''')

    (impact_dir / "__init__.py").touch()
    print("  Created: road_impact, village_isolation (with infrastructure_exposure)")


# ==============================================================
# PHASES 19-22: SIMULATION, OPTIMIZATION, HUMAN DECISION
# ==============================================================
def phase19_to_22():
    print("\nPHASES 19-22: Simulation, Optimization, Human Decision")
    sim_dir = PROJECT / "backend" / "app" / "simulation"
    sim_dir.mkdir(parents=True, exist_ok=True)
    dec_dir = PROJECT / "backend" / "app" / "decision_engine"
    dec_dir.mkdir(parents=True, exist_ok=True)

    write_file(sim_dir / "risk_simulation.py", '''"""NER-LDI What-If Simulation Engine."""
import uuid, copy
from datetime import datetime, timezone
from typing import Dict


def run_simulation(baseline_state: Dict, scenario: Dict) -> Dict:
    """Run a what-if simulation without mutating the base state."""
    sim_id = str(uuid.uuid4())
    simulated = copy.deepcopy(baseline_state)

    scenario_type = scenario.get("type", "custom")
    rainfall_factor = scenario.get("rainfall_factor", 1.0)
    road_closure = scenario.get("road_closure", False)

    # Apply rainfall change
    if rainfall_factor != 1.0:
        base_risk = simulated.get("risk_score", 0.5)
        # Rainfall increase raises risk non-linearly
        risk_boost = (rainfall_factor - 1.0) * 0.3 * base_risk
        simulated["risk_score"] = min(1.0, base_risk + risk_boost)
        simulated["rainfall_features"] = {
            k: (v * rainfall_factor if v else None)
            for k, v in (simulated.get("rainfall_features") or {}).items()
        }

    # Apply road closure
    if road_closure:
        simulated["road_blockage_probability"] = max(simulated.get("road_blockage_probability", 0), 0.9)
        simulated["village_isolation_probability"] = max(simulated.get("village_isolation_probability", 0), 0.7)

    # Recalculate priority
    risk = simulated.get("risk_score", 0.5)
    pop = simulated.get("population_exposed", 0)
    simulated["priority_score"] = min(1.0, risk * 0.6 + (pop / 10000) * 0.4)

    # Update risk level
    r = simulated["risk_score"]
    simulated["risk_level"] = "CRITICAL" if r >= 0.8 else "HIGH" if r >= 0.6 else "MODERATE" if r >= 0.4 else "LOW" if r >= 0.2 else "VERY_LOW"

    delta = {
        "risk_change": simulated["risk_score"] - baseline_state.get("risk_score", 0.5),
        "priority_change": simulated.get("priority_score", 0) - baseline_state.get("priority_score", 0),
        "isolation_change": simulated.get("village_isolation_probability", 0) - baseline_state.get("village_isolation_probability", 0),
    }

    return {
        "simulation_id": sim_id,
        "scenario_type": scenario_type,
        "input_changes": scenario,
        "baseline_state": baseline_state,
        "simulated_state": simulated,
        "delta": delta,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_simulated": True,
    }
''')

    write_file(dec_dir / "optimizer.py", '''"""NER-LDI Resource-Constrained Action Optimizer."""
from typing import Dict, List


INTERVENTIONS = [
    {"action": "inspect_road", "cost": 2, "time_hours": 3, "harm_reduction_factor": 0.1},
    {"action": "field_verification", "cost": 3, "time_hours": 4, "harm_reduction_factor": 0.15},
    {"action": "prepare_route", "cost": 5, "time_hours": 6, "harm_reduction_factor": 0.2},
    {"action": "pre_position_team", "cost": 8, "time_hours": 2, "harm_reduction_factor": 0.3},
    {"action": "increase_monitoring", "cost": 1, "time_hours": 1, "harm_reduction_factor": 0.05},
    {"action": "issue_warning_recommendation", "cost": 1, "time_hours": 0.5, "harm_reduction_factor": 0.25},
    {"action": "restrict_corridor_recommendation", "cost": 4, "time_hours": 1, "harm_reduction_factor": 0.35},
    {"action": "prepare_evacuation_support", "cost": 10, "time_hours": 4, "harm_reduction_factor": 0.4},
]


def optimize_actions(locations: List[Dict], budget: float = 20, teams: int = 3) -> Dict:
    """Greedy optimization: maximize expected harm reduction under resource constraints."""
    candidates = []

    for loc in locations:
        risk = loc.get("risk_score", 0.5)
        pop = loc.get("population_exposed", 100)
        expected_harm = risk * pop / 1000

        for intervention in INTERVENTIONS:
            if intervention["cost"] > budget:
                continue
            reduction = intervention["harm_reduction_factor"] * expected_harm
            efficiency = reduction / max(intervention["cost"], 0.1)
            candidates.append({
                "location_id": loc.get("location_id", "unknown"),
                "action": intervention["action"],
                "cost": intervention["cost"],
                "time_hours": intervention["time_hours"],
                "expected_harm_reduction": round(reduction, 4),
                "efficiency": round(efficiency, 4),
                "requires_human_approval": intervention["action"] in ("restrict_corridor_recommendation", "prepare_evacuation_support", "issue_warning_recommendation"),
            })

    # Greedy selection
    candidates.sort(key=lambda x: x["efficiency"], reverse=True)
    selected = []
    remaining_budget = budget
    remaining_teams = teams

    for c in candidates:
        if c["cost"] <= remaining_budget and remaining_teams > 0:
            selected.append(c)
            remaining_budget -= c["cost"]
            remaining_teams -= 1

    return {
        "selected_actions": selected,
        "total_cost": budget - remaining_budget,
        "total_harm_reduction": sum(a["expected_harm_reduction"] for a in selected),
        "remaining_budget": remaining_budget,
        "any_requires_approval": any(a["requires_human_approval"] for a in selected),
    }
''')

    write_file(dec_dir / "human_decision.py", '''"""NER-LDI Human Decision Loop - AI recommends, human decides."""
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional


def create_decision_record(location: Dict, risk_state: Dict, recommended_actions: list) -> Dict:
    """Create a decision record requiring human review."""
    needs_approval = any(a.get("requires_human_approval") for a in recommended_actions)

    return {
        "decision_id": str(uuid.uuid4()),
        "location": location,
        "risk_state": {
            "risk_score": risk_state.get("risk_score"),
            "risk_level": risk_state.get("risk_level"),
            "confidence": risk_state.get("confidence"),
        },
        "recommended_actions": recommended_actions,
        "human_approval_required": needs_approval,
        "human_decision": {"status": "PENDING"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_trail": [{
            "event": "CREATED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": "system",
        }],
    }


def record_human_decision(decision_record: Dict, status: str, decided_by: str,
                          reason: str = "", modified_actions: list = None) -> Dict:
    """Record human approval/rejection/modification."""
    decision_record["human_decision"] = {
        "status": status,
        "decided_by": decided_by,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modified_actions": modified_actions,
    }
    decision_record["audit_trail"].append({
        "event": f"HUMAN_{status}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": decided_by,
        "reason": reason,
    })
    return decision_record


def record_outcome(decision_record: Dict, actual_event: bool, harm_realized: float = 0,
                   feedback_category: str = "CORRECT") -> Dict:
    """Record the actual outcome for learning."""
    decision_record["outcome"] = {
        "actual_event": actual_event,
        "harm_realized": harm_realized,
        "feedback_category": feedback_category,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    decision_record["audit_trail"].append({
        "event": "OUTCOME_RECORDED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feedback": feedback_category,
    })
    return decision_record
''')

    (sim_dir / "__init__.py").touch()
    (dec_dir / "__init__.py").touch()
    print("  Created: risk_simulation, optimizer, human_decision")


# ==============================================================
# PHASE 30: DEMO SCENARIO
# ==============================================================
def phase30_demo():
    print("\nPHASE 30: Replayable Demo Scenario")
    sys.path.insert(0, str(PROJECT / "backend" / "app"))

    from evidence.uncertainty_engine import compute_uncertainty
    from evidence.evidence_fusion import fuse_evidence
    from evidence.contradiction_engine import detect_contradictions
    from evidence.knowledge_gap_engine import identify_knowledge_gaps
    from evidence.next_best_evidence import compute_next_best_evidence
    from evidence.update_risk import update_risk_with_evidence
    from evidence.citizen_verification import verify_citizen_evidence
    from evidence.satellite_adapter import create_satellite_observation
    from impact.road_impact import compute_road_impact
    from impact.village_isolation import compute_village_isolation, compute_infrastructure_exposure
    from simulation.risk_simulation import run_simulation
    from decision_engine.optimizer import optimize_actions
    from decision_engine.human_decision import create_decision_record, record_human_decision, record_outcome

    # Demo location: Known landslide-prone area in Assam
    location = {"latitude": 25.5, "longitude": 93.0, "location_id": "demo_loc_01", "name": "Haflong Road Corridor"}

    # Step 1: Initial terrain-based risk
    risk_state = {
        "location": location,
        "risk_score": 0.65,
        "risk_level": "HIGH",
        "confidence": 0.55,
        "terrain_features": {"elevation": 850, "slope": 32, "aspect": 180, "terrain_ruggedness": 28},
        "rainfall_features": {"rainfall_1d": 45, "rainfall_3d": 120, "rainfall_7d": 280, "antecedent_rainfall_index": 65},
        "model_version": "2.0.0-dynamic-partial",
        "timestamp": "2024-06-05T06:00:00Z",
    }

    # Step 2: Evidence arrives
    evidence_items = [
        {"evidence_id": "ev1", "source": "IMERG", "source_type": "rainfall_sensor", "evidence_type": "rainfall",
         "timestamp": "2024-06-05T05:00:00Z", "value": {"intensity": "HIGH", "rainfall_24h": 85},
         "reliability": 0.88, "freshness": "FRESH", "is_simulated": True},
        {"evidence_id": "ev2", "source": "terrain_model", "source_type": "model_output", "evidence_type": "terrain",
         "timestamp": "2024-06-05T06:00:00Z", "value": {"risk_level": "HIGH", "slope": 32},
         "reliability": 0.82, "freshness": "FRESH", "is_simulated": True},
        {"evidence_id": "ev3", "source": "sentinel_2", "source_type": "satellite", "evidence_type": "satellite",
         "timestamp": "2024-06-02T10:00:00Z", "value": {"change_detected": False, "ndvi_change": -0.02},
         "reliability": 0.85, "freshness": "STALE", "is_simulated": True},
    ]

    # Step 3: Compute uncertainty
    uncertainty = compute_uncertainty(risk_state["risk_score"], risk_state["terrain_features"], evidence_items)
    risk_state["confidence"] = uncertainty["confidence"]
    risk_state["uncertainty"] = {"level": uncertainty["uncertainty_level"], "reasons": uncertainty["uncertainty_reasons"]}

    # Step 4: Evidence fusion
    fusion = fuse_evidence(evidence_items)

    # Step 5: Contradiction detection
    contradictions = detect_contradictions(evidence_items)

    # Step 6: Knowledge gaps
    gaps = identify_knowledge_gaps(evidence_items, location)

    # Step 7: Next-best-evidence
    nbe = compute_next_best_evidence(risk_state["risk_score"], uncertainty["confidence"], gaps)

    # Step 8: Citizen evidence arrives
    citizen_report = {
        "latitude": 25.505, "longitude": 93.002,
        "timestamp": "2024-06-05T08:30:00Z",
        "description": "Large debris slide blocking road near km 42. Mud and rocks on highway. Very dangerous.",
        "image_keys": ["img_001.jpg"],
        "is_simulated": True,
    }
    citizen_verified = verify_citizen_evidence(citizen_report)

    # Step 9: Update risk with citizen evidence
    new_evidence = {
        "evidence_type": "citizen_report",
        "reliability": citizen_verified["reliability_score"],
        "supports_risk": True,
        "is_simulated": True,
    }
    risk_state = update_risk_with_evidence(risk_state, new_evidence)

    # Step 10: Road impact
    road_impact = compute_road_impact(location["latitude"], location["longitude"], risk_state["risk_score"])
    risk_state["road_blockage_probability"] = road_impact["road_blockage_probability"]

    # Step 11: Village isolation
    isolation = compute_village_isolation(location["latitude"], location["longitude"], road_impact["road_blockage_probability"])
    risk_state["village_isolation_probability"] = isolation["village_isolation_probability"]
    risk_state["population_exposed"] = isolation["population_affected"]

    # Step 12: Infrastructure exposure
    exposure = compute_infrastructure_exposure(location["latitude"], location["longitude"], risk_state["risk_score"])

    # Step 13: What-if simulation - rainfall increases
    sim_result = run_simulation(risk_state, {"type": "rainfall_increase", "rainfall_factor": 1.5})

    # Step 14: Priority calculation
    risk_state["priority_score"] = min(1.0, risk_state["risk_score"] * 0.5 + (risk_state.get("population_exposed", 0) / 5000) * 0.3 + road_impact["road_blockage_probability"] * 0.2)

    # Step 15: Action optimization
    opt_result = optimize_actions([{**location, **risk_state}])

    # Step 16: Human decision
    decision = create_decision_record(location, risk_state, opt_result["selected_actions"])
    decision = record_human_decision(decision, "APPROVED", "district_dm_officer", "Confirmed via field radio. Approve all actions.")
    decision = record_outcome(decision, actual_event=True, harm_realized=0.2, feedback_category="CORRECT")

    # Build complete scenario
    scenario = {
        "scenario_name": "NER-LDI SIH Demo - Haflong Road Corridor",
        "description": "Deterministic replayable demonstration of the complete NER-LDI decision loop",
        "seed": SEED,
        "is_simulated": True,
        "all_evidence_simulated": True,
        "generated": NOW,
        "steps": [
            {"step": 1, "name": "Initial Risk Assessment", "data": {"risk_score": 0.65, "confidence": 0.55}},
            {"step": 2, "name": "Evidence Collection", "data": {"items": len(evidence_items)}},
            {"step": 3, "name": "Uncertainty Computation", "data": uncertainty},
            {"step": 4, "name": "Evidence Fusion", "data": {"status": fusion["status"], "coverage": fusion["coverage"]}},
            {"step": 5, "name": "Contradiction Detection", "data": contradictions},
            {"step": 6, "name": "Knowledge Gap Analysis", "data": {"gaps": gaps["total_gaps"], "critical": gaps["critical_gaps"]}},
            {"step": 7, "name": "Next-Best-Evidence", "data": nbe},
            {"step": 8, "name": "Citizen Evidence Arrives", "data": citizen_verified},
            {"step": 9, "name": "Risk Updated", "data": {"new_risk": risk_state["risk_score"], "new_confidence": risk_state["confidence"]}},
            {"step": 10, "name": "Road Impact", "data": road_impact},
            {"step": 11, "name": "Village Isolation", "data": {"isolation_prob": isolation["village_isolation_probability"], "pop_affected": isolation["population_affected"]}},
            {"step": 12, "name": "Infrastructure Exposure", "data": exposure},
            {"step": 13, "name": "What-If Simulation (Rain +50%)", "data": {"simulated_risk": sim_result["simulated_state"]["risk_score"], "delta": sim_result["delta"]}},
            {"step": 14, "name": "Priority Calculation", "data": {"priority": risk_state["priority_score"]}},
            {"step": 15, "name": "Action Optimization", "data": opt_result},
            {"step": 16, "name": "Human Decision & Outcome", "data": {"status": decision["human_decision"]["status"], "feedback": decision["outcome"]["feedback_category"]}},
        ],
        "final_state": risk_state,
        "decision_record": decision,
    }

    sim_dir = PROJECT / "data" / "simulation"
    sim_dir.mkdir(parents=True, exist_ok=True)
    with open(sim_dir / "ner_ldi_demo_scenario.json", "w") as f:
        json.dump(scenario, f, indent=2, default=str)

    print(f"  Demo scenario: data/simulation/ner_ldi_demo_scenario.json")
    print(f"  Steps: {len(scenario['steps'])}")
    print(f"  Final risk: {risk_state['risk_score']:.4f}, Confidence: {risk_state['confidence']:.4f}")
    return scenario


# ==============================================================
# PHASE 31: MODEL REGISTRY
# ==============================================================
def phase31_registry():
    print("\nPHASE 31: Model Registry")
    artifacts_dir = PROJECT / "ml" / "artifacts"

    # Load existing metadata
    baseline_meta = json.load(open(artifacts_dir / "terrain_susceptibility_metadata.json"))
    dynamic_meta_path = artifacts_dir / "ner_dynamic_risk_metadata.json"
    dynamic_meta = json.load(open(dynamic_meta_path)) if dynamic_meta_path.exists() else {"status": "NOT_BUILT"}

    registry = {
        "registry_version": "1.0.0",
        "updated": NOW,
        "models": {
            "terrain_susceptibility_baseline": {
                "path": "ml/artifacts/terrain_susceptibility_model.joblib",
                "version": baseline_meta.get("model_version", "1.0.0-baseline"),
                "type": baseline_meta.get("model_type"),
                "features": baseline_meta.get("feature_names"),
                "metrics": baseline_meta.get("evaluation_metrics"),
                "training_date": baseline_meta.get("training_timestamp"),
                "status": "ACTIVE",
                "limitations": ["Terrain only", "Partial coverage (24/57 cells)"]
            },
            "dynamic_risk_model": {
                "path": "ml/artifacts/ner_dynamic_risk_model.joblib",
                "version": dynamic_meta.get("model_version", "2.0.0-dynamic-partial"),
                "type": dynamic_meta.get("model_type"),
                "features": dynamic_meta.get("features"),
                "metrics": dynamic_meta.get("metrics"),
                "training_date": dynamic_meta.get("training_timestamp"),
                "status": "INCOMPLETE",
                "limitations": dynamic_meta.get("limitations", [])
            },
            "risk_calibrator": {
                "path": "ml/artifacts/risk_calibrator.joblib",
                "version": "1.0.0",
                "type": "IsotonicCalibration",
                "status": "ACTIVE",
            }
        },
        "feature_version": "2.0.0",
        "known_limitations": [
            "Terrain coverage partial (24/57 SRTM cells)",
            "Rainfall history only 7 days",
            "Dynamic model INCOMPLETE for production use",
            "No real satellite observations integrated",
            "Infrastructure data is representative, not exhaustive"
        ]
    }

    with open(artifacts_dir / "model_registry.json", "w") as f:
        json.dump(registry, f, indent=2)
    print(f"  Registry: ml/artifacts/model_registry.json")


# ==============================================================
# UTILITY
# ==============================================================
def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ==============================================================
# MAIN
# ==============================================================
def main():
    print("=" * 60)
    print("NER-LDI COMPLETE DECISION INTELLIGENCE SYSTEM BUILD")
    print("=" * 60)
    print(f"Started: {NOW}\n")

    phase1_schemas()
    phase2_rainfall_features()
    dynamic_df = phase3_feature_join()
    phase4_dynamic_model(dynamic_df)
    phase5_calibration()
    phase6_to_14_engines()
    phase15_to_18_impact()
    phase19_to_22()
    phase30_demo()
    phase31_registry()

    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
