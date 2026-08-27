"""
NER-SAGE — Next-Best-Evidence Engine

The central operational engine of the Self-Questioning Decision Loop.

For each candidate evidence acquisition action, computes a Decision Value:

  DecisionValue = (UncertaintyReduction × DecisionImportance × Reliability)
                  / AcquisitionCost

The action with the highest Decision Value is the recommended next step.

Key insight: Decision Value ≠ Uncertainty Reduction alone.
An evidence item is most valuable if it reduces uncertainty about a
HIGH-CONSEQUENCE decision — not just about the model's probability estimate.
"""

from datetime import UTC, datetime
from typing import Any

# ── Candidate Evidence Actions ────────────────────────────────────

CANDIDATE_ACTIONS = [
    {
        "action_type": "INSPECT_ROAD",
        "title": "Verify road condition",
        "base_uncertainty_reduction": 0.35,
        "base_reliability": 0.90,
        "acquisition_cost": 0.40,
        "description": "Direct field inspection of the road to verify current condition.",
    },
    {
        "action_type": "REQUEST_FIELD_REPORT",
        "title": "Request citizen photograph",
        "base_uncertainty_reduction": 0.25,
        "base_reliability": 0.70,
        "acquisition_cost": 0.10,
        "description": "Request a photograph from a citizen near the location.",
    },
    {
        "action_type": "REQUEST_SATELLITE",
        "title": "Refresh satellite imagery",
        "base_uncertainty_reduction": 0.28,
        "base_reliability": 0.88,
        "acquisition_cost": 0.30,
        "description": "Request fresh Sentinel-1 or Sentinel-2 acquisition.",
    },
    {
        "action_type": "INCREASE_MONITORING",
        "title": "Compare historical event patterns",
        "base_uncertainty_reduction": 0.10,
        "base_reliability": 0.75,
        "acquisition_cost": 0.05,
        "description": "Compare current conditions to historical landslide events.",
    },
    {
        "action_type": "CONTINUE_MONITORING",
        "title": "Continue monitoring only",
        "base_uncertainty_reduction": 0.02,
        "base_reliability": 1.0,
        "acquisition_cost": 0.01,
        "description": "No additional evidence acquisition; continue passive monitoring.",
    },
]


def _compute_decision_importance(
    impact_data: dict[str, Any],
    risk_score: float,
) -> float:
    """
    Compute how consequential the decision is, given impact data.
    Higher consequence → higher decision importance.
    """
    base = risk_score  # Higher risk → more important to be accurate

    isolation_prob = impact_data.get("isolation_probability", 0.0)
    hospital_degraded = impact_data.get("hospital_access_degraded", False)
    affected_pop = impact_data.get("affected_population", 0)

    # Isolation and hospital access greatly increase importance
    base += isolation_prob * 0.20
    if hospital_degraded:
        base += 0.20
    if affected_pop > 1000:
        base += 0.10

    return min(base, 1.0)


async def compute_next_best_evidence(
    location_id: str,
    risk_prediction: dict[str, Any],
    uncertainty_profile: dict[str, Any],
    impact_data: dict[str, Any],
    information_states: dict[str, Any],
) -> dict[str, Any]:
    """
    Score all candidate evidence actions and return the ranked list.

    Returns:
        Dict with ranked candidates and the top recommendation.
    """
    risk_score = risk_prediction.get("risk_score", 0.5)
    uncertainty_profile.get("final_confidence", 0.5)
    decision_importance = _compute_decision_importance(impact_data, risk_score)

    # Adjust uncertainty reduction based on what's currently missing
    unknowns = set(information_states.get("unknowns", []))
    stale = set(information_states.get("stale", []))

    scored = []
    for candidate in CANDIDATE_ACTIONS:
        uncertainty_reduction = candidate["base_uncertainty_reduction"]
        reliability = candidate["base_reliability"]
        cost = max(candidate["acquisition_cost"], 0.01)

        # Bonus if this action addresses a known unknown
        action_type = candidate["action_type"]
        if action_type == "INSPECT_ROAD" and ("road_status" in unknowns or "road_status" in stale):
            uncertainty_reduction *= 1.40
        if action_type == "REQUEST_SATELLITE" and ("satellite" in stale):
            uncertainty_reduction *= 1.30
        if action_type == "REQUEST_FIELD_REPORT" and ("road_status" in unknowns):
            uncertainty_reduction *= 1.20

        decision_value = (uncertainty_reduction * decision_importance * reliability) / cost

        scored.append({
            **candidate,
            "uncertainty_reduction": round(uncertainty_reduction, 3),
            "decision_importance": round(decision_importance, 3),
            "decision_value": round(decision_value, 4),
            "addresses_unknowns": list(unknowns | stale),
        })

    # Sort by decision value descending
    scored.sort(key=lambda x: x["decision_value"], reverse=True)
    top = scored[0]

    consequence = (
        f"If this evidence is not gathered and the risk materialises, "
        f"the impact may include village isolation "
        f"(probability: {impact_data.get('isolation_probability', 0):.0%}) "
        f"and {'degraded' if impact_data.get('hospital_access_degraded') else 'maintained'} "
        f"hospital accessibility."
    )

    return {
        "location_id": location_id,
        "candidates": scored,
        "recommended_action": top["title"],
        "recommended_action_type": top["action_type"],
        "decision_value": top["decision_value"],
        "reason": (
            f"This action has the highest decision value ({top['decision_value']:.3f}) "
            f"because it addresses {'unknown' if unknowns else 'stale'} evidence "
            f"for a high-consequence location."
        ),
        "consequence_if_ignored": consequence,
        "computed_at": datetime.now(UTC).isoformat(),
    }
