"""NER-SAGE — documents routes (stub)."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/documents", summary="documents endpoint (stub)")
async def documents_list():
    return {"module": "documents", "status": "stub - implementation in progress"}
