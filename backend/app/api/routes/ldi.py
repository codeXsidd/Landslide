"""
NER-LDI Decision Intelligence API Routes (standalone, no database required).

POST /ldi/assess       - Full decision intelligence assessment for a location
POST /ldi/simulate     - Run a what-if simulation
POST /ldi/role-output  - Get role-specific formatted output
GET  /ldi/health       - System health check

All outputs are clearly marked as AI recommendations, not official warnings.
"""
from fastapi import APIRouter, HTTPException

from app.evidence.uncertainty_engine import compute_uncertainty
from app.evidence.evidence_fusion import fuse_evidence
from app.evidence.contradiction_engine import detect_contradictions
from app.evidence.knowledge_gap_engine import identify_knowledge_gaps
from app.evidence.next_best_evidence import compute_next_best_evidence
from app.evidence.update_risk import update_risk_with_evidence
from app.impact.road_impact import compute_road_impact
from app.impact.village_isolation import compute_village_isolation, compute_infrastructure_exposure
from app.simulation.risk_simulation import run_simulation
from app.decision_engine.optimizer import optimize_actions
from app.schemas.unified_risk import build_unified_risk_object
from app.services.recommendation.role_output import format_for_role

router = APIRouter(prefix="/ldi", tags=["Decision Intelligence"])


@router.get("/health")
async def ldi_health():
    return {"status": "ok", "system": "NER-LDI", "version": "1.0.0", "is_simulated": True}


@router.post("/assess")
async def assess_location(payload: dict):
    """Full decision intelligence assessment pipeline."""
    lat = payload.get("latitude")
    lon = payload.get("longitude")
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="latitude and longitude required")

    terrain = payload.get("terrain_features", {"elevation": 500, "slope": 20, "aspect": 180, "terrain_ruggedness": 10})
    risk_score = payload.get("risk_score")
    if risk_score is None:
        risk_score = 0.5 + terrain.get("slope", 20) * 0.008 + terrain.get("terrain_ruggedness", 10) * 0.005
        risk_score = min(0.95, max(0.1, risk_score))
    rainfall = payload.get("rainfall_features", {})
    evidence_items = payload.get("evidence", [])
    location = {"latitude": lat, "longitude": lon, "location_id": payload.get("location_id", f"loc_{lat}_{lon}"), "name": payload.get("name", "Unknown")}

    unc = compute_uncertainty(risk_score, terrain, evidence_items)
    fusion = fuse_evidence(evidence_items)
    contradictions = detect_contradictions(evidence_items)
    gaps = identify_knowledge_gaps(evidence_items, location)
    nbe = compute_next_best_evidence(risk_score, unc["confidence"], gaps)
    road = compute_road_impact(lat, lon, risk_score)
    isolation = compute_village_isolation(lat, lon, road["road_blockage_probability"])
    exposure = compute_infrastructure_exposure(lat, lon, risk_score)
    opt = optimize_actions([{**location, "risk_score": risk_score, "population_exposed": isolation["population_affected"]}])

    unified = build_unified_risk_object(
        location=location, risk_score=risk_score, confidence=unc["confidence"],
        terrain_features=terrain, rainfall_features=rainfall,
        evidence_fusion=fusion, uncertainty=unc, contradictions=contradictions,
        knowledge_gaps=gaps, road_impact=road, village_isolation=isolation,
        infrastructure_exposure=exposure, optimization=opt,
    )

    return {
        "unified_risk": unified,
        "next_best_evidence": nbe,
        "disclaimer": "AI-generated recommendation. Not an official emergency warning.",
    }


@router.post("/simulate")
async def simulate_scenario(payload: dict):
    """Run a what-if scenario simulation."""
    baseline = payload.get("baseline_state")
    scenario = payload.get("scenario")
    if not baseline or not scenario:
        raise HTTPException(status_code=400, detail="baseline_state and scenario required")
    result = run_simulation(baseline, scenario)
    return result


@router.post("/role-output")
async def get_role_output(payload: dict):
    """Get risk information formatted for a specific stakeholder role."""
    role = payload.get("role")
    risk_state = payload.get("risk_state")
    if not role or not risk_state:
        raise HTTPException(status_code=400, detail="role and risk_state required")
    impact = payload.get("impact")
    actions = payload.get("actions")
    result = format_for_role(role, risk_state, impact, actions)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
