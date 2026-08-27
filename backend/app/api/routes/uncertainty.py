"""
NER-SAGE — Uncertainty, Unknowns & Conflicts Routes

GET /uncertainty/{location_id}   - Full uncertainty profile
GET /unknowns/{location_id}      - KNOWN/UNKNOWN/STALE/CONFLICTING breakdown
GET /conflicts/{location_id}     - Conflicting evidence pairs
"""

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/uncertainty/{location_id}", summary="Get uncertainty profile for a location")
async def get_uncertainty(location_id: str):
    """
    Returns the full uncertainty profile for a location.
    Includes overall confidence level, per-source uncertainty contributions,
    and flags for stale/missing/conflicting evidence.
    """
    from app.evidence_engine.uncertainty.estimator import compute_uncertainty_profile

    # Get latest risk prediction + all evidence
    risk_col = get_collection("risk_predictions")
    evidence_col = get_collection("evidence_items")

    latest_risk = await risk_col.find_one(
        {"location_id": location_id}, sort=[("created_at", -1)]
    )
    if not latest_risk:
        raise HTTPException(status_code=404, detail=f"No risk data for '{location_id}'")

    evidence = await evidence_col.find({"location_id": location_id}).to_list(length=100)
    profile = await compute_uncertainty_profile(location_id, latest_risk, evidence)
    return profile


@router.get("/unknowns/{location_id}", summary="Get KNOWN/UNKNOWN/STALE classification")
async def get_unknowns(location_id: str):
    """
    Returns the information-state classification for all evidence types at this location.
    States: KNOWN | UNKNOWN | UNCERTAIN | CONFLICTING | STALE
    This drives the Self-Questioning Loop.
    """
    from app.evidence_engine.unknowns.tracker import classify_information_states

    evidence_col = get_collection("evidence_items")
    evidence = await evidence_col.find({"location_id": location_id}).to_list(length=100)
    classification = await classify_information_states(location_id, evidence)
    return classification


router_unknowns = router  # alias for import in main.py


@router.get("/conflicts/{location_id}", summary="Get conflicting evidence pairs")
async def get_conflicts(location_id: str):
    """
    Returns pairs of evidence items that contradict each other.
    Example: Rainfall HIGH + Satellite showing LOW deformation.
    Each conflict is explained with a reason.
    """
    from app.evidence_engine.contradiction.detector import detect_contradictions

    evidence_col = get_collection("evidence_items")
    evidence = await evidence_col.find({"location_id": location_id}).to_list(length=100)
    conflicts = await detect_contradictions(location_id, evidence)
    return conflicts
