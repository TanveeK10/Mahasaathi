# backend/rag_ingest.py
"""
Command-line ingestion helper. Run this to (re)build the Chroma vector DB from rag_docs.
"""

from rag_engine import ingest_documents

if __name__ == "__main__":
    ingest_documents()
    print("✅ RAG ingestion done.")
