"""
NER-SAGE — Qdrant Connection Manager
Handles connection to Qdrant vector database and collection initialization.
"""

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.config.settings import settings

logger = structlog.get_logger(__name__)

# Single global async client instance
qdrant_client = AsyncQdrantClient(location=settings.QDRANT_LOCATION)


async def init_qdrant_collections():
    """Ensure required vector collections exist in Qdrant."""
    collections = [
        settings.QDRANT_COLLECTION_DOCUMENTS,
        settings.QDRANT_COLLECTION_EVIDENCE
    ]

    # We use MiniLM which produces 384-dimensional embeddings
    vector_size = 384

    for collection_name in collections:
        try:
            exists = await qdrant_client.collection_exists(collection_name)
            if not exists:
                await qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"Qdrant collection {collection_name} already exists.")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collection {collection_name}: {e}")

async def close_qdrant_client():
    """Close the async qdrant client (stubbed for compatibility if needed in future)."""
    # qdrant_client does not require explicit async closure in most versions
    pass
