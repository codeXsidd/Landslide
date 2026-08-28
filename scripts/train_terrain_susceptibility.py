"""
NER-LDI Terrain-Based Landslide Susceptibility Baseline Model
Trains RF and XGBoost classifiers on terrain features extracted at GSI landslide locations.
"""

import os
import sys
import json
import datetime
import numpy as np
import pandas as pd
import rasterio
import rasterio.windows
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve, brier_score_loss,
)
from sklearn.calibration import calibration_curve
from sklearn.model_selection import GroupKFold
import xgboost as xgb
import joblib

SEED = 42
np.random.seed(SEED)

PROJECT_ROOT = Path(__file__).parent.parent
TERRAIN_DIR = PROJECT_ROOT / "data" / "processed" / "terrain"
LANDSLIDE_CSV = PROJECT_ROOT / "data" / "processed" / "landslides" / "gsi_landslide_inventory_ner.csv"
ML_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "ml"
ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
DOCS_ML_DIR = PROJECT_ROOT / "docs" / "ml"

RASTER_FILES = {
    "elevation": TERRAIN_DIR / "elevation.tif",
    "slope": TERRAIN_DIR / "slope.tif",
    "aspect": TERRAIN_DIR / "aspect.tif",
    "terrain_ruggedness": TERRAIN_DIR / "terrain_ruggedness.tif",
}

FEATURES = ["elevation", "slope", "aspect", "terrain_ruggedness"]
MIN_DISTANCE_DEG = 0.01  # ~1.1 km minimum distance from landslide for negative samples
NEGATIVE_RATIO = 2  # 2 negatives per positive


def extract_raster_value(ds, lon, lat):
    try:
        row, col = ds.index(lon, lat)
        if 0 <= row < ds.height and 0 <= col < ds.width:
            val = ds.read(1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]
            if val == ds.nodata:
                return np.nan
            return float(val)
    except Exception:
        pass
    return np.nan


def point_in_bounds(lon, lat, bounds):
    return (bounds.left <= lon <= bounds.right and
            bounds.bottom <= lat <= bounds.top)


