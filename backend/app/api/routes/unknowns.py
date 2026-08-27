"""NER-SAGE — unknowns routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/unknowns", summary="unknowns endpoint (stub)")
async def unknowns_list():
    return {"module": "unknowns", "status": "stub - implementation in progress"}
