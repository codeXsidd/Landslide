"""
NER-SAGE FastAPI Application Entry Point
Northeast Region — Self-Adaptive Geospatial Emergency Intelligence
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── Import all route modules ────────────────────────────────────
from app.api.routes import (
    actions,
    auth,
    connectivity,
    decisions,
    documents,
    evidence,
    health,
    impact,
    locations,
    reports,
    risk,
    simulation,
    uncertainty,
    unknowns,
    verification,
)
from app.config.logging import configure_logging
from app.config.settings import settings
from app.database.indexes import create_all_indexes
from app.database.mongodb import close_mongo, connect_mongo
from app.database.neo4j import close_neo4j, connect_neo4j
from app.database.qdrant import ensure_collections
from app.database.redis import close_redis, connect_redis

configure_logging()
log = structlog.get_logger(__name__)


# ── Application lifespan ────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    log.info("ner_sage_starting", version=settings.APP_VERSION, env=settings.APP_ENV)

    # Startup
    await connect_mongo()
    await create_all_indexes()
    await connect_neo4j()
    await connect_redis()
    await ensure_collections()

    log.info("ner_sage_ready", api_url=f"http://{settings.API_HOST}:{settings.API_PORT}")
    yield

    # Shutdown
    log.info("ner_sage_shutting_down")
    await close_mongo()
    await close_neo4j()
    await close_redis()
    log.info("ner_sage_stopped")


# ── FastAPI Application ─────────────────────────────────────────

app = FastAPI(
    title="NER-SAGE",
    description=(
        "Northeast Region — Self-Adaptive Geospatial Emergency Intelligence.\n\n"
        "An AI-powered landslide decision-intelligence system for Northeast India.\n\n"
        "**Key Innovation:** Self-Questioning Decision Loop with Next-Best-Evidence Engine.\n\n"
        "*Smart India Hackathon 2026 · Problem Statement 2*"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ── Middleware ──────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception Handlers ──────────────────────────────────────────

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "type": "ValueError"},
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc), "type": "PermissionError"},
    )


# ── Routers ────────────────────────────────────────────────────

PREFIX = settings.API_PREFIX

app.include_router(health.router, prefix=PREFIX, tags=["Health"])
app.include_router(auth.router, prefix=PREFIX, tags=["Authentication"])
app.include_router(locations.router, prefix=PREFIX, tags=["Locations"])
app.include_router(risk.router, prefix=PREFIX, tags=["Risk"])
app.include_router(evidence.router, prefix=PREFIX, tags=["Evidence"])
app.include_router(uncertainty.router, prefix=PREFIX, tags=["Uncertainty"])
app.include_router(unknowns.router, prefix=PREFIX, tags=["Unknowns"])
app.include_router(verification.router, prefix=PREFIX, tags=["Verification"])
app.include_router(impact.router, prefix=PREFIX, tags=["Impact"])
app.include_router(connectivity.router, prefix=PREFIX, tags=["Connectivity"])
app.include_router(simulation.router, prefix=PREFIX, tags=["Simulation"])
app.include_router(decisions.router, prefix=PREFIX, tags=["Decisions"])
app.include_router(actions.router, prefix=PREFIX, tags=["Actions"])
app.include_router(reports.router, prefix=PREFIX, tags=["Reports"])
app.include_router(documents.router, prefix=PREFIX, tags=["Documents / RAG"])
