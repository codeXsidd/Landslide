"""NER-LDI Contradiction Engine - detects conflicting evidence."""
from typing import List, Dict


def detect_contradictions(evidence_items: List[Dict]) -> Dict:
    """Detect and explain contradictions between evidence sources."""
    contradictions = []

    # Group by type
    by_type = {}
    for item in evidence_items:
        t = item.get("evidence_type", "unknown")
        by_type.setdefault(t, []).append(item)

    # Check rainfall vs satellite
    rainfall_items = by_type.get("rainfall", [])
    satellite_items = by_type.get("satellite", [])
    if rainfall_items and satellite_items:
        high_rain = any(i.get("value", {}).get("intensity", "") in ("HIGH", "EXTREME") for i in rainfall_items)
        low_sat_change = any(not i.get("value", {}).get("change_detected", True) for i in satellite_items)
        if high_rain and low_sat_change:
            contradictions.append({
                "type": "rainfall_vs_satellite",
                "severity": "MEDIUM",
                "explanation": "High rainfall detected but satellite shows no ground change. Possible: early stage, satellite stale, or false alarm.",
                "supporting_sources": [i.get("source") for i in rainfall_items],
                "conflicting_sources": [i.get("source") for i in satellite_items],
                "verification_required": True,
            })

    # Check citizen vs model
    citizen_items = by_type.get("citizen_report", [])
    model_items = by_type.get("model_output", [])
    if citizen_items and model_items:
        citizen_damage = any("damage" in str(i.get("value", "")).lower() or "slide" in str(i.get("value", "")).lower() for i in citizen_items)
        model_low = any(i.get("value", {}).get("risk_level") in ("VERY_LOW", "LOW") for i in model_items)
        if citizen_damage and model_low:
            contradictions.append({
                "type": "citizen_vs_model",
                "severity": "HIGH",
                "explanation": "Citizen reports damage/slide but model predicts low risk. Ground truth takes priority pending verification.",
                "supporting_sources": [i.get("source") for i in citizen_items],
                "conflicting_sources": ["risk_model"],
                "verification_required": True,
            })

    # Road status conflicts
    road_items = by_type.get("road_status", [])
    if len(road_items) > 1:
        statuses = set(str(i.get("value", {}).get("status", "")) for i in road_items)
        if len(statuses) > 1:
            contradictions.append({
                "type": "road_status_conflict",
                "severity": "HIGH",
                "explanation": f"Conflicting road status reports: {statuses}",
                "supporting_sources": [road_items[0].get("source")],
                "conflicting_sources": [i.get("source") for i in road_items[1:]],
                "verification_required": True,
            })

    return {
        "has_contradictions": len(contradictions) > 0,
        "contradiction_count": len(contradictions),
        "contradictions": contradictions,
        "evidence_status": "CONFLICTING" if contradictions else "CONSISTENT",
        "max_severity": max((c["severity"] for c in contradictions), default="NONE"),
    }
