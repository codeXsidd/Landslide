"""
NER-SAGE Domain Constants

All threshold values, enumerations, and domain-specific constants.
Change these values via environment variables where possible (see settings.py).
"""

from enum import Enum

# ── Risk Levels ─────────────────────────────────────────────────

class RiskLevel(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NEGLIGIBLE = "NEGLIGIBLE"
    UNKNOWN = "UNKNOWN"


RISK_THRESHOLDS = {
    RiskLevel.VERY_HIGH: 0.90,
    RiskLevel.HIGH: 0.75,
    RiskLevel.MEDIUM: 0.50,
    RiskLevel.LOW: 0.25,
}

def risk_score_to_level(score: float) -> RiskLevel:
    """Convert a numeric risk score (0-1) to a RiskLevel enum."""
    if score >= RISK_THRESHOLDS[RiskLevel.VERY_HIGH]:
        return RiskLevel.VERY_HIGH
    if score >= RISK_THRESHOLDS[RiskLevel.HIGH]:
        return RiskLevel.HIGH
    if score >= RISK_THRESHOLDS[RiskLevel.MEDIUM]:
        return RiskLevel.MEDIUM
    if score >= RISK_THRESHOLDS[RiskLevel.LOW]:
        return RiskLevel.LOW
    return RiskLevel.NEGLIGIBLE


# ── Confidence Levels ────────────────────────────────────────────

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


CONFIDENCE_THRESHOLDS = {
    ConfidenceLevel.HIGH: 0.80,
    ConfidenceLevel.MEDIUM: 0.60,
    ConfidenceLevel.LOW: 0.40,
}

def confidence_score_to_level(score: float) -> ConfidenceLevel:
    if score >= CONFIDENCE_THRESHOLDS[ConfidenceLevel.HIGH]:
        return ConfidenceLevel.HIGH
    if score >= CONFIDENCE_THRESHOLDS[ConfidenceLevel.MEDIUM]:
        return ConfidenceLevel.MEDIUM
    if score >= CONFIDENCE_THRESHOLDS[ConfidenceLevel.LOW]:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.VERY_LOW


# ── Evidence States ──────────────────────────────────────────────

class EvidenceState(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    STALE = "STALE"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"


class EvidenceStatus(str, Enum):
    """Overall evidence status for a location."""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


# ── Freshness Thresholds (seconds) ───────────────────────────────

class FreshnessLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


FRESHNESS_THRESHOLDS = {
    "satellite": {"HIGH": 172800, "MEDIUM": 604800},       # 2 days / 7 days
    "rainfall": {"HIGH": 10800, "MEDIUM": 86400},           # 3 hours / 24 hours
    "rainfall_forecast": {"HIGH": 21600, "MEDIUM": 86400},  # 6 hours / 24 hours
    "citizen_report": {"HIGH": 21600, "MEDIUM": 86400},     # 6 hours / 24 hours
    "road_status": {"HIGH": 3600, "MEDIUM": 21600},         # 1 hour / 6 hours
    "terrain": {"HIGH": 31536000, "MEDIUM": 315360000},     # 1 year / 10 years
}


# ── Evidence Source Types ────────────────────────────────────────

class SourceType(str, Enum):
    SATELLITE = "satellite"
    RAINFALL = "rainfall"
    TERRAIN = "terrain"
    HUMAN = "human"
    OFFICIAL = "official"
    DERIVED = "derived"
    HISTORICAL = "historical"


# ── Information States (Self-Questioning Loop) ───────────────────

class InformationState(str, Enum):
    KNOWN = "KNOWN"
    UNKNOWN = "UNKNOWN"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"


# ── Decision / Action Types ──────────────────────────────────────

class ActionType(str, Enum):
    INSPECT_ROAD = "INSPECT_ROAD"
    PREPARE_ALTERNATE_ROUTE = "PREPARE_ALTERNATE_ROUTE"
    INCREASE_MONITORING = "INCREASE_MONITORING"
    PRE_POSITION_TEAM = "PRE_POSITION_TEAM"
    ISSUE_WARNING = "ISSUE_WARNING"
    RESTRICT_CORRIDOR = "RESTRICT_CORRIDOR"
    PREPARE_EVACUATION = "PREPARE_EVACUATION"
    REQUEST_SATELLITE = "REQUEST_SATELLITE"
    REQUEST_FIELD_REPORT = "REQUEST_FIELD_REPORT"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"


class DecisionStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    EXPIRED = "EXPIRED"


# ── NER Region ───────────────────────────────────────────────────

NER_BBOX = {
    "min_lon": 88.0,
    "min_lat": 21.9,
    "max_lon": 97.4,
    "max_lat": 29.5,
}

NER_STATES = [
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura",
]

# Demo scenario location IDs (for SIH demo)
DEMO_LOCATIONS = {
    "road_b": "Road B — Primary access corridor to Village X",
    "village_x": "Village X — Isolated on Road B failure",
    "hospital_z": "Hospital Z — Accessible via Junction Y",
    "junction_y": "Junction Y — Road B/C merge point",
    "route_c": "Route C — Alternate route (longer, passable)",
}


# ── Uncertainty Engine Thresholds ────────────────────────────────

UNCERTAINTY_THRESHOLDS = {
    "stale_satellite_penalty": 0.15,   # Confidence reduction per stale satellite day
    "missing_ground_penalty": 0.20,    # Confidence reduction for no ground evidence
    "model_disagreement_penalty": 0.10, # Per 0.1 model disagreement
    "forecast_conflict_penalty": 0.12,  # Confidence reduction for forecast conflicts
}


# ── Next-Best-Evidence Engine ────────────────────────────────────

MAX_DECISION_VALUE = 1.0
MIN_ACQUISITION_COST = 0.01  # Avoid division by zero
