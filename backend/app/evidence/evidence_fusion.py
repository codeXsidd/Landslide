"""NER-LDI Evidence Fusion - combines multiple evidence sources with provenance."""
from typing import List, Dict
from datetime import datetime, timezone, timedelta


SOURCE_RELIABILITY = {
    "satellite_sentinel": 0.92,
    "rainfall_sensor": 0.88,
    "official_report": 0.90,
    "field_inspection": 0.95,
    "citizen_report_verified": 0.80,
    "citizen_report_unverified": 0.45,
    "model_output": 0.75,
    "historical": 0.70,
    "synthetic": 0.30,
}

FRESHNESS_THRESHOLDS = {
    "satellite": timedelta(hours=48),
    "rainfall_sensor": timedelta(hours=6),
    "field_inspection": timedelta(hours=24),
    "citizen_report": timedelta(hours=12),
    "official_report": timedelta(hours=72),
}


def classify_freshness(source_type: str, timestamp: str) -> str:
    if not timestamp:
        return "EXPIRED"
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "EXPIRED"
    age = datetime.now(timezone.utc) - ts
    threshold = FRESHNESS_THRESHOLDS.get(source_type, timedelta(hours=24))
    if age < threshold:
        return "FRESH"
    elif age < threshold * 2:
        return "RECENT"
    elif age < threshold * 5:
        return "STALE"
    return "EXPIRED"


def fuse_evidence(evidence_items: List[Dict]) -> Dict:
    """Fuse multiple evidence sources into a unified assessment."""
    if not evidence_items:
        return {"status": "UNKNOWN", "known": [], "unknown": [], "uncertain": [], "conflicting": [], "stale": []}

    known, unknown, uncertain, conflicting, stale = [], [], [], [], []
    expected_types = {"rainfall", "terrain", "satellite", "historical", "road_status", "forecast"}
    present_types = set()

    for item in evidence_items:
        etype = item.get("evidence_type", "unknown")
        present_types.add(etype)
        freshness = item.get("freshness", classify_freshness(item.get("source_type", ""), item.get("timestamp", "")))
        reliability = item.get("reliability", SOURCE_RELIABILITY.get(item.get("source_type", ""), 0.5))

        if freshness in ("STALE", "EXPIRED"):
            stale.append(item)
        elif reliability < 0.5:
            uncertain.append(item)
        else:
            known.append(item)

    # Check for conflicts
    values_by_type = {}
    for item in known:
        t = item.get("evidence_type")
        values_by_type.setdefault(t, []).append(item)
    for t, items in values_by_type.items():
        if len(items) > 1:
            risk_levels = set(str(i.get("value", {}).get("risk_level", "")) for i in items)
            if len(risk_levels) > 1:
                conflicting.extend(items)
                known = [k for k in known if k not in items]

    # Missing types
    missing = expected_types - present_types
    for m in missing:
        unknown.append({"evidence_type": m, "status": "NOT_AVAILABLE"})

    overall = "KNOWN" if known and not conflicting and not stale else               "CONFLICTING" if conflicting else               "STALE" if stale and not known else               "UNCERTAIN" if uncertain else "UNKNOWN"

    return {
        "status": overall,
        "known": known,
        "unknown": unknown,
        "uncertain": uncertain,
        "conflicting": conflicting,
        "stale": stale,
        "coverage": len(present_types) / len(expected_types),
        "reliability_weighted_score": sum(i.get("reliability", 0.5) for i in known) / max(len(known), 1),
    }