def task1_build_training_data():
    print("=" * 60)
    print("TASK 1: BUILD TRAINING DATA")
    print("=" * 60)

    df = pd.read_csv(LANDSLIDE_CSV)
    total_gsi = len(df)
    print(f"  Total GSI NER events: {total_gsi}")

    df = df.dropna(subset=["latitude", "longitude"])
    df = df[(df.latitude >= -90) & (df.latitude <= 90)]
    df = df[(df.longitude >= -180) & (df.longitude <= 180)]

    with rasterio.open(TERRAIN_DIR / "ner_dem.tif") as dem_ds:
        bounds = dem_ds.bounds
        nodata = dem_ds.nodata

    inside_mask = df.apply(
        lambda r: point_in_bounds(r.longitude, r.latitude, bounds), axis=1
    )
    df_inside = df[inside_mask].copy()
    excluded = total_gsi - len(df_inside)
    print(f"  Events inside terrain coverage: {len(df_inside)}")
    print(f"  Events excluded (outside terrain): {excluded}")

    # Open all rasters
    raster_datasets = {}
    for name, path in RASTER_FILES.items():
        raster_datasets[name] = rasterio.open(path)

    # Extract features for positive samples
    print("  Extracting terrain features for landslide locations...")
    for feat_name, ds in raster_datasets.items():
        df_inside[feat_name] = df_inside.apply(
            lambda r: extract_raster_value(ds, r.longitude, r.latitude), axis=1
        )

    # Drop rows where ALL terrain features are NaN
    valid_mask = df_inside[FEATURES].notna().any(axis=1)
    df_positive = df_inside[valid_mask].copy()
    print(f"  Valid positive samples (at least one terrain value): {len(df_positive)}")

    # Drop rows with ANY missing terrain feature for clean training
    complete_mask = df_positive[FEATURES].notna().all(axis=1)
    df_positive = df_positive[complete_mask].copy()
    print(f"  Complete positive samples (all features present): {len(df_positive)}")

    df_positive["label"] = 1
    n_positive = len(df_positive)
    n_negative = n_positive * NEGATIVE_RATIO

    # Generate negative samples
    print(f"  Generating {n_negative} negative samples...")
    landslide_lons = df_positive.longitude.values
    landslide_lats = df_positive.latitude.values

    dem_ds = raster_datasets["elevation"]
    negative_samples = []
    max_attempts = n_negative * 20
    attempts = 0

    rng = np.random.default_rng(SEED)

    while len(negative_samples) < n_negative and attempts < max_attempts:
        batch_size = min(n_negative * 3, max_attempts - attempts)
        rand_lons = rng.uniform(bounds.left + 0.01, bounds.right - 0.01, batch_size)
        rand_lats = rng.uniform(bounds.bottom + 0.01, bounds.top - 0.01, batch_size)

        for lon, lat in zip(rand_lons, rand_lats):
            if len(negative_samples) >= n_negative:
                break
            attempts += 1

            # Check minimum distance from all landslides
            dists = np.sqrt((landslide_lons - lon)**2 + (landslide_lats - lat)**2)
            if dists.min() < MIN_DISTANCE_DEG:
                continue

            # Extract features
            values = {}
            all_valid = True
            for feat_name, ds in raster_datasets.items():
                val = extract_raster_value(ds, lon, lat)
                if np.isnan(val):
                    all_valid = False
                    break
                values[feat_name] = val

            if not all_valid:
                continue

            values["latitude"] = lat
            values["longitude"] = lon
            values["label"] = 0
            negative_samples.append(values)

    for ds in raster_datasets.values():
        ds.close()

    print(f"  Generated {len(negative_samples)} negative samples (attempts: {attempts})")

    df_negative = pd.DataFrame(negative_samples)

    # Combine
    pos_cols = ["latitude", "longitude"] + FEATURES + ["label"]
    df_train = pd.concat([
        df_positive[pos_cols],
        df_negative[pos_cols]
    ], ignore_index=True)

    # Shuffle
    df_train = df_train.sample(frac=1, random_state=SEED).reset_index(drop=True)

    # Save
    ML_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_train.to_parquet(ML_DATA_DIR / "terrain_susceptibility_dataset.parquet", index=False)
    df_train.to_csv(ML_DATA_DIR / "terrain_susceptibility_dataset.csv", index=False)

    missing_per_feature = df_train[FEATURES].isna().sum().to_dict()

    print(f"\n  SUMMARY:")
    print(f"  Total GSI NER events: {total_gsi}")
    print(f"  Events inside terrain: {len(df_inside)}")
    print(f"  Events excluded: {excluded}")
    print(f"  Positive samples: {n_positive}")
    print(f"  Negative samples: {len(negative_samples)}")
    print(f"  Final training rows: {len(df_train)}")
    print(f"  Missing values per feature: {missing_per_feature}")

    return df_train, n_positive, len(negative_samples), total_gsi, excluded


def task2_spatial_split(df):
    print("\n" + "=" * 60)
    print("TASK 2: SPATIAL TRAIN/TEST SPLIT")
    print("=" * 60)

    # Grid-based spatial blocking: assign each point to a 0.5-degree grid cell
    grid_size = 0.5
    df["grid_x"] = (df.longitude / grid_size).astype(int)
    df["grid_y"] = (df.latitude / grid_size).astype(int)
    df["spatial_block"] = df["grid_x"].astype(str) + "_" + df["grid_y"].astype(str)

    unique_blocks = df["spatial_block"].unique()
    n_blocks = len(unique_blocks)
    print(f"  Spatial blocks (0.5° grid): {n_blocks}")

    # Assign blocks to folds using hash for reproducibility
    block_to_fold = {}
    rng = np.random.default_rng(SEED)
    shuffled_blocks = rng.permutation(unique_blocks)
    test_fraction = 0.25
    n_test_blocks = max(1, int(n_blocks * test_fraction))
    test_blocks = set(shuffled_blocks[:n_test_blocks])

    df["is_test"] = df["spatial_block"].isin(test_blocks)
    train_df = df[~df["is_test"]].copy()
    test_df = df[df["is_test"]].copy()

    # Clean up temp columns
    for col in ["grid_x", "grid_y", "spatial_block", "is_test"]:
        df.drop(columns=[col], inplace=True)
        train_df.drop(columns=[col], inplace=True)
        test_df.drop(columns=[col], inplace=True)

    print(f"  Test blocks: {n_test_blocks}/{n_blocks}")
    print(f"  Train rows: {len(train_df)} (pos={train_df.label.sum()}, neg={(train_df.label==0).sum()})")
    print(f"  Test rows: {len(test_df)} (pos={test_df.label.sum()}, neg={(test_df.label==0).sum()})")

    return train_df, test_df


