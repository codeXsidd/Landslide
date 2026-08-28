"""NER-LDI Next-Best-Evidence Engine - recommends most valuable observation to acquire."""
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
        urgency = "CRITICAL" if risk_score > 0.75 and uncertainty > 0.4 else                   "HIGH" if risk_score > 0.5 else "MEDIUM" if risk_score > 0.25 else "LOW"

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
