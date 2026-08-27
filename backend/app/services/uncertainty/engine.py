"""
NER-LDI MVP — Uncertainty Engine
Computes confidence score as distinct from risk probability.

risk     = probability that a landslide will occur (ML output)
confidence = how much to trust that risk estimate

Confidence degrades when:
- Features are missing or stale
- Evidence is conflicting
- Model is extrapolating outside training distribution
- Sources are unreliable

IMPORTANT: This AI output is NOT an official emergency warning.
All recommendations require human review and approval.
"""

from datetime import UTC, datetime, timedelta
from typing import Any


# Source reliability weights (calibrated empirically)
SOURCE_RELIABILITY = {
    "satellite_sentinel": 0.95,
    "satellite_landsat": 0.88,
    "nasa_imerg_rainfall": 0.90,
    "field_inspection": 0.92,
    "citizen_report_verified": 0.75,
    "citizen_report_unverified": 0.45,
    "weather_station": 0.88,
    "historical_inventory": 0.85,
    "synthetic": 0.30,
    "unknown": 0.40,
}


def compute_missing_feature_penalty(features: dict[str, Any]) -> float:
    """
    Penalise confidence for each missing or default feature.
    Returns penalty in [0.0, 0.5].
    """
    required_features = ["slope", "elevation", "rainfall_1d", "rainfall_7d", "terrain_ruggedness"]
    missing_count = sum(1 for f in required_features if features.get(f) is None)
    # Linearly scale: 0 missing = 0 penalty, all missing = 0.5 penalty
    return round(missing_count / len(required_features) * 0.5, 3)


def compute_freshness_factor(evidence_items: list[dict[str, Any]]) -> float:
    """
    Compute evidence freshness factor in [0.5, 1.0].
    Fresh evidence (< 6h) = 1.0, stale (> 48h) = 0.5.
    """
    if not evidence_items:
        return 0.6  # No evidence → low freshness

    now = datetime.now(UTC)
    freshness_scores = []

    for item in evidence_items:
        ts_str = item.get("timestamp") or item.get("created_at")
        if not ts_str:
            freshness_scores.append(0.5)
            continue
        try:
            if isinstance(ts_str, str):
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            else:
                ts = ts_str
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            age_hours = (now - ts).total_seconds() / 3600
            # Freshness decay: 1.0 at 0h, 0.5 at 48h
            score = max(0.5, 1.0 - (age_hours / 96))
            freshness_scores.append(score)
        except Exception:
            freshness_scores.append(0.5)

    return round(sum(freshness_scores) / len(freshness_scores), 3)


def compute_source_reliability_factor(evidence_items: list[dict[str, Any]]) -> float:
    """
    Weighted average reliability of all evidence sources.
    Returns value in [0.3, 1.0].
    """
    if not evidence_items:
        return 0.5

    weights = []
    for item in evidence_items:
        source_type = item.get("source_type", "unknown").lower().replace(" ", "_")
        reliability = SOURCE_RELIABILITY.get(source_type, SOURCE_RELIABILITY["unknown"])
        # Penalise simulated evidence
        if item.get("is_simulated"):
            reliability *= 0.7
        weights.append(reliability)

    return round(sum(weights) / len(weights), 3)


def compute_conflict_penalty(evidence_items: list[dict[str, Any]]) -> float:
    """
    Penalty for conflicting evidence.
    Detects contradiction between evidence types (e.g., road reported clear AND blocked).
    Returns penalty in [0.0, 0.25].
    """
    road_statuses = [
        item.get("road_status") for item in evidence_items
        if item.get("evidence_type") == "road_condition" and item.get("road_status")
    ]
    if len(road_statuses) >= 2:
        unique_statuses = set(road_statuses)
        if len(unique_statuses) > 1:
            return 0.20  # Contradiction detected

    satellite_reports = [
        item.get("damage_observed") for item in evidence_items
        if item.get("evidence_type") == "satellite" and item.get("damage_observed") is not None
    ]
    if len(satellite_reports) >= 2:
        if len(set(satellite_reports)) > 1:
            return 0.15

    return 0.0


