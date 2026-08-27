"""
NER-SAGE — RAG Ingestion Script
Reads the synthetic SOP, chunks it, embeds it, and upserts to Qdrant.
"""

import asyncio
import os
import sys

from langchain.schema import Document

# Fix path to import backend modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.database.qdrant import init_qdrant_collections
from app.rag.chunking import get_text_splitter
from app.rag.generation import generate_action_plan
from app.rag.retrieval import get_vector_store


async def ingest_documents():
    print("1. Initializing Qdrant collections...")
    await init_qdrant_collections()

    print("2. Reading SOP documents...")
    doc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rag", "documents", "emergency_sop", "assam_landslide_sop.txt")

    if not os.path.exists(doc_path):
        print(f"Error: Could not find document at {doc_path}")
        return

    with open(doc_path, encoding="utf-8") as f:
        text = f.read()

    print("3. Chunking document...")
    splitter = get_text_splitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_text(text)

    docs = [Document(page_content=chunk, metadata={"source": "assam_landslide_sop.txt", "chunk_index": i}) for i, chunk in enumerate(chunks)]
    print(f"   Created {len(docs)} chunks.")

    print("4. Embedding and Upserting to Qdrant...")
    vector_store = get_vector_store()
    vector_store.add_documents(docs)
    print("   Ingestion complete!")

    print("\n--- Testing Retrieval and Generation ---")
    test_scenario = "Road B has a major landslide blocking it. Village X (pop 850) is now completely isolated, and hospital access is degraded."
    print(f"Scenario: {test_scenario}")

    print("\nGenerating AI Response via Groq...")
    response = generate_action_plan(test_scenario)
    print("\n[ NER-SAGE ACTION PLAN ]")
    print("=" * 60)
    print(response)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(ingest_documents())
