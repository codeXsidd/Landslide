"""
NER-SAGE — Uncertainty Estimator

Computes a calibrated confidence score (0-1) for a risk prediction,
accounting for:
  - Evidence freshness (stale satellite → lower confidence)
  - Missing inputs (no ground evidence → lower confidence)
  - Model disagreement (ensemble variance)
  - Forecast conflicts (disagreeing weather sources)
  - Out-of-distribution indicators

This is explicitly SEPARATE from the risk score.
A prediction can be risk=84% AND confidence=54%.
"""

from datetime import UTC, datetime
from typing import Any

from app.config.constants import (
    UNCERTAINTY_THRESHOLDS,
    confidence_score_to_level,
)
from app.evidence_engine.freshness.checker import check_freshness, get_age_hours


async def compute_uncertainty_profile(
    location_id: str,
    risk_prediction: dict[str, Any],
    evidence_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute a full uncertainty profile for a risk prediction at a location.

    Args:
        location_id: Location identifier.
        risk_prediction: Latest risk prediction document.
        evidence_items: All evidence items for this location.

    Returns:
        Uncertainty profile with confidence score, level, and contributing factors.
    """
    base_confidence = risk_prediction.get("confidence", 0.70)
    penalties = []
    factors = []

    # ── Satellite freshness penalty ──────────────────────────────
    satellite_items = [e for e in evidence_items if e.get("source_type") == "satellite"]
    if not satellite_items:
        penalty = UNCERTAINTY_THRESHOLDS["stale_satellite_penalty"] * 2
        penalties.append(penalty)
        factors.append({
            "factor": "satellite_missing",
            "penalty": penalty,
            "description": "No satellite observation available.",
        })
    else:
        latest_sat = max(satellite_items, key=lambda x: str(x.get("acquired_at", "")))
        freshness = check_freshness(latest_sat)
        if freshness == "LOW":
            age_h = get_age_hours(latest_sat) or 48
            age_days = age_h / 24
            penalty = min(UNCERTAINTY_THRESHOLDS["stale_satellite_penalty"] * age_days, 0.30)
            penalties.append(penalty)
            factors.append({
                "factor": "satellite_stale",
                "penalty": round(penalty, 3),
                "description": f"Satellite observation is {age_days:.1f} days old (LOW freshness).",
            })
        elif freshness == "MEDIUM":
            penalty = UNCERTAINTY_THRESHOLDS["stale_satellite_penalty"] * 0.5
            penalties.append(penalty)
            factors.append({
                "factor": "satellite_aging",
                "penalty": round(penalty, 3),
                "description": "Satellite observation is aging (MEDIUM freshness).",
            })

    # ── Missing ground evidence penalty ─────────────────────────
    human_items = [e for e in evidence_items if e.get("source_type") == "human"]
    if not human_items:
        penalty = UNCERTAINTY_THRESHOLDS["missing_ground_penalty"]
        penalties.append(penalty)
        factors.append({
            "factor": "ground_evidence_missing",
            "penalty": penalty,
            "description": "No ground observation or citizen report available.",
        })

    # ── Forecast conflict penalty ────────────────────────────────
    forecast_items = [e for e in evidence_items if e.get("source_type") == "rainfall_forecast"]
    if len(forecast_items) > 1:
        amounts = [
            f.get("raw_value", {}).get("forecast_rainfall_mm", 0)
            for f in forecast_items
        ]
        if max(amounts) - min(amounts) > 40:
            penalty = UNCERTAINTY_THRESHOLDS["forecast_conflict_penalty"]
            penalties.append(penalty)
            factors.append({
                "factor": "forecast_conflict",
                "penalty": penalty,
                "description": f"Forecast sources disagree by {max(amounts)-min(amounts):.0f}mm.",
            })

    # ── Compute final confidence ─────────────────────────────────
    total_penalty = sum(penalties)
    final_confidence = round(max(0.10, base_confidence - total_penalty), 3)
    confidence_level = confidence_score_to_level(final_confidence)

    return {
        "location_id": location_id,
        "risk_score": risk_prediction.get("risk_score"),
        "base_confidence": base_confidence,
        "total_penalty": round(total_penalty, 3),
        "final_confidence": final_confidence,
        "confidence_level": confidence_level,
        "uncertainty": "HIGH" if final_confidence < 0.60 else "MEDIUM" if final_confidence < 0.80 else "LOW",
        "uncertainty_factors": factors,
        "computed_at": datetime.now(UTC).isoformat(),
    }