def task3_train_models(train_df, test_df):
    print("\n" + "=" * 60)
    print("TASK 3: TRAIN MODELS")
    print("=" * 60)

    X_train = train_df[FEATURES].values
    y_train = train_df["label"].values
    X_test = test_df[FEATURES].values
    y_test = test_df["label"].values

    n_pos = y_train.sum()
    n_neg = (y_train == 0).sum()
    scale_pos_weight = n_neg / max(n_pos, 1)

    # RandomForest
    print("  Training RandomForestClassifier...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=SEED,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    print("    Done.")

    # XGBoost
    print("  Training XGBClassifier...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=SEED,
        use_label_encoder=False,
        eval_metric="logloss",
        n_jobs=-1,
    )
    xgb_model.fit(X_train, y_train)
    print("    Done.")

    return {"RandomForest": rf, "XGBoost": xgb_model}, X_train, y_train, X_test, y_test


def task4_evaluate(models, X_test, y_test):
    print("\n" + "=" * 60)
    print("TASK 4: EVALUATION")
    print("=" * 60)

    results = {}
    for name, model in models.items():
        print(f"\n  --- {name} ---")
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        brier = brier_score_loss(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        print(f"  Accuracy:  {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall:    {rec:.4f}")
        print(f"  F1:        {f1:.4f}")
        print(f"  ROC-AUC:   {roc_auc:.4f}")
        print(f"  PR-AUC:    {pr_auc:.4f}")
        print(f"  Brier:     {brier:.4f}")
        print(f"  Confusion Matrix:\n    {cm}")

        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "brier_score": brier,
            "confusion_matrix": cm.tolist(),
            "y_prob": y_prob,
            "y_pred": y_pred,
        }

    return results


def task5_select_model(results):
    print("\n" + "=" * 60)
    print("TASK 5: SELECT BEST MODEL")
    print("=" * 60)

    best_name = None
    best_score = -1

    for name, r in results.items():
        composite = 0.4 * r["pr_auc"] + 0.3 * r["roc_auc"] + 0.2 * r["f1"] + 0.1 * (1 - r["brier_score"])
        print(f"  {name}: composite={composite:.4f} (PR-AUC={r['pr_auc']:.4f}, ROC-AUC={r['roc_auc']:.4f}, F1={r['f1']:.4f}, Brier={r['brier_score']:.4f})")
        if composite > best_score:
            best_score = composite
            best_name = name

    print(f"\n  Selected: {best_name}")
    return best_name


def task6_save_model(models, best_name, results, train_df, test_df, n_positive, n_negative, total_gsi, excluded):
    print("\n" + "=" * 60)
    print("TASK 6: SAVE MODEL")
    print("=" * 60)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    model = models[best_name]
    model_path = ARTIFACTS_DIR / "terrain_susceptibility_model.joblib"
    joblib.dump(model, model_path)
    print(f"  Model saved: {model_path}")

    r = results[best_name]
    metadata = {
        "model_type": best_name,
        "model_version": "1.0.0-baseline",
        "feature_names": FEATURES,
        "training_row_count": len(train_df) + len(test_df),
        "positive_count": n_positive,
        "negative_count": n_negative,
        "train_count": len(train_df),
        "test_count": len(test_df),
        "random_seed": SEED,
        "split_method": "spatial_grid_block_0.5deg",
        "evaluation_metrics": {
            "accuracy": r["accuracy"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
            "roc_auc": r["roc_auc"],
            "pr_auc": r["pr_auc"],
            "brier_score": r["brier_score"],
            "confusion_matrix": r["confusion_matrix"],
        },
        "training_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "terrain_source_paths": {k: str(v.relative_to(PROJECT_ROOT)) for k, v in RASTER_FILES.items()},
        "gsi_source_path": str(LANDSLIDE_CSV.relative_to(PROJECT_ROOT)),
        "total_gsi_events": total_gsi,
        "events_excluded_no_terrain": excluded,
        "terrain_coverage": "PARTIAL (24/57 NER cells)",
        "negative_sampling_method": f"random background, min {MIN_DISTANCE_DEG} deg from landslides",
        "negative_ratio": NEGATIVE_RATIO,
    }

    meta_path = ARTIFACTS_DIR / "terrain_susceptibility_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved: {meta_path}")

    return metadata


def task7_feature_importance(models, best_name, results, y_test):
    print("\n" + "=" * 60)
    print("TASK 7: FEATURE IMPORTANCE")
    print("=" * 60)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    DOCS_ML_DIR.mkdir(parents=True, exist_ok=True)

    model = models[best_name]
    if best_name == "RandomForest":
        importances = model.feature_importances_
    else:
        importances = model.feature_importances_

    sorted_idx = np.argsort(importances)[::-1]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(FEATURES)))
    bars = ax.barh(
        [FEATURES[i] for i in sorted_idx[::-1]],
        importances[sorted_idx[::-1]],
        color=colors
    )
    ax.set_xlabel("Feature Importance")
    ax.set_title(f"Terrain Feature Importance ({best_name})")
    plt.tight_layout()
    plt.savefig(DOCS_ML_DIR / "terrain_feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("  Feature importance ranking:")
    for i in sorted_idx:
        print(f"    {FEATURES[i]}: {importances[i]:.4f}")
    print(f"  Saved: {DOCS_ML_DIR / 'terrain_feature_importance.png'}")

    # Also generate ROC and PR curves
    for name, r in results.items():
        y_prob = r["y_prob"]

        fpr, tpr, _ = roc_curve(y_test, y_prob)
        prec_arr, rec_arr, _ = precision_recall_curve(y_test, y_prob)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        axes[0].plot(fpr, tpr, lw=2, label=f"ROC (AUC={r['roc_auc']:.3f})")
        axes[0].plot([0, 1], [0, 1], "k--", lw=1)
        axes[0].set_xlabel("False Positive Rate")
        axes[0].set_ylabel("True Positive Rate")
        axes[0].set_title(f"ROC Curve - {name}")
        axes[0].legend()

        axes[1].plot(rec_arr, prec_arr, lw=2, label=f"PR (AUC={r['pr_auc']:.3f})")
        axes[1].set_xlabel("Recall")
        axes[1].set_ylabel("Precision")
        axes[1].set_title(f"Precision-Recall Curve - {name}")
        axes[1].legend()

        plt.tight_layout()
        plt.savefig(DOCS_ML_DIR / f"curves_{name.lower()}.png", dpi=150, bbox_inches="tight")
        plt.close()

    return importances


def task8_report(metadata, results, importances):
    print("\n" + "=" * 60)
    print("TASK 8: MODEL REPORT")
    print("=" * 60)

    report_path = DOCS_ML_DIR / "terrain_susceptibility_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# NER-LDI Terrain-Based Landslide Susceptibility Baseline Model\n\n")
        f.write(f"**Generated**: {metadata['training_timestamp']}\n")
        f.write(f"**Model Version**: {metadata['model_version']}\n\n")

        f.write("## 1. Purpose\n\n")
        f.write("This is a **baseline static susceptibility model** that estimates relative landslide susceptibility\n")
        f.write("based solely on terrain morphology. It identifies areas where topographic conditions are similar\n")
        f.write("to historically recorded landslide locations in Northeast India.\n\n")

        f.write("## 2. Data Sources\n\n")
        f.write(f"- **Landslide inventory**: GSI NER landslide inventory ({metadata['total_gsi_events']} events)\n")
        f.write(f"- **Terrain rasters**: SRTM GL1 30m DEM derivatives\n")
        f.write(f"- **Terrain coverage**: {metadata['terrain_coverage']}\n\n")

        f.write("## 3. Training Data Construction\n\n")
        f.write(f"- Total GSI events: {metadata['total_gsi_events']}\n")
        f.write(f"- Events excluded (outside current terrain coverage): {metadata['events_excluded_no_terrain']}\n")
        f.write(f"- Positive samples used: {metadata['positive_count']}\n")
        f.write(f"- Negative samples generated: {metadata['negative_count']}\n")
        f.write(f"- Total training rows: {metadata['training_row_count']}\n\n")

        f.write("## 4. Positive/Negative Sampling\n\n")
        f.write("- **Positive (label=1)**: Historical GSI landslide locations with valid terrain features\n")
        f.write(f"- **Negative (label=0)**: Random background points at minimum {MIN_DISTANCE_DEG}° (~1.1 km) from any landslide\n")
        f.write(f"- **Ratio**: {NEGATIVE_RATIO} negatives per positive\n")
        f.write("- Only points with complete terrain feature extraction (no NoData) are used\n\n")

        f.write("## 5. Spatial Split\n\n")
        f.write(f"- **Method**: {metadata['split_method']}\n")
        f.write("- Points are assigned to 0.5° grid blocks; entire blocks are allocated to train or test\n")
        f.write("- This prevents spatial autocorrelation leakage between train and test sets\n")
        f.write(f"- Train rows: {metadata['train_count']}\n")
        f.write(f"- Test rows: {metadata['test_count']}\n\n")

        f.write("## 6. Features\n\n")
        f.write("| Feature | Description |\n")
        f.write("|---|---|\n")
        f.write("| elevation | Elevation in meters (SRTM GL1) |\n")
        f.write("| slope | Slope angle in degrees |\n")
        f.write("| aspect | Slope aspect in degrees (0-360, N=0) |\n")
        f.write("| terrain_ruggedness | Terrain Ruggedness Index (TRI) |\n\n")

        f.write("## 7. Model Comparison\n\n")
        f.write("| Metric | RandomForest | XGBoost |\n")
        f.write("|---|---|---|\n")
        for metric in ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc", "brier_score"]:
            rf_val = results["RandomForest"][metric]
            xgb_val = results["XGBoost"][metric]
            f.write(f"| {metric} | {rf_val:.4f} | {xgb_val:.4f} |\n")
        f.write(f"\n**Selected model**: {metadata['model_type']}\n\n")

        f.write("## 8. Evaluation Metrics (Best Model)\n\n")
        m = metadata["evaluation_metrics"]
        f.write(f"- Accuracy: {m['accuracy']:.4f}\n")
        f.write(f"- Precision: {m['precision']:.4f}\n")
        f.write(f"- Recall: {m['recall']:.4f}\n")
        f.write(f"- F1: {m['f1']:.4f}\n")
        f.write(f"- ROC-AUC: {m['roc_auc']:.4f}\n")
        f.write(f"- PR-AUC: {m['pr_auc']:.4f}\n")
        f.write(f"- Brier Score: {m['brier_score']:.4f}\n\n")

        f.write("## 9. Limitations\n\n")
        f.write("- Terrain coverage is partial (24/57 required SRTM cells downloaded)\n")
        f.write("- Model trained only on areas where terrain data is available\n")
        f.write("- Northern NER (Arunachal Pradesh, parts of Assam/Nagaland above 26°N) are not covered\n")
        f.write("- No rainfall, soil moisture, or land cover features included\n")
        f.write("- Negative sampling is random background, not confirmed stable sites\n")
        f.write("- GSI inventory may have spatial reporting bias toward accessible areas\n\n")

        f.write("## 10. Why This is a Baseline Susceptibility Model\n\n")
        f.write("This model captures **static terrain predisposition** to landslides. It does not\n")
        f.write("account for dynamic triggering factors (rainfall, seismicity, land-use change).\n")
        f.write("It provides a spatial prior for where landslides are more likely given terrain alone.\n\n")

        f.write("## 11. NOT an Official Emergency Warning\n\n")
        f.write("**This model is for research purposes only.** It is NOT:\n")
        f.write("- An official early warning system\n")
        f.write("- A replacement for GSI/NDMA/IMD hazard assessments\n")
        f.write("- Suitable for evacuation decisions without expert review\n")
        f.write("- Validated against real-time event data\n\n")

        f.write("## 12. Why Rainfall is Not Yet Included\n\n")
        f.write("The IMERG rainfall data available in this project is a 7-day test extract, not a\n")
        f.write("multi-year historical rainfall record. Using it as a training feature would:\n")
        f.write("- Misrepresent temporal rainfall patterns\n")
        f.write("- Create a model that cannot generalize beyond the test period\n")
        f.write("- Require antecedent rainfall computation over months/years of data\n\n")
        f.write("Rainfall will be incorporated in the dynamic risk model once multi-year IMERG\n")
        f.write("data is acquired and antecedent rainfall indices are computed.\n")

    print(f"  Report saved: {report_path}")


