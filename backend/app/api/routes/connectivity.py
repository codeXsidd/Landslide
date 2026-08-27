"""NER-SAGE — connectivity routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/connectivity", summary="connectivity endpoint (stub)")
async def connectivity_list():
    return {"module": "connectivity", "status": "stub - implementation in progress"}
