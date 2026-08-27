"""
NER-SAGE — Pydantic models for Citizen Reports and CV Verification.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CitizenReportModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str | None = None

    # Reporter info (anonymous for MVP)
    reporter_id: str | None = None

    # Report content
    description: str
    report_type: str  # road_damage | debris | crack | flooding | general

    # Location
    location: dict = Field(..., description="GeoJSON Point of report location")
    reported_at: datetime

    # Image/video stored in MinIO
    image_keys: list[str] = Field(default_factory=list)
    video_keys: list[str] = Field(default_factory=list)

    # Verification pipeline
    status: str = "PENDING"  # PENDING | VERIFIED | REJECTED | NEEDS_REVIEW
    location_verified: bool = False
    timestamp_verified: bool = False
    is_duplicate: bool = False

    # CV results
    cracks_detected: bool = False
    road_damage_detected: bool = False
    debris_detected: bool = False
    flooding_detected: bool = False
    cv_confidence: float = Field(0.0, ge=0, le=1)

    # Final reliability
    reliability_score: float = Field(0.0, ge=0, le=1)
    reliability_reason: str | None = None

    is_simulated: bool = True
    created_at: datetime
    verified_at: datetime | None = None

    class Config:
        populate_by_name = True


class VerificationResultModel(BaseModel):
    report_id: str
    location_verified: bool
    timestamp_verified: bool
    is_duplicate: bool
    cracks_detected: bool
    road_damage_detected: bool
    debris_detected: bool
    reliability_score: float
    evidence_type: str
    notes: str | None = None
    verified_at: datetime
