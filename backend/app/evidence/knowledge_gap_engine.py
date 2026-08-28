"""NER-LDI Knowledge Gap Engine - identifies what the system does NOT know."""
from typing import List, Dict
from datetime import datetime, timezone, timedelta


EXPECTED_EVIDENCE = {
    "rainfall": {"max_age_hours": 6, "critical": True},
    "terrain": {"max_age_hours": 8760, "critical": True},
    "satellite": {"max_age_hours": 48, "critical": False},
    "historical": {"max_age_hours": 8760, "critical": False},
    "road_status": {"max_age_hours": 24, "critical": True},
    "forecast": {"max_age_hours": 12, "critical": True},
    "field_inspection": {"max_age_hours": 72, "critical": False},
}


def identify_knowledge_gaps(evidence_items: List[Dict], location: Dict = None) -> Dict:
    """Identify what the system doesn't know about a location."""
    now = datetime.now(timezone.utc)
    known, unknown, uncertain, stale, conflicting = [], [], [], [], []

    present_types = {}
    for item in evidence_items:
        etype = item.get("evidence_type", "unknown")
        present_types.setdefault(etype, []).append(item)

    for etype, config in EXPECTED_EVIDENCE.items():
        items = present_types.get(etype, [])
        if not items:
            unknown.append({
                "evidence_type": etype,
                "reason": f"No {etype} evidence available",
                "critical": config["critical"],
                "impact": f"Cannot assess {etype} contribution to risk"
            })
            continue

        # Check freshness
        latest = max(items, key=lambda x: x.get("timestamp", ""))
        try:
            ts = datetime.fromisoformat(latest.get("timestamp", "").replace("Z", "+00:00"))
            age_hours = (now - ts).total_seconds() / 3600
        except (ValueError, TypeError):
            age_hours = float("inf")

        if age_hours > config["max_age_hours"]:
            stale.append({
                "evidence_type": etype,
                "reason": f"{etype} evidence is {age_hours:.0f}h old (threshold: {config['max_age_hours']}h)",
                "critical": config["critical"],
                "last_update": latest.get("timestamp")
            })
        else:
            reliability = latest.get("reliability", 0.5)
            if reliability < 0.5:
                uncertain.append({"evidence_type": etype, "reason": f"Low reliability ({reliability:.2f})", "critical": config["critical"]})
            else:
                known.append({"evidence_type": etype, "reliability": reliability, "timestamp": latest.get("timestamp")})

    # Out-of-distribution check
    if location:
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        if lat > 27 or lat < 22:
            uncertain.append({"evidence_type": "spatial", "reason": "Location at edge of training coverage", "critical": False})

    return {
        "known_items": known,
        "unknown_items": unknown,
        "uncertain_items": uncertain,
        "stale_items": stale,
        "conflicting_items": conflicting,
        "total_gaps": len(unknown) + len(stale) + len(uncertain),
        "critical_gaps": sum(1 for i in unknown + stale if i.get("critical")),
        "knowledge_completeness": len(known) / max(len(EXPECTED_EVIDENCE), 1),
    }
