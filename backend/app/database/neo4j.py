"""
NER-SAGE Neo4j Connection Manager
Uses the official Neo4j async Python driver.
"""


import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config.settings import settings

log = structlog.get_logger(__name__)

_driver: AsyncDriver | None = None


async def connect_neo4j() -> None:
    """Initialize Neo4j async driver."""
    global _driver
    log.info("neo4j_connecting", uri=settings.NEO4J_URI)
    _driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        max_connection_pool_size=20,
    )
    # Verify connectivity
    await _driver.verify_connectivity()
    log.info("neo4j_connected", uri=settings.NEO4J_URI)


async def close_neo4j() -> None:
    """Close Neo4j driver."""
    global _driver
    if _driver:
        await _driver.close()
        _driver = None
    log.info("neo4j_disconnected")


def get_neo4j_driver() -> AsyncDriver:
    """Return the active Neo4j driver."""
    if _driver is None:
        raise RuntimeError("Neo4j not connected. Call connect_neo4j() first.")
    return _driver


async def run_query(cypher: str, parameters: dict = None) -> list:
    """Execute a read Cypher query and return records as dicts."""
    driver = get_neo4j_driver()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.run(cypher, parameters or {})
        records = await result.data()
        return records


async def run_write_query(cypher: str, parameters: dict = None) -> list:
    """Execute a write Cypher query inside an explicit write transaction."""
    driver = get_neo4j_driver()
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = await session.execute_write(
            lambda tx: tx.run(cypher, parameters or {})
        )
        return result
