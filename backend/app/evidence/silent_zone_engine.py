"""NER-LDI Silent Zone Engine - identifies under-monitored high-risk areas."""
from typing import Dict, List
from datetime import datetime, timezone, timedelta


def detect_silent_zones(locations: List[Dict], evidence_by_location: Dict[str, List],
                        risk_scores: Dict[str, float] = None) -> List[Dict]:
    """Identify locations with high risk but low observation coverage."""
    silent_zones = []
    now = datetime.now(timezone.utc)

    for loc in locations:
        loc_id = loc.get("location_id", loc.get("name", "unknown"))
        evidence = evidence_by_location.get(loc_id, [])
        risk = risk_scores.get(loc_id, 0.5) if risk_scores else 0.5

        # Count recent evidence
        recent_count = 0
        for e in evidence:
            try:
                ts = datetime.fromisoformat(e.get("timestamp", "").replace("Z", "+00:00"))
                if (now - ts) < timedelta(hours=48):
                    recent_count += 1
            except (ValueError, TypeError):
                pass

        # Criteria for silent zone
        is_silent = (
            risk >= 0.4 and  # Moderate+ susceptibility
            recent_count < 2 and  # Very few recent observations
            loc.get("population", 0) > 0  # Has population exposure
        )

        if is_silent:
            priority = "CRITICAL" if risk > 0.7 else "HIGH" if risk > 0.5 else "MODERATE"
            silent_zones.append({
                "location_id": loc_id,
                "location": loc,
                "silent_zone_status": True,
                "reason": f"Risk={risk:.2f} but only {recent_count} recent observations",
                "monitoring_priority": priority,
                "risk_score": risk,
                "recent_observations": recent_count,
                "population_at_risk": loc.get("population", 0),
            })

    return sorted(silent_zones, key=lambda x: x["risk_score"], reverse=True)
