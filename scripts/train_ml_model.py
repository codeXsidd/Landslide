"""
NER-SAGE — Machine Learning Training Script
Generates a synthetic dataset of landslides, trains XGBoost, calibrates,
calculates SHAP values, and saves artifacts for the backend.
"""

import os
import sys

import joblib
import numpy as np
import pandas as pd

try:
    import xgboost as xgb
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import average_precision_score, roc_auc_score
    from sklearn.model_selection import train_test_split
except ImportError as e:
    print(f"Missing ML dependencies: {e}")
    print("Run: pip install xgboost scikit-learn pandas shap")
    sys.exit(1)

def generate_training_data(n_samples=5000) -> pd.DataFrame:
    """Generates synthetic historical landslide data for training."""
    np.random.seed(42)

    # Generate features
    slope = np.random.normal(25, 10, n_samples)
    slope = np.clip(slope, 0, 70)

    elevation = np.random.normal(1500, 500, n_samples)
    aspect = np.random.uniform(0, 360, n_samples)

    rain_24h = np.random.exponential(30, n_samples)
    rain_72h = np.random.exponential(70, n_samples)

    api_score = rain_24h + (0.5 * rain_72h)

    soil_type = np.random.randint(0, 4, n_samples)
    dist_fault = np.random.exponential(15, n_samples)

    df = pd.DataFrame({
        "slope_deg": slope,
        "elevation_m": elevation,
        "aspect_deg": aspect,
        "rainfall_24h": rain_24h,
        "rainfall_72h": rain_72h,
        "api_score": api_score,
        "soil_type_idx": soil_type,
        "distance_to_fault_km": dist_fault
    })

    # Generate target based on logistic function
    logit = (
        -4.0
        + (df["slope_deg"] * 0.08)
        + (df["api_score"] * 0.015)
        - (df["distance_to_fault_km"] * 0.1)
        + (df["soil_type_idx"] * 0.3)
    )

    # Add noise
    logit += np.random.normal(0, 1, n_samples)

    prob = 1 / (1 + np.exp(-logit))
    df["landslide_occurred"] = (prob > 0.5).astype(int)

    return df

def train_and_save_models():
    print("1. Generating synthetic dataset (5000 samples)...")
    df = generate_training_data()

    X = df.drop("landslide_occurred", axis=1)  # noqa: N806
    y = df["landslide_occurred"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # noqa: N806

    print("2. Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        objective="binary:logistic",
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    pr_auc = average_precision_score(y_test, y_pred_proba)
    print(f"   Evaluation: ROC-AUC={roc_auc:.3f}, PR-AUC={pr_auc:.3f}")

    print("3. Calibrating probabilities (Isotonic Regression)...")
    calibrator = CalibratedClassifierCV(model, cv="prefit", method="isotonic")
    calibrator.fit(X_test, y_test)

    print("4. Skipping SHAP explainer (C++ build tool dependency removed for Windows)...")

    print("5. Saving artifacts...")
    artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    joblib.dump(model, os.path.join(artifacts_dir, "xgb_model.pkl"))
    joblib.dump(calibrator, os.path.join(artifacts_dir, "calibrator.pkl"))

    print("ML Pipeline complete. Models saved to ml/artifacts/")

if __name__ == "__main__":
    train_and_save_models()
