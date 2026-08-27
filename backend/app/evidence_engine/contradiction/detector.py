"""
NER-SAGE — Contradiction Detector

Detects conflicts between evidence items at the same location.
A conflict exists when two sources give significantly different signals
about the same underlying phenomenon.

Example conflicts:
  - Rainfall=HIGH + Satellite showing LOW deformation/change
  - Citizen reports road OPEN + High risk prediction
  - Forecast=HEAVY + Historical data suggesting LOW susceptibility in this season
"""

from typing import Any

CONFLICT_RULES = [
    {
        "id": "rainfall_vs_satellite",
        "name": "Rainfall signal vs Satellite change detection",
        "source_a_type": "rainfall",
        "source_b_type": "satellite",
        "condition": lambda a, b: (
            a.get("raw_value", {}).get("intensity") in ("HEAVY", "VERY_HEAVY", "EXTREMELY_HEAVY")
            and not b.get("change_detected", True)
            and b.get("freshness") == "HIGH"  # only conflict if satellite is fresh
        ),
        "severity": "MEDIUM",
        "description": (
            "Rainfall intensity is HIGH but recent satellite shows no significant change. "
            "This may indicate the satellite observation preceded the current rainfall event."
        ),
    },
    {
        "id": "citizen_vs_risk",
        "name": "Citizen report (OPEN) vs High ML risk",
        "source_a_type": "human",
        "source_b_type": "derived",
        "condition": lambda a, b: (
            "open" in str(a.get("description", "")).lower()
            and b.get("risk_score", 0) > 0.80
        ),
        "severity": "HIGH",
        "description": (
            "A citizen report states the road is open, but the ML model assigns high risk. "
            "Requires field verification to resolve."
        ),
    },
    {
        "id": "forecast_vs_observation",
        "name": "Forecast vs Current observation mismatch",
        "source_a_type": "rainfall_forecast",
        "source_b_type": "rainfall",
        "condition": lambda a, b: (
            abs(
                a.get("forecast_rainfall_mm", 0) - b.get("raw_value", {}).get("rainfall_mm", 0)
            ) > 50
        ),
        "severity": "MEDIUM",
        "description": "Forecast rainfall differs significantly from current observation.",
    },
]


async def detect_contradictions(
    location_id: str, evidence_items: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Detect conflicting evidence pairs at a location.

    Args:
        location_id: Location identifier.
        evidence_items: List of evidence item dicts.

    Returns:
        Dict with conflict list, overall status, and resolution suggestions.
    """
    conflicts = []

    for rule in CONFLICT_RULES:
        items_a = [e for e in evidence_items if e.get("source_type") == rule["source_a_type"]]
        items_b = [e for e in evidence_items if e.get("source_type") == rule["source_b_type"]]

        for a in items_a:
            for b in items_b:
                try:
                    if rule["condition"](a, b):
                        conflicts.append({
                            "conflict_id": rule["id"],
                            "name": rule["name"],
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "evidence_a_id": str(a.get("_id", "unknown")),
                            "evidence_b_id": str(b.get("_id", "unknown")),
                            "source_a": rule["source_a_type"],
                            "source_b": rule["source_b_type"],
                        })
                except Exception:
                    continue  # Skip rules that can't be evaluated

    overall_status = "CONFLICTING" if conflicts else "CONSISTENT"

    return {
        "location_id": location_id,
        "overall_status": overall_status,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "recommendation": (
            "Resolve conflicting evidence before high-confidence decision."
            if conflicts else "Evidence is consistent."
        ),
    }
