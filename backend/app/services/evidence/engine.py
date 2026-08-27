"""
NER-LDI MVP — Evidence Engine Service Layer
Manages known, unknown, stale, conflicting, and reliable evidence.

Every evidence item includes:
  source, timestamp, location, evidence_type, freshness, reliability, is_simulated
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.evidence_engine.freshness.checker import check_freshness
from backend.app.evidence_engine.reliability.scorer import score_evidence_reliability


# Evidence types supported
EVIDENCE_TYPES = {
    "satellite": {"max_age_hours": 72, "base_reliability": 0.92},
    "rainfall_sensor": {"max_age_hours": 6, "base_reliability": 0.88},
    "road_inspection": {"max_age_hours": 48, "base_reliability": 0.92},
    "citizen_report": {"max_age_hours": 24, "base_reliability": 0.65},
    "historical_inventory": {"max_age_hours": 8760, "base_reliability": 0.85},
    "model_output": {"max_age_hours": 12, "base_reliability": 0.78},
    "weather_forecast": {"max_age_hours": 12, "base_reliability": 0.72},
}


def classify_information_state(item: dict[str, Any]) -> str:
    """
    Classify an evidence item's information state:
    - KNOWN: fresh, reliable, consistent
    - STALE: exists but too old
    - CONFLICTING: contradicts another item
    - UNKNOWN: no data available
    """
    evidence_type = item.get("evidence_type", "unknown")
    cfg = EVIDENCE_TYPES.get(evidence_type, {"max_age_hours": 48, "base_reliability": 0.5})

    # Check freshness
    ts_str = item.get("timestamp") or item.get("created_at")
    if ts_str:
        try:
            if isinstance(ts_str, str):
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            else:
                ts = ts_str
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=UTC)
            age_hours = (datetime.now(UTC) - ts).total_seconds() / 3600
            if age_hours > cfg["max_age_hours"]:
                return "STALE"
        except Exception:
            return "UNKNOWN"
    else:
        return "UNKNOWN"

    # Check reliability
    reliability = item.get("reliability", cfg["base_reliability"])
    if isinstance(reliability, (int, float)) and reliability < 0.4:
        return "CONFLICTING"

    return "KNOWN"


def compute_evidence_summary(evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute a full evidence summary for a location.
    Returns classified items + what is unknown.
    """
    classified = []
    for item in evidence_items:
        state = classify_information_state(item)
        classified.append({**item, "information_state": state})

    known = [e for e in classified if e["information_state"] == "KNOWN"]
    stale = [e for e in classified if e["information_state"] == "STALE"]
    conflicting = [e for e in classified if e["information_state"] == "CONFLICTING"]

    # What evidence is missing entirely?
    covered_types = {e.get("evidence_type") for e in evidence_items}
    critical_missing = [t for t in ["satellite", "rainfall_sensor", "road_inspection"] if t not in covered_types]

    return {
        "total_items": len(classified),
        "known_count": len(known),
        "stale_count": len(stale),
        "conflicting_count": len(conflicting),
        "missing_types": critical_missing,
        "items": classified,
        "has_conflict": len(conflicting) > 0,
        "computed_at": datetime.now(UTC).isoformat(),
    }


def build_evidence_item(
    location_id: str,
    source: str,
    source_type: str,
    evidence_type: str,
    value: Any,
    timestamp: datetime | None = None,
    is_simulated: bool = False,
    lat: float | None = None,
    lon: float | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """
    Construct a standardised evidence item with all required fields.
    """
    ts = timestamp or datetime.now(UTC)
    cfg = EVIDENCE_TYPES.get(evidence_type, {"max_age_hours": 48, "base_reliability": 0.6})
    age_hours = (datetime.now(UTC) - ts.replace(tzinfo=UTC) if ts.tzinfo is None else datetime.now(UTC) - ts).total_seconds() / 3600 if ts else 0

    freshness = max(0.0, 1.0 - age_hours / (cfg["max_age_hours"] * 2))
    reliability = cfg["base_reliability"]
    if is_simulated:
        reliability *= 0.7

    item = {
        "location_id": location_id,
        "source": source,
        "source_type": source_type,
        "evidence_type": evidence_type,
        "value": value,
        "timestamp": ts.isoformat() if isinstance(ts, datetime) else str(ts),
        "freshness": round(freshness, 3),
        "reliability": round(reliability, 3),
        "is_simulated": is_simulated,
        "information_state": "KNOWN" if freshness > 0.5 else "STALE",
    }

    if lat is not None:
        item["latitude"] = lat
    if lon is not None:
        item["longitude"] = lon
    if extra:
        item.update(extra)

    return item


def detect_conflicts(evidence_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Detect contradictions between evidence items.
    Returns list of conflict pairs.
    """
    conflicts = []
    road_items = [e for e in evidence_items if e.get("evidence_type") == "road_inspection"]

    for i in range(len(road_items)):
        for j in range(i + 1, len(road_items)):
            a, b = road_items[i], road_items[j]
            status_a = a.get("value", {}).get("road_status") if isinstance(a.get("value"), dict) else a.get("road_status")
            status_b = b.get("value", {}).get("road_status") if isinstance(b.get("value"), dict) else b.get("road_status")
            if status_a and status_b and status_a != status_b:
                conflicts.append({
                    "type": "ROAD_STATUS_CONFLICT",
                    "item_a_source": a.get("source"),
                    "item_b_source": b.get("source"),
                    "value_a": status_a,
                    "value_b": status_b,
                    "severity": "HIGH",
                    "resolution": "Require field verification",
                })

    return conflicts
