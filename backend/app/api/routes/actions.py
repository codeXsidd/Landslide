"""NER-SAGE — actions routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/actions", summary="actions endpoint (stub)")
async def actions_list():
    return {"module": "actions", "status": "stub - implementation in progress"}
