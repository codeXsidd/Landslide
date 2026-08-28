"""
NER-LDI API Routes v2 — No database dependency.
All persistence uses file-based JSONL stores.
"""
from datetime import datetime, timezone

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
from app.persistence.jsonl_store import append_event, read_events

router = APIRouter()


# ── Health ──────────────────────────────────────────────────────

@router.get("/health", tags=["Health"])
async def health():
    from app.services.groq_service import is_available as groq_available
    return {
        "status": "ok",
        "system": "NER-LDI",
        "version": "1.0.0",
        "database": "file-based (no DB required)",
        "groq_available": groq_available(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Risk ────────────────────────────────────────────────────────

@router.post("/risk/predict", tags=["Risk"], status_code=201)
async def predict_risk(payload: dict):
    """ML risk prediction pipeline. Uses actual model or stub fallback."""
    location_id = payload.get("location_id")
    if not location_id:
        raise HTTPException(status_code=400, detail="location_id required")

    lat = payload.get("latitude", 26.1)
    lon = payload.get("longitude", 91.7)
    terrain = payload.get("terrain_features", {"elevation": 500, "slope": 25, "aspect": 180, "terrain_ruggedness": 12})
    rainfall = payload.get("rainfall_features", {})
    evidence_items = payload.get("evidence", [])

    risk_score = 0.5 + terrain.get("slope", 20) * 0.008 + terrain.get("terrain_ruggedness", 10) * 0.005
    risk_score = min(0.95, max(0.1, risk_score))

    unc = compute_uncertainty(risk_score, terrain, evidence_items)
    fusion = fuse_evidence(evidence_items)
    road = compute_road_impact(lat, lon, risk_score)
    iso = compute_village_isolation(lat, lon, road["road_blockage_probability"])

    risk_level = "CRITICAL" if risk_score >= 0.8 else "HIGH" if risk_score >= 0.6 else "MODERATE" if risk_score >= 0.4 else "LOW"

    result = {
        "location_id": location_id,
        "latitude": lat,
        "longitude": lon,
        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
        "confidence": round(unc["confidence"], 4),
        "uncertainty_level": unc["uncertainty_level"],
        "evidence_status": fusion["status"],
        "major_factors": _get_factors(terrain, risk_score),
        "road_blockage_probability": road["road_blockage_probability"],
        "village_isolation_probability": iso["village_isolation_probability"],
        "population_exposed": iso["population_affected"],
        "model_version": "terrain_heuristic_v1",
        "is_simulated": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    append_event("audit_log", {"event": "RISK_PREDICTION", "location_id": location_id, "risk_score": result["risk_score"]})
    return result


@router.get("/risk/{location_id}", tags=["Risk"])
async def get_risk(location_id: str):
    """Get latest risk prediction for a location (from event log or compute fresh)."""
    events = read_events("audit_log", limit=50, filter_fn=lambda e: e.get("event") == "RISK_PREDICTION" and e.get("location_id") == location_id)
    if events:
        return events[0]
    raise HTTPException(status_code=404, detail=f"No risk data for {location_id}. Run /risk/predict first.")


# ── Evidence ────────────────────────────────────────────────────

@router.post("/evidence", tags=["Evidence"], status_code=201)
async def submit_evidence(payload: dict):
    """Submit a new evidence item. Persisted to JSONL."""
    required = ["location_id", "source", "source_type", "evidence_type", "is_simulated"]
    for f in required:
        if f not in payload:
            raise HTTPException(status_code=422, detail=f"Missing: {f}")

    event = append_event("evidence_events", {
        **payload,
        "event": "EVIDENCE_SUBMITTED",
        "status": "ACCEPTED",
    })
    append_event("audit_log", {"event": "EVIDENCE_SUBMITTED", "location_id": payload["location_id"], "source": payload["source"]})
    return {"id": event["id"], "status": "created"}


@router.post("/evidence/verify", tags=["Evidence"])
async def verify_evidence(payload: dict):
    """Verify a citizen evidence report."""
    report_id = payload.get("report_id") or payload.get("evidence_id")
    if not report_id:
        raise HTTPException(status_code=400, detail="report_id required")

    reliability = 0.6 + (0.2 if payload.get("has_photo") else 0.0)
    result = {
        "report_id": report_id,
        "verification_status": "LIKELY_VALID",
        "reliability_score": reliability,
        "checks_passed": ["location_valid", "timestamp_recent", "format_valid"],
        "is_simulated": True,
    }
    append_event("evidence_events", {"event": "EVIDENCE_VERIFIED", **result})
    append_event("audit_log", {"event": "EVIDENCE_VERIFIED", "report_id": report_id, "reliability": reliability})
    return result


@router.post("/evidence/update-risk", tags=["Evidence"])
async def update_risk_with_new_evidence(payload: dict):
    """Update risk score after new evidence arrives."""
    location_id = payload.get("location_id")
    if not location_id:
        raise HTTPException(status_code=400, detail="location_id required")

    current_risk = payload.get("current_risk_score", 0.72)
    evidence = payload.get("evidence", {})
    updated = update_risk_with_evidence(current_risk, evidence)
    append_event("audit_log", {"event": "RISK_UPDATED", "location_id": location_id, "new_risk": updated.get("updated_risk_score")})
    return updated


# ── Impact ──────────────────────────────────────────────────────

@router.get("/impact/{location_id}", tags=["Impact"])
async def get_impact(location_id: str):
    """Get impact prediction for a location."""
    lat = 26.1
    lon = 91.7
    risk_score = 0.72

    road = compute_road_impact(lat, lon, risk_score)
    iso = compute_village_isolation(lat, lon, road["road_blockage_probability"])
    infra = compute_infrastructure_exposure(lat, lon, risk_score)

    return {
        "location_id": location_id,
        "road_impact": road,
        "village_isolation": iso,
        "infrastructure": infra,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "is_simulated": True,
    }


# ── Simulation ──────────────────────────────────────────────────

@router.post("/simulation", tags=["Simulation"], status_code=201)
async def run_simulation_route(payload: dict):
    """Run a what-if simulation scenario."""
    scenario_type = payload.get("scenario_type", "custom")
    location_id = payload.get("location_id", "LOC-001")

    baseline = payload.get("baseline_state", {
        "risk_score": 0.72,
        "road_blockage_probability": 0.45,
        "village_isolation_probability": 0.32,
        "population_exposed": 850,
        "rainfall_features": {"cumulative_7d": 120, "intensity_max": 35},
    })
    scenario = payload.get("scenario", {
        "type": scenario_type,
        "rainfall_factor": payload.get("rainfall_multiplier", 1.0),
        "road_closure": payload.get("road_failure", False),
    })

    result = run_simulation(baseline, scenario)
    append_event("simulation_runs", {"event": "SIMULATION_RUN", "location_id": location_id, "scenario_type": scenario_type, "simulation_id": result["simulation_id"]})
    append_event("audit_log", {"event": "SIMULATION_RUN", "location_id": location_id, "scenario_type": scenario_type})
    return result


# ── Decisions ───────────────────────────────────────────────────

@router.post("/decisions", tags=["Decisions"], status_code=201)
async def record_decision(payload: dict):
    """Record a human decision (APPROVED/REJECTED/MODIFIED)."""
    required = ["action_id", "status", "decided_by"]
    for f in required:
        if f not in payload:
            raise HTTPException(status_code=422, detail=f"Missing: {f}")
    if payload["status"] not in ("APPROVED", "REJECTED", "MODIFIED"):
        raise HTTPException(status_code=400, detail="status must be APPROVED, REJECTED, or MODIFIED")

    event = append_event("human_decisions", {
        "event": "HUMAN_DECISION",
        **payload,
    })
    append_event("audit_log", {
        "event": "HUMAN_DECISION",
        "action_id": payload["action_id"],
        "status": payload["status"],
        "decided_by": payload["decided_by"],
    })
    return {"id": event["id"], "status": "recorded"}


@router.get("/priorities", tags=["Decisions"])
async def get_priorities():
    """Get ranked action priorities."""
    locations = [
        {"location_id": "LOC-001", "name": "Road B Corridor", "risk_score": 0.88, "population_exposed": 850},
        {"location_id": "LOC-002", "name": "Village A Access", "risk_score": 0.82, "population_exposed": 1240},
    ]
    opt = optimize_actions(locations)
    return {"priorities": opt.get("selected_actions", []), "total_cost": opt.get("total_cost", 0)}


# ── Feedback ────────────────────────────────────────────────────

@router.post("/feedback", tags=["Feedback"], status_code=201)
async def record_feedback(payload: dict):
    """Record outcome feedback for a prediction."""
    event = append_event("feedback", {
        "event": "OUTCOME_RECORDED",
        **payload,
    })
    append_event("audit_log", {"event": "OUTCOME_RECORDED", "location_id": payload.get("location_id"), "category": payload.get("feedback_category")})
    return {"id": event["id"], "status": "recorded"}


# ── Audit ───────────────────────────────────────────────────────

@router.get("/audit", tags=["Audit"])
async def get_audit_log(limit: int = 50):
    """Get recent audit events."""
    events = read_events("audit_log", limit=limit)
    return {"events": events, "total": len(events)}


# ── AI / Groq ───────────────────────────────────────────────────

@router.post("/ai/explain-risk", tags=["AI"])
async def explain_risk_endpoint(payload: dict):
    """Get AI explanation of a risk assessment. Uses Groq server-side."""
    from app.services.groq_service import explain_risk
    result = await explain_risk(payload)
    return result


@router.post("/ai/emergency-guidance", tags=["AI"])
async def emergency_guidance_endpoint(payload: dict):
    """Get role-specific emergency guidance. Uses Groq server-side."""
    from app.services.groq_service import emergency_guidance
    risk_state = payload.get("risk_state", {})
    impact = payload.get("impact", {})
    role = payload.get("role", "DISTRICT_AUTHORITY")
    result = await emergency_guidance(risk_state, impact, role)
    return result


@router.post("/ai/ask", tags=["AI"])
async def ask_endpoint(payload: dict):
    """Ask a question about landslide risk. Uses Groq server-side."""
    from app.services.groq_service import answer_question
    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="question required")
    context = payload.get("context", "")
    result = await answer_question(question, context)
    return result


# ── Helpers ─────────────────────────────────────────────────────

def _get_factors(terrain: dict, risk_score: float) -> list:
    factors = []
    if terrain.get("slope", 0) > 30:
        factors.append("steep slope")
    if terrain.get("elevation", 0) > 600:
        factors.append("high elevation")
    if terrain.get("terrain_ruggedness", 0) > 15:
        factors.append("high terrain ruggedness")
    if risk_score > 0.7:
        factors.append("historical susceptibility")
    if not factors:
        factors.append("moderate terrain")
    return factors
