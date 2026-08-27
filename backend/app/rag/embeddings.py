"""
NER-SAGE — Embedding pipeline
Uses sentence-transformers to convert text into vector embeddings locally,
removing reliance on external APIs (like OpenAI) for the retrieval stage.
"""

from langchain_huggingface import HuggingFaceEmbeddings

# Use a small, fast embedding model suitable for CPUs and rapid prototyping
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Global lazy-loaded instance
_embeddings_instance = None

def get_embeddings():
    """Returns the singleton HuggingFaceEmbeddings instance."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embeddings_instance
