"""
NER-SAGE — Evidence Freshness Checker

Determines the freshness level (HIGH/MEDIUM/LOW/UNKNOWN) of an evidence item
based on the age of the observation relative to source-specific thresholds.
"""

from datetime import UTC, datetime
from typing import Any

from app.config.constants import FRESHNESS_THRESHOLDS, FreshnessLevel


def check_freshness(evidence: dict[str, Any]) -> str:
    """
    Return FreshnessLevel string for an evidence item.

    Args:
        evidence: Evidence dict. Must contain 'source_type' and either
                  'acquired_at', 'observed_at', or 'timestamp'.

    Returns:
        'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN'
    """
    source_type = evidence.get("source_type", "derived")
    thresholds = FRESHNESS_THRESHOLDS.get(source_type, FRESHNESS_THRESHOLDS["citizen_report"])

    # Try to get the observation timestamp
    timestamp_str = (
        evidence.get("acquired_at")
        or evidence.get("observed_at")
        or evidence.get("timestamp")
    )
    if not timestamp_str:
        return FreshnessLevel.UNKNOWN

    try:
        if isinstance(timestamp_str, datetime):
            obs_time = timestamp_str
        else:
            obs_time = datetime.fromisoformat(str(timestamp_str).replace("Z", "+00:00"))

        now = datetime.now(UTC)
        age_seconds = (now - obs_time).total_seconds()

        if age_seconds < thresholds["HIGH"]:
            return FreshnessLevel.HIGH
        elif age_seconds < thresholds["MEDIUM"]:
            return FreshnessLevel.MEDIUM
        else:
            return FreshnessLevel.LOW

    except (ValueError, TypeError):
        return FreshnessLevel.UNKNOWN


def is_stale(evidence: dict[str, Any]) -> bool:
    """Return True if the evidence item is stale (freshness = LOW)."""
    return check_freshness(evidence) == FreshnessLevel.LOW


def get_age_hours(evidence: dict[str, Any]) -> float | None:
    """Return the age of an evidence item in hours, or None if timestamp is missing."""
    timestamp_str = (
        evidence.get("acquired_at")
        or evidence.get("observed_at")
        or evidence.get("timestamp")
    )
    if not timestamp_str:
        return None
    try:
        if isinstance(timestamp_str, datetime):
            obs_time = timestamp_str
        else:
            obs_time = datetime.fromisoformat(str(timestamp_str).replace("Z", "+00:00"))
        return (datetime.now(UTC) - obs_time).total_seconds() / 3600
    except (ValueError, TypeError):
        return None
