"""
NER-SAGE MongoDB Index Definitions
All indexes are created at startup. Safe to re-run (uses ensureIndex semantics).
"""

import structlog

from app.database.mongodb import get_database

log = structlog.get_logger(__name__)


async def create_all_indexes() -> None:
    """Create all MongoDB indexes. Called once at application startup."""
    db = get_database()
    log.info("mongodb_creating_indexes")

    # ── Geospatial 2dsphere indexes ────────────────────────────
    await db.locations.create_index([("geometry", "2dsphere")])
    await db.roads.create_index([("geometry", "2dsphere")])
    await db.villages.create_index([("geometry", "2dsphere")])
    await db.landslide_events.create_index([("geometry", "2dsphere")])
    await db.citizen_reports.create_index([("location", "2dsphere")])
    await db.satellite_observations.create_index([("geometry", "2dsphere")])
    await db.infrastructure.create_index([("geometry", "2dsphere")])

    # ── Risk predictions ────────────────────────────────────────
    await db.risk_predictions.create_index(
        [("location_id", 1), ("created_at", -1)]
    )
    await db.risk_predictions.create_index([("risk_level", 1)])
    await db.risk_predictions.create_index([("created_at", -1)])

    # ── Evidence items ──────────────────────────────────────────
    await db.evidence_items.create_index(
        [("location_id", 1), ("evidence_type", 1)]
    )
    await db.evidence_items.create_index([("source_type", 1), ("freshness", 1)])
    await db.evidence_items.create_index([("created_at", -1)])

    # ── Citizen reports ─────────────────────────────────────────
    await db.citizen_reports.create_index([("status", 1), ("created_at", -1)])
    await db.citizen_reports.create_index([("location_id", 1)])

    # ── Weather ─────────────────────────────────────────────────
    await db.weather_observations.create_index(
        [("location_id", 1), ("observed_at", -1)]
    )
    await db.rainfall_forecasts.create_index(
        [("location_id", 1), ("valid_from", 1)]
    )

    # ── Satellite ───────────────────────────────────────────────
    await db.satellite_observations.create_index(
        [("location_id", 1), ("acquired_at", -1)]
    )

    # ── Simulations ─────────────────────────────────────────────
    await db.simulation_runs.create_index([("created_at", -1)])
    await db.simulation_runs.create_index([("location_id", 1)])

    # ── Decisions / Actions ─────────────────────────────────────
    await db.human_decisions.create_index([("status", 1), ("created_at", -1)])
    await db.actions.create_index([("location_id", 1), ("status", 1)])

    # ── Audit logs ──────────────────────────────────────────────
    await db.audit_logs.create_index([("timestamp", -1)])
    await db.audit_logs.create_index([("user_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("resource_type", 1), ("resource_id", 1)])

    # ── Impact predictions ──────────────────────────────────────
    await db.impact_predictions.create_index([("location_id", 1), ("created_at", -1)])

    # ── Documents (RAG source) ──────────────────────────────────
    await db.documents.create_index([("jurisdiction", 1), ("document_type", 1)])

    # ── Model versions ──────────────────────────────────────────
    await db.model_versions.create_index([("is_active", 1), ("created_at", -1)])

    log.info("mongodb_indexes_created")
