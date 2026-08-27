"""
NER-SAGE — Evidence Reliability Scorer

Scores the reliability of an evidence item based on:
- Source type (satellite > official > citizen > derived)
- Image/data quality indicators
- Cross-source consistency
- Location/timestamp verification (for citizen reports)
"""

from datetime import UTC, datetime
from typing import Any

SOURCE_BASE_RELIABILITY = {
    "satellite": 0.88,
    "official": 0.85,
    "rainfall": 0.82,
    "terrain": 0.95,   # terrain features are stable
    "historical": 0.80,
    "human": 0.60,     # citizen reports — needs verification
    "derived": 0.70,
}


async def score_evidence_reliability(evidence: dict[str, Any]) -> float:
    """
    Compute a reliability score (0-1) for an evidence item.

    Args:
        evidence: Evidence item dict containing at minimum source_type.

    Returns:
        Reliability score between 0.0 and 1.0.
    """
    source_type = evidence.get("source_type", "derived")
    base = SOURCE_BASE_RELIABILITY.get(source_type, 0.60)

    # Freshness modifier
    freshness = evidence.get("freshness", "UNKNOWN")
    freshness_modifier = {"HIGH": 0.0, "MEDIUM": -0.05, "LOW": -0.15, "UNKNOWN": -0.20}
    base += freshness_modifier.get(freshness, -0.10)

    # For citizen reports: verification bonuses
    if source_type == "human":
        if evidence.get("location_verified"):
            base += 0.10
        if evidence.get("timestamp_verified"):
            base += 0.05
        if evidence.get("cracks_detected") or evidence.get("road_damage_detected"):
            base += 0.15  # CV confirmed damage

    # Satellite quality bonus
    if source_type == "satellite":
        coherence = evidence.get("coherence")
        if coherence and coherence > 0.7:
            base += 0.05

    return round(min(max(base, 0.0), 1.0), 3)


async def verify_citizen_report(report_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Run the full citizen report verification pipeline.
    In the demo this uses heuristics; production would call CV models.

    Pipeline:
      metadata → location → timestamp → duplicate detection → CV → reliability
    """
    from app.database.mongodb import get_collection

    reports_col = get_collection("citizen_reports")
    report = await reports_col.find_one({"_id": report_id})

    if not report:
        # Use payload directly (new submission path)
        report = payload

    result = {
        "report_id": report_id,
        "location_verified": bool(report.get("location")),
        "timestamp_verified": True,   # stub: check if within 24h
        "is_duplicate": False,         # stub: implement hash-based dedup
        "cracks_detected": "crack" in str(report.get("description", "")).lower(),
        "road_damage_detected": "damage" in str(report.get("description", "")).lower()
                                 or "block" in str(report.get("description", "")).lower(),
        "debris_detected": "debris" in str(report.get("description", "")).lower(),
        "flooding_detected": "flood" in str(report.get("description", "")).lower(),
        "cv_confidence": 0.75,  # stub: would come from actual CV model
    }

    # Compute reliability from verification results
    reliability = await score_evidence_reliability({
        "source_type": "human",
        "freshness": "HIGH",
        **result,
    })
    result["reliability_score"] = reliability
    result["evidence_type"] = "road_damage" if result["road_damage_detected"] else "general_report"
    result["verified_at"] = datetime.now(UTC).isoformat()

    # Update report in DB if it exists
    if report and "_id" in report:
        await reports_col.update_one(
            {"_id": report_id},
            {"$set": {**result, "status": "VERIFIED"}},
        )

    return result
