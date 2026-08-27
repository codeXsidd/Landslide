"""
NER-SAGE — Feature Explainability (SHAP)
Extracts the driving factors behind a specific risk prediction.
"""


import pandas as pd

# Feature name mapping for human-readable output
FEATURE_NAMES = {
    "slope_deg": "steep terrain slope",
    "elevation_m": "high elevation",
    "rainfall_24h": "heavy 24h rainfall",
    "rainfall_72h": "prolonged rainfall",
    "api_score": "high antecedent moisture",
    "soil_type_idx": "vulnerable soil composition",
    "distance_to_fault_km": "proximity to fault line",
}

def explain_prediction(features_df: pd.DataFrame, model, explainer=None) -> list[str]:
    """
    Returns the top 2 driving factors for a prediction.
    In production, uses SHAP values. This implementation falls back to heuristics
    if the SHAP explainer isn't provided (e.g., during fast inference).
    """
    try:
        if explainer is not None:
            # Use SHAP values
            shap_values = explainer.shap_values(features_df)
            # shap_values for a single instance is a 1D array
            contributions = shap_values[0] if isinstance(shap_values, list) else shap_values

            # Map features to contributions
            feat_contribs = []
            for i, col in enumerate(features_df.columns):
                feat_contribs.append((col, contributions[0][i] if len(contributions.shape) > 1 else contributions[i]))

            # Sort by absolute impact
            feat_contribs.sort(key=lambda x: abs(x[1]), reverse=True)

            # Return top 2 factors driving the risk UP (positive contribution)
            top_factors = [FEATURE_NAMES.get(f[0], f[0]) for f in feat_contribs if f[1] > 0][:2]
            if top_factors:
                return top_factors
    except Exception as e:
        import logging
        logging.warning(f"SHAP explanation failed: {e}")

    # Fallback heuristic: look at standardized values
    # We'll just check raw values against known high-risk thresholds
    factors = []
    row = features_df.iloc[0]

    if row.get("rainfall_24h", 0) > 100 or row.get("api_score", 0) > 150:
        factors.append(FEATURE_NAMES["rainfall_24h"])
    if row.get("slope_deg", 0) > 30:
        factors.append(FEATURE_NAMES["slope_deg"])
    if row.get("distance_to_fault_km", 10) < 2.0:
        factors.append(FEATURE_NAMES["distance_to_fault_km"])

    if not factors:
        factors = ["historical susceptibility"]

    return factors[:2]
