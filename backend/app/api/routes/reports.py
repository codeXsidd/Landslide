"""NER-SAGE — reports routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/reports", summary="reports endpoint (stub)")
async def reports_list():
    return {"module": "reports", "status": "stub - implementation in progress"}
