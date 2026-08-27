"""
NER-SAGE — Pydantic models for Impact, Simulation, Decision, and Action.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.config.constants import ActionType, DecisionStatus


class ImpactPredictionModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str

    # Road blockage
    road_blockage_probability: float = Field(..., ge=0, le=1)
    road_blockage_level: str  # HIGH | MEDIUM | LOW
    blocked_road_ids: list[str] = Field(default_factory=list)

    # Village isolation
    isolation_probability: float = Field(..., ge=0, le=1)
    isolated_village_ids: list[str] = Field(default_factory=list)
    affected_population: int = 0

    # Hospital/facility access
    hospital_access_degraded: bool = False
    hospital_access_probability: float = Field(1.0, ge=0, le=1)
    nearest_hospital_id: str | None = None
    alternate_route_available: bool = False
    alternate_route_distance_km: float | None = None

    # Cascading consequences
    cascade_level: int = Field(0, description="Depth of cascading road failures")
    consequences: list[str] = Field(default_factory=list)

    is_simulated: bool = True
    created_at: datetime
    based_on_risk_id: str | None = None

    class Config:
        populate_by_name = True


class SimulationRunModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    scenario_type: str  # rainfall_increase | road_failure | evidence_update | intervention
    input_changes: dict[str, Any]
    baseline_state: dict[str, Any]
    simulated_state: dict[str, Any]
    model_version: str
    is_simulated: bool = True
    created_at: datetime
    created_by: str | None = None

    class Config:
        populate_by_name = True


class ActionModel(BaseModel):
    id: str = Field(alias="_id")
    location_id: str
    action_type: ActionType
    title: str
    description: str
    priority_rank: int
    expected_harm_reduction: float = Field(..., ge=0, le=1)
    action_cost: str  # LOW | MEDIUM | HIGH
    time_to_execute_hours: float
    resources_required: list[str] = Field(default_factory=list)
    reason: str
    supporting_evidence: list[str] = Field(default_factory=list)
    unknown_evidence: list[str] = Field(default_factory=list)
    consequence_if_wrong: str
    requires_human_approval: bool = True
    status: str = "RECOMMENDED"
    created_at: datetime

    class Config:
        populate_by_name = True


class HumanDecisionModel(BaseModel):
    id: str = Field(alias="_id")
    action_id: str
    location_id: str
    status: DecisionStatus
    decided_by: str
    decision_notes: str | None = None
    modified_action: dict[str, Any] | None = None
    created_at: datetime
    outcome: str | None = None
    outcome_recorded_at: datetime | None = None

    class Config:
        populate_by_name = True


class AuditLogModel(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str | None = None
    result: str  # SUCCESS | FAILURE
    details: dict[str, Any] | None = None

    class Config:
        populate_by_name = True