def task9_inference_script():
    print("\n" + "=" * 60)
    print("TASK 9: INFERENCE SCRIPT")
    print("=" * 60)

    inference_dir = PROJECT_ROOT / "ml" / "inference"
    inference_dir.mkdir(parents=True, exist_ok=True)

    script_content = '''"""
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
        print(f"Using default: {lat}, {lon}\\n")

    result = predict_susceptibility(lat, lon)
    print(json.dumps(result, indent=2))
    close()
'''

    script_path = inference_dir / "predict_susceptibility.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"  Inference script: {script_path}")


def task10_tests():
    print("\n" + "=" * 60)
    print("TASK 10: TESTS")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0
    failures = []

    def check(name, condition, detail=""):
        nonlocal tests_passed, tests_failed
        if condition:
            tests_passed += 1
            print(f"  PASS: {name}")
        else:
            tests_failed += 1
            failures.append(f"{name}: {detail}")
            print(f"  FAIL: {name} - {detail}")

    # Test feature extraction
    import rasterio
    ds = rasterio.open(TERRAIN_DIR / "slope.tif")
    val = extract_raster_value(ds, 93.0, 25.0)
    check("Feature extraction returns float", isinstance(val, float) and not np.isnan(val), str(val))
    ds.close()

    # Test extraction at invalid location
    ds = rasterio.open(TERRAIN_DIR / "slope.tif")
    val = extract_raster_value(ds, 0.0, 0.0)
    check("Invalid location returns NaN", np.isnan(val))
    ds.close()

    # Test model loading
    model = joblib.load(ARTIFACTS_DIR / "terrain_susceptibility_model.joblib")
    check("Model loads successfully", model is not None)

    # Test prediction
    X_test = np.array([[500.0, 25.0, 180.0, 10.0]])
    prob = model.predict_proba(X_test)
    check("Model predicts probabilities", prob.shape == (1, 2))
    check("Probabilities sum to 1", abs(prob.sum() - 1.0) < 0.001)

    # Test inference script
    sys.path.insert(0, str(PROJECT_ROOT / "ml" / "inference"))
    from predict_susceptibility import predict_susceptibility, close

    result = predict_susceptibility(25.0, 93.0)
    check("Inference returns dict", isinstance(result, dict))
    check("Inference has score", "susceptibility_score" in result)
    check("Score is numeric", isinstance(result.get("susceptibility_score"), (int, float)))

    # Test invalid coordinates
    result_invalid = predict_susceptibility(200.0, 93.0)
    check("Invalid coords handled", result_invalid["susceptibility_level"] == "INVALID_COORDINATES")

    # Test location outside raster
    result_outside = predict_susceptibility(10.0, 10.0)
    check("Outside raster returns NO_DATA", result_outside["susceptibility_level"] == "NO_DATA")

    # Test deterministic sampling
    rng1 = np.random.default_rng(SEED)
    rng2 = np.random.default_rng(SEED)
    check("Deterministic RNG", np.all(rng1.uniform(0, 1, 10) == rng2.uniform(0, 1, 10)))

    # Test dataset exists
    check("Training dataset exists", (ML_DATA_DIR / "terrain_susceptibility_dataset.parquet").exists())
    check("Training CSV exists", (ML_DATA_DIR / "terrain_susceptibility_dataset.csv").exists())

    close()

    print(f"\n  Results: {tests_passed} passed, {tests_failed} failed")
    return tests_passed, tests_failed, failures


