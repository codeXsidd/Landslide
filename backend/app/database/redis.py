"""
NER-SAGE Redis Connection Manager
Uses redis-py async client with connection pooling.
"""


import structlog
from redis.asyncio import ConnectionPool, Redis

from app.config.settings import settings

log = structlog.get_logger(__name__)

_redis: Redis | None = None


async def connect_redis() -> None:
    """Initialize Redis async client."""
    global _redis
    log.info("redis_connecting", url=settings.REDIS_URL)
    pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,
    )
    _redis = Redis(connection_pool=pool)
    await _redis.ping()
    log.info("redis_connected")


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
    log.info("redis_disconnected")


def get_redis() -> Redis:
    """Return the active Redis client."""
    if _redis is None:
        raise RuntimeError("Redis not connected. Call connect_redis() first.")
    return _redis


async def cache_get(key: str) -> str | None:
    """Get a value from cache. Returns None on miss."""
    return await get_redis().get(key)


async def cache_set(key: str, value: str, ttl: int = None) -> None:
    """Set a cache value with optional TTL (defaults to settings.REDIS_DEFAULT_TTL)."""
    ttl = ttl or settings.REDIS_DEFAULT_TTL
    await get_redis().setex(key, ttl, value)


async def cache_delete(key: str) -> None:
    """Delete a cache key."""
    await get_redis().delete(key)


async def cache_exists(key: str) -> bool:
    """Check if a key exists in cache."""
    return bool(await get_redis().exists(key))
