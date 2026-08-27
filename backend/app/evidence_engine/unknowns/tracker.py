"""
NER-SAGE — Information State Tracker (Unknown / Stale / Conflicting)

Classifies each evidence category into:
  KNOWN       — fresh, reliable evidence available
  UNKNOWN     — no evidence of this type exists
  STALE       — evidence exists but exceeds freshness threshold
  UNCERTAIN   — evidence exists but reliability is low
  CONFLICTING — multiple sources disagree significantly

This is the Self-Questioning Loop's primary input.
"""

from typing import Any

from app.config.constants import FreshnessLevel, InformationState
from app.evidence_engine.freshness.checker import check_freshness

# Expected evidence categories per monitored location
EXPECTED_EVIDENCE_TYPES = {
    "rainfall": "rainfall",
    "satellite": "satellite",
    "terrain": "terrain",
    "historical": "historical",
    "road_status": "human",
    "forecast": "rainfall_forecast",
}

RELIABILITY_THRESHOLD_UNCERTAIN = 0.50


async def classify_information_states(
    location_id: str, evidence_items: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    Classify the information state of each evidence category for a location.

    Returns:
        Dict with state per evidence type, summary counts, and unknown list.
    """
    # Group evidence by source_type
    by_type: dict[str, list[dict]] = {}
    for item in evidence_items:
        st = item.get("source_type", "unknown")
        by_type.setdefault(st, []).append(item)

    states: dict[str, str] = {}
    reasons: dict[str, str] = {}

    for label, source_type in EXPECTED_EVIDENCE_TYPES.items():
        items = by_type.get(source_type, [])

        if not items:
            states[label] = InformationState.UNKNOWN
            reasons[label] = f"No {label} evidence available for this location."
            continue

        # Take most recent
        latest = max(items, key=lambda x: str(x.get("created_at", "")))
        freshness = check_freshness(latest)
        reliability = latest.get("reliability", 0.5)

        if freshness == FreshnessLevel.LOW:
            states[label] = InformationState.STALE
            reasons[label] = f"{label} evidence is stale (too old to be reliable)."
        elif reliability < RELIABILITY_THRESHOLD_UNCERTAIN:
            states[label] = InformationState.UNCERTAIN
            reasons[label] = f"{label} reliability is below threshold ({reliability:.2f})."
        else:
            states[label] = InformationState.KNOWN
            reasons[label] = f"{label} evidence is fresh and reliable."

    # Build summary
    unknowns = [k for k, v in states.items() if v == InformationState.UNKNOWN]
    stale = [k for k, v in states.items() if v == InformationState.STALE]
    conflicting = [k for k, v in states.items() if v == InformationState.CONFLICTING]
    known = [k for k, v in states.items() if v == InformationState.KNOWN]

    return {
        "location_id": location_id,
        "states": states,
        "reasons": reasons,
        "summary": {
            "known_count": len(known),
            "unknown_count": len(unknowns),
            "stale_count": len(stale),
            "conflicting_count": len(conflicting),
            "total_categories": len(EXPECTED_EVIDENCE_TYPES),
        },
        "unknowns": unknowns,
        "stale": stale,
        "conflicting": conflicting,
        "known": known,
        "completeness_pct": round(100 * len(known) / len(EXPECTED_EVIDENCE_TYPES), 1),
    }