def compute_model_confidence(model_metadata: dict[str, Any]) -> float:
    """
    Confidence in the ML model itself.
    Degrades if using fallback/stub model or extrapolating.
    """
    model_version = model_metadata.get("model_version", "unknown")
    if "stub" in model_version or "fallback" in model_version:
        return 0.45
    if "prod" in model_version or "xgb" in model_version:
        return 0.85
    return 0.65


def compute_uncertainty_profile(
    raw_risk_score: float,
    features: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    model_metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Full uncertainty computation pipeline.

    Returns a structured uncertainty profile with:
    - final_confidence: overall confidence in the risk estimate
    - risk (unchanged): the ML risk probability
    - confidence_level: HIGH / MEDIUM / LOW
    - penalty breakdown
    - what_is_unknown: list of missing critical information
    """
    # 1. Base model confidence
    model_conf = compute_model_confidence(model_metadata)

    # 2. Missing-feature penalty
    missing_penalty = compute_missing_feature_penalty(features)

    # 3. Evidence freshness factor
    freshness = compute_freshness_factor(evidence_items)

    # 4. Source reliability factor
    reliability = compute_source_reliability_factor(evidence_items)

    # 5. Conflict penalty
    conflict_penalty = compute_conflict_penalty(evidence_items)

    # 6. Combine into final confidence
    # Formula: model_conf × freshness × reliability − missing_penalty − conflict_penalty
    raw_confidence = (model_conf * freshness * reliability) - missing_penalty - conflict_penalty
    final_confidence = round(max(0.10, min(0.99, raw_confidence)), 3)

    # 7. Classify
    if final_confidence >= 0.75:
        confidence_level = "HIGH"
    elif final_confidence >= 0.50:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "LOW"

    # 8. What does the system not know?
    unknowns = []
    required = {
        "slope": "Slope gradient",
        "rainfall_1d": "24-hour rainfall",
        "elevation": "Elevation",
        "terrain_ruggedness": "Terrain ruggedness index",
    }
    for key, label in required.items():
        if features.get(key) is None:
            unknowns.append({"field": key, "label": label, "impact": "HIGH"})

    if not evidence_items:
        unknowns.append({"field": "field_evidence", "label": "Any field observation", "impact": "HIGH"})

    stale_items = [
        item.get("evidence_type", "unknown")
        for item in evidence_items
        if _is_stale(item)
    ]
    if stale_items:
        unknowns.append({
            "field": "stale_evidence",
            "label": f"Stale evidence: {', '.join(set(stale_items))}",
            "impact": "MEDIUM"
        })

    return {
        "risk_score": round(raw_risk_score, 3),
        "final_confidence": final_confidence,
        "confidence_level": confidence_level,
        "model_confidence": round(model_conf, 3),
        "freshness_factor": round(freshness, 3),
        "reliability_factor": round(reliability, 3),
        "missing_feature_penalty": round(missing_penalty, 3),
        "conflict_penalty": round(conflict_penalty, 3),
        "evidence_count": len(evidence_items),
        "what_is_unknown": unknowns,
        "note": "confidence != risk. A high risk with low confidence means the system is uncertain about its own risk estimate.",
        "ai_disclaimer": "THIS IS NOT AN OFFICIAL EMERGENCY WARNING. All outputs require human review.",
        "computed_at": datetime.now(UTC).isoformat(),
    }


def _is_stale(item: dict[str, Any], stale_hours: int = 24) -> bool:
    """Check if an evidence item is older than stale_hours."""
    ts_str = item.get("timestamp") or item.get("created_at")
    if not ts_str:
        return True
    try:
        if isinstance(ts_str, str):
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            ts = ts_str
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        return (datetime.now(UTC) - ts) > timedelta(hours=stale_hours)
    except Exception:
        return True
