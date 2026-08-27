"""
NER-SAGE — RAG Retrieval Pipeline
Queries Qdrant to find the most relevant document chunks for a given context.
"""

import structlog
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config.settings import settings
from app.rag.embeddings import get_embeddings

logger = structlog.get_logger(__name__)

# Use sync client for Langchain QdrantVectorStore compatibility in some contexts,
# or AsyncQdrant depending on exact langchain-qdrant version support.
# For simplicity in retrieval, we'll instantiate standard client.
_qdrant_sync_client = None

def get_vector_store():
    global _qdrant_sync_client
    if _qdrant_sync_client is None:
        _qdrant_sync_client = QdrantClient(location=settings.QDRANT_LOCATION)

    return QdrantVectorStore(
        client=_qdrant_sync_client,
        collection_name=settings.QDRANT_COLLECTION_DOCUMENTS,
        embedding=get_embeddings()
    )

def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieves the top K most relevant chunks from Qdrant based on the query.
    Returns them as a single concatenated string.
    """
    try:
        vector_store = get_vector_store()
        docs = vector_store.similarity_search(query, k=top_k)
        if not docs:
            return "No relevant SOPs found in the database."

        context = "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in docs])
        return context
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return "Warning: Retrieval system unavailable."
