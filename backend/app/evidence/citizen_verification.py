"""NER-LDI Citizen/Field Evidence Validation."""
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import hashlib


def verify_citizen_evidence(report: Dict) -> Dict:
    """Validate citizen-submitted evidence for reliability."""
    checks = []
    score = 0.5  # Start neutral

    lat = report.get("latitude")
    lon = report.get("longitude")
    timestamp = report.get("timestamp")
    description = report.get("description", "")
    has_image = bool(report.get("image_keys") or report.get("images"))
    has_video = bool(report.get("video_keys") or report.get("videos"))

    # Geographic consistency
    if lat and lon:
        if 21.0 <= lat <= 30.0 and 88.0 <= lon <= 98.0:
            checks.append({"check": "location_in_ner", "passed": True})
            score += 0.1
        else:
            checks.append({"check": "location_in_ner", "passed": False, "reason": "Outside NER bounds"})
            score -= 0.2

    # Timestamp plausibility
    if timestamp:
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - ts
            if age < timedelta(hours=0):
                checks.append({"check": "timestamp_future", "passed": False})
                score -= 0.3
            elif age < timedelta(hours=24):
                checks.append({"check": "timestamp_recent", "passed": True})
                score += 0.1
            else:
                checks.append({"check": "timestamp_aged", "passed": True, "age_hours": age.total_seconds()/3600})
        except (ValueError, TypeError):
            checks.append({"check": "timestamp_parse", "passed": False})

    # Media presence boosts reliability
    if has_image:
        score += 0.15
        checks.append({"check": "has_image", "passed": True})
    if has_video:
        score += 0.1
        checks.append({"check": "has_video", "passed": True})

    # Description quality
    if len(description) > 20:
        score += 0.05
        checks.append({"check": "description_length", "passed": True})

    # Landslide keywords
    keywords = ["slide", "landslide", "mud", "debris", "crack", "blocked", "collapse", "soil"]
    if any(k in description.lower() for k in keywords):
        score += 0.1
        checks.append({"check": "relevant_keywords", "passed": True})

    score = max(0.0, min(1.0, score))

    if score >= 0.7:
        status = "LIKELY_VALID"
    elif score >= 0.5:
        status = "NEEDS_VERIFICATION"
    elif score >= 0.3:
        status = "LOW_CONFIDENCE"
    else:
        status = "LIKELY_INVALID"

    return {
        "reliability_score": round(score, 3),
        "validation_status": status,
        "detected_signals": checks,
        "reason": f"Score {score:.2f} based on {len(checks)} checks",
        "is_simulated": report.get("is_simulated", False),
    }
