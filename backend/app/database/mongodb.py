"""
NER-SAGE MongoDB Connection Manager
Uses Motor (async MongoDB driver) with connection pooling.
"""


import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.settings import settings

log = structlog.get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_mongo() -> None:
    """Initialize MongoDB connection pool."""
    global _client, _database
    log.info("mongodb_connecting", uri=settings.MONGODB_URI.split("@")[-1])
    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        maxPoolSize=20,
        minPoolSize=2,
        serverSelectionTimeoutMS=5000,
    )
    _database = _client[settings.MONGODB_DATABASE]
    # Verify connection
    await _client.admin.command("ping")
    log.info("mongodb_connected", database=settings.MONGODB_DATABASE)


async def close_mongo() -> None:
    """Close MongoDB connection pool."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
    log.info("mongodb_disconnected")


def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    if _database is None:
        raise RuntimeError("MongoDB not connected. Call connect_mongo() first.")
    return _database


def get_collection(name: str):
    """Return a named collection from the active database."""
    return get_database()[name]