def main():
    print("NER-LDI TERRAIN SUSCEPTIBILITY MODEL TRAINING")
    print("=" * 60)
    print(f"Started: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    # Task 1
    df_train, n_positive, n_negative, total_gsi, excluded = task1_build_training_data()

    # Task 2
    train_df, test_df = task2_spatial_split(df_train)

    # Task 3
    models, X_train, y_train, X_test, y_test = task3_train_models(train_df, test_df)

    # Task 4
    results = task4_evaluate(models, X_test, y_test)

    # Task 5
    best_name = task5_select_model(results)

    # Task 6
    metadata = task6_save_model(models, best_name, results, train_df, test_df,
                                n_positive, n_negative, total_gsi, excluded)

    # Task 7
    importances = task7_feature_importance(models, best_name, results, y_test)

    # Task 8
    task8_report(metadata, results, importances)

    # Task 9
    task9_inference_script()

    # Task 10
    passed, failed, failures = task10_tests()

    # Final output
    best_r = results[best_name]
    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    print(f"Model trained: YES")
    print(f"Model type: {best_name}")
    print(f"Training rows: {len(train_df) + len(test_df)}")
    print(f"Positive samples: {n_positive}")
    print(f"Negative samples: {n_negative}")
    print(f"Train rows: {len(train_df)}")
    print(f"Test rows: {len(test_df)}")
    print(f"ROC-AUC: {best_r['roc_auc']:.4f}")
    print(f"PR-AUC: {best_r['pr_auc']:.4f}")
    print(f"F1: {best_r['f1']:.4f}")
    print(f"Brier score: {best_r['brier_score']:.4f}")
    print(f"Best model: {best_name}")
    print(f"Terrain coverage: PARTIAL")
    print(f"Final status: {'PASS' if failed == 0 else 'FAIL'}")
    print(f"\nBaseline model trained on available validated terrain coverage only.")


if __name__ == "__main__":
    main()
