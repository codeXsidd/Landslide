"""
NER-SAGE — Pydantic models for Risk Predictions and Confidence.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.config.constants import (
    ConfidenceLevel,
    EvidenceStatus,
    InformationState,
    RiskLevel,
)


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: list[float] = Field(..., description="[longitude, latitude]")


class RiskPredictionModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated landslide probability (0-1)")
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0, description="Trust in risk_score (0-1)")
    confidence_level: ConfidenceLevel
    uncertainty: str = Field(..., description="HIGH | MEDIUM | LOW")
    evidence_status: EvidenceStatus
    major_factors: list[str] = Field(default_factory=list)
    model_version: str
    is_simulated: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        populate_by_name = True


class EvidenceItemModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    source: str
    source_type: str
    evidence_type: str
    reliability: float = Field(..., ge=0.0, le=1.0)
    freshness: str  # HIGH | MEDIUM | LOW | UNKNOWN
    information_state: InformationState
    location_verified: bool = False
    timestamp_verified: bool = False
    is_simulated: bool = True
    raw_value: dict | None = None
    notes: str | None = None
    created_at: datetime
    acquired_at: datetime | None = None

    class Config:
        populate_by_name = True


class UncertaintyProfileModel(BaseModel):
    location_id: str
    overall_confidence: float
    confidence_level: ConfidenceLevel
    uncertainty_sources: list[dict] = Field(default_factory=list)
    information_states: dict = Field(default_factory=dict)
    computed_at: datetime


class NextBestEvidenceModel(BaseModel):
    location_id: str
    candidates: list[dict] = Field(default_factory=list)
    recommended_action: str
    recommended_action_type: str
    decision_value: float
    reason: str
    consequence_if_ignored: str
    computed_at: datetime
