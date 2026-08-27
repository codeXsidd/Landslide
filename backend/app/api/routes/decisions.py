"""
NER-SAGE — Decision and Action API Routes

GET  /priorities              - Get ranked action priorities
POST /actions                 - Create a recommended action
POST /decisions               - Record a human decision (approve/reject/modify)
POST /decisions/{id}/override - Override a previous decision
"""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_collection

router = APIRouter()


@router.get("/priorities", summary="Get ranked action priorities")
async def get_priorities(location_id: str = None):
    """
    Returns the ranked list of recommended actions across all high-risk locations.
    Each action includes: expected harm reduction, cost, reason, and approval requirement.
    """
    from app.decision_engine.prioritization.ranker import rank_actions
    priorities = await rank_actions(location_id)
    return {"priorities": priorities}


@router.post("/actions", summary="Create a recommended action", status_code=201)
async def create_action(payload: dict):
    required = ["location_id", "action_type", "title", "reason"]
    for f in required:
        if f not in payload:
            raise HTTPException(status_code=422, detail=f"Missing field: {f}")
    payload["created_at"] = datetime.now(UTC)
    payload["status"] = "RECOMMENDED"
    collection = get_collection("actions")
    result = await collection.insert_one(payload)
    return {"id": str(result.inserted_id), "status": "created"}


@router.post("/decisions", summary="Record a human decision", status_code=201)
async def record_decision(payload: dict):
    """
    Records a human APPROVE / REJECT / MODIFY decision on a recommended action.
    This is the critical human-in-the-loop gate before any action is executed.
    All critical actions require this approval.
    """
    required = ["action_id", "status", "decided_by"]
    for f in required:
        if f not in payload:
            raise HTTPException(status_code=422, detail=f"Missing field: {f}")
    if payload["status"] not in ("APPROVED", "REJECTED", "MODIFIED"):
        raise HTTPException(status_code=400, detail="status must be APPROVED, REJECTED, or MODIFIED")

    payload["created_at"] = datetime.now(UTC)
    collection = get_collection("human_decisions")
    result = await collection.insert_one(payload)

    # Audit log
    from app.security.audit import log_audit
    await log_audit(
        user_id=payload["decided_by"],
        action="HUMAN_DECISION",
        resource_type="action",
        resource_id=payload["action_id"],
        result=payload["status"],
    )

    return {"id": str(result.inserted_id), "status": "recorded"}


@router.post("/decisions/{decision_id}/override", summary="Override a previous decision")
async def override_decision(decision_id: str, payload: dict):
    collection = get_collection("human_decisions")
    doc = await collection.find_one({"_id": decision_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Decision not found")
    await collection.update_one(
        {"_id": decision_id},
        {"$set": {"status": "MODIFIED", "override_notes": payload.get("notes"), "override_at": datetime.now(UTC)}}
    )
    return {"status": "overridden"}
