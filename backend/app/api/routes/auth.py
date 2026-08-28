"""
NER-SAGE — Stub routes for Auth, Verification, Actions, Reports, Documents, Unknowns, Connectivity
"""

from datetime import UTC

from fastapi import APIRouter

router = APIRouter()

@router.post("/auth/login", summary="Login and get JWT token")
async def login(payload: dict):
    """Returns a JWT token for demo user. Replace with real auth in production."""
    from datetime import datetime, timedelta

    from jose import jwt

    from app.config.settings import settings
    user_id = payload.get("username", "demo_user")
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": user_id, "exp": expire, "role": "responder"},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer", "role": "responder"}
