"""
NER-SAGE — Evidence API Routes

GET  /evidence/{location_id}   - Get all evidence for a location
POST /evidence                 - Submit new evidence item
POST /evidence/verify          - Submit citizen report for verification
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/evidence/{location_id}", summary="Get all evidence for a location")
async def get_evidence(
    location_id: str,
    evidence_type: str | None = Query(None),
    information_state: str | None = Query(None),
):
    """
    Returns all evidence items for the specified location.
    Includes known, unknown, stale, and conflicting evidence.
    Each item includes reliability score, freshness, and information state.
    """
    collection = get_collection("evidence_items")
    query = {"location_id": location_id}
    if evidence_type:
        query["evidence_type"] = evidence_type
    if information_state:
        query["information_state"] = information_state.upper()

    cursor = collection.find(query).sort("created_at", -1)
    items = await cursor.to_list(length=200)
    for item in items:
        item["_id"] = str(item["_id"])

    # Summarise information states
    states_summary = {}
    for item in items:
        state = item.get("information_state", "UNKNOWN")
        states_summary[state] = states_summary.get(state, 0) + 1

    return {
        "location_id": location_id,
        "evidence_count": len(items),
        "states_summary": states_summary,
        "items": items,
    }


@router.post("/evidence", summary="Submit new evidence item", status_code=201)
async def submit_evidence(payload: dict):
    """
    Submit a new evidence item (satellite observation, rainfall reading, field report).
    Required fields: location_id, source, source_type, evidence_type, timestamp, is_simulated.
    """
    required = ["location_id", "source", "source_type", "evidence_type", "is_simulated"]
    for field in required:
        if field not in payload:
            raise HTTPException(status_code=422, detail=f"Missing required field: {field}")

    from app.evidence_engine.freshness.checker import check_freshness
    from app.evidence_engine.reliability.scorer import score_evidence_reliability

    payload["reliability"] = await score_evidence_reliability(payload)
    payload["freshness"] = check_freshness(payload)
    payload["created_at"] = datetime.now(UTC)

    collection = get_collection("evidence_items")
    result = await collection.insert_one(payload)
    return {"id": str(result.inserted_id), "status": "created"}


@router.post("/evidence/verify", summary="Submit citizen report for verification")
async def verify_citizen_evidence(payload: dict):
    """
    Accepts a citizen report (text + image references) and runs the full
    verification pipeline: metadata → location → timestamp → duplicate → CV → reliability.
    """
    from app.evidence_engine.reliability.scorer import verify_citizen_report

    report_id = payload.get("report_id")
    if not report_id:
        raise HTTPException(status_code=400, detail="report_id is required")

    result = await verify_citizen_report(report_id, payload)
    return result
