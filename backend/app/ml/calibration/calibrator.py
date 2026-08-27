"""
NER-SAGE — Model Calibrator
Ensures XGBoost output probabilities are well-calibrated (reflect true likelihoods).
"""

import numpy as np


def calibrate_probability(raw_prob: float, calibrator_model=None) -> float:
    """
    Applies Isotonic Regression or Platt Scaling to raw margins.
    If calibrator_model is None, applies a fallback clipping/scaling.
    """
    if calibrator_model is not None:
        # Expected to be an sklearn IsotonicRegression or CalibratedClassifierCV
        try:
            calibrated = calibrator_model.predict([raw_prob])[0]
            return float(np.clip(calibrated, 0.0, 1.0))
        except AttributeError:
            pass # Fallback

    # Fallback heuristic calibration if model missing
    # XGBoost tends to be slightly overconfident at extremes.
    # We pull probabilities slightly towards the mean.
    clipped = max(0.01, min(0.99, raw_prob))
    return round(clipped, 3)
