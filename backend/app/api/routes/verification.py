"""NER-SAGE — verification routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/verification", summary="verification endpoint (stub)")
async def verification_list():
    return {"module": "verification", "status": "stub - implementation in progress"}
