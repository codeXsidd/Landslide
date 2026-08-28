"""
NER-LDI FastAPI Application — Database-Free Prototype
Northeast Region Landslide Decision Intelligence
"""
import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.ldi import router as ldi_router
from app.api.routes.map import router as map_router
from app.api.routes_v2 import router as v2_router
from app.config.settings import settings

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.dev.ConsoleRenderer(colors=True),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger(__name__)

app = FastAPI(
    title="NER-LDI",
    description=(
        "Northeast Region Landslide Decision Intelligence.\n\n"
        "AI-powered landslide risk assessment and decision support.\n\n"
        "**No database required.** File-based persistence for prototype.\n\n"
        "*Smart India Hackathon 2026*"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "type": "ValueError"},
    )


@app.get("/health")
async def root_health():
    return {"status": "ok", "system": "NER-LDI", "version": "1.0.0"}


PREFIX = settings.API_PREFIX
app.include_router(v2_router, prefix=PREFIX)
app.include_router(ldi_router, prefix=PREFIX)
app.include_router(map_router, prefix=PREFIX)


@app.on_event("startup")
async def startup():
    log.info("ner_ldi_started", port=settings.API_PORT, prefix=PREFIX)
