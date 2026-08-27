"""
NER-SAGE — Text Chunking Pipeline
Splits large SOP documents into indexable chunks for Qdrant.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_text_splitter(chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Returns a text splitter configured for SOP and guideline documents.
    We use relatively small chunks (500 chars) to ensure highly specific retrieval
    (e.g., retrieving just the specific bullet point for a road closure).
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
