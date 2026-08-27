"""
NER-LDI MVP — Next-Best-Evidence Service
Wraps the core engine and exposes a clean service interface.

Returns:
  recommended_observation, reason, expected_information_value, cost, priority
"""

from datetime import UTC, datetime
from typing import Any


# Observable actions the system can recommend
CANDIDATE_OBSERVATIONS = [
    {
        "observation_type": "ROAD_VERIFICATION",
        "recommended_observation": "Road condition verification",
        "description": "Dispatch field officer or trusted vehicle to verify current road status.",
        "base_information_value": 0.38,
        "base_reliability": 0.92,
        "cost": "MEDIUM",
        "cost_score": 0.40,
        "requires_human_action": True,
    },
    {
        "observation_type": "FIELD_PHOTOGRAPH",
        "recommended_observation": "Field photograph from local source",
        "description": "Request geotagged photograph from a person near the location.",
        "base_information_value": 0.25,
        "base_reliability": 0.70,
        "cost": "LOW",
        "cost_score": 0.10,
        "requires_human_action": True,
    },
    {
        "observation_type": "SATELLITE_REFRESH",
        "recommended_observation": "Satellite imagery refresh",
        "description": "Request fresh Sentinel-1 SAR or Sentinel-2 optical acquisition.",
        "base_information_value": 0.30,
        "base_reliability": 0.90,
        "cost": "MEDIUM",
        "cost_score": 0.30,
        "requires_human_action": False,
    },
    {
        "observation_type": "OFFICIAL_ROAD_STATUS",
        "recommended_observation": "Official road status confirmation",
        "description": "Contact PWD/NHAI for official road status update.",
        "base_information_value": 0.35,
        "base_reliability": 0.95,
        "cost": "LOW",
        "cost_score": 0.15,
        "requires_human_action": True,
    },
    {
        "observation_type": "HISTORICAL_COMPARISON",
        "recommended_observation": "Historical event comparison",
        "description": "Compare current conditions to historical landslide events at this location.",
        "base_information_value": 0.12,
        "base_reliability": 0.80,
        "cost": "VERY_LOW",
        "cost_score": 0.05,
        "requires_human_action": False,
    },
]


def _compute_priority(score: float, risk_score: float) -> str:
    combined = (score + risk_score) / 2
    if combined >= 0.8:
        return "CRITICAL"
    if combined >= 0.6:
        return "HIGH"
    if combined >= 0.4:
        return "MEDIUM"
    return "LOW"


async def compute_next_best_evidence(
    location_id: str,
    risk_score: float,
    confidence: float,
    evidence_summary: dict[str, Any],
    impact_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Compute the recommended next observation to reduce decision uncertainty.

    Information Value = (base_IV × decision_importance × reliability) / cost_score
    """
    missing_types = set(evidence_summary.get("missing_types", []))
    stale_types = set(
        e.get("evidence_type") for e in evidence_summary.get("items", [])
        if e.get("information_state") == "STALE"
    )
    has_conflict = evidence_summary.get("has_conflict", False)

    # Decision importance: how consequential is this decision?
    isolation_prob = impact_data.get("village_isolation_probability", 0.0)
    hospital_degraded = impact_data.get("hospital_accessibility_degraded", False)
    affected_pop = impact_data.get("population_exposed", 0)

    decision_importance = risk_score
    decision_importance += isolation_prob * 0.20
    if hospital_degraded:
        decision_importance += 0.20
    if affected_pop > 1000:
        decision_importance += 0.10
    if has_conflict:
        decision_importance += 0.15  # Conflicts increase importance of clarifying evidence
    decision_importance = min(decision_importance, 1.0)

    scored = []
    for obs in CANDIDATE_OBSERVATIONS:
        iv = obs["base_information_value"]
        reliability = obs["base_reliability"]
        cost = max(obs["cost_score"], 0.01)

        # Boost if this observation fills a gap or resolves staleness
        otype = obs["observation_type"]
        if otype == "ROAD_VERIFICATION" and ("road_inspection" in missing_types or "road_inspection" in stale_types):
            iv *= 1.50
        if otype == "SATELLITE_REFRESH" and "satellite" in stale_types:
            iv *= 1.35
        if otype == "FIELD_PHOTOGRAPH" and "road_inspection" in missing_types:
            iv *= 1.25
        if otype == "OFFICIAL_ROAD_STATUS" and has_conflict:
            iv *= 1.60  # Very valuable when evidence conflicts
        if otype == "HISTORICAL_COMPARISON" and confidence < 0.5:
            iv *= 1.20

        # When uncertainty is low, additional evidence adds less value
        uncertainty_factor = 1.0 - confidence
        iv_adjusted = iv * uncertainty_factor

        expected_iv = (iv_adjusted * decision_importance * reliability) / cost

        scored.append({
            **obs,
            "expected_information_value": round(expected_iv, 4),
            "adjusted_iv": round(iv_adjusted, 3),
            "decision_importance": round(decision_importance, 3),
            "priority": _compute_priority(expected_iv / max(expected_iv + 0.01, 1), risk_score),
        })

    scored.sort(key=lambda x: x["expected_information_value"], reverse=True)
    top = scored[0]

    reason = (
        f"This observation has the highest expected information value ({top['expected_information_value']:.3f}) "
        f"given current risk ({risk_score:.0%}), confidence ({confidence:.0%}), and "
        f"{'conflicting' if has_conflict else 'missing/stale'} evidence."
    )

    if missing_types:
        reason += f" Missing evidence: {', '.join(missing_types)}."

    return {
        "location_id": location_id,
        "recommended_observation": top["recommended_observation"],
        "observation_type": top["observation_type"],
        "reason": reason,
        "expected_information_value": top["expected_information_value"],
        "cost": top["cost"],
        "priority": top["priority"],
        "requires_human_action": top["requires_human_action"],
        "description": top["description"],
        "all_candidates": scored,
        "decision_importance": round(decision_importance, 3),
        "computed_at": datetime.now(UTC).isoformat(),
        "note": "This recommendation requires human judgement before acting.",
    }
