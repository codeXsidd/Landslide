"""NER-LDI Uncertainty Engine - separates risk, confidence, and uncertainty."""
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
