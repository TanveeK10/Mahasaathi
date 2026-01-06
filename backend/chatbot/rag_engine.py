# backend/rag_engine.py
"""
ChromaDB-based RAG engine using SentenceTransformer (MiniLM) embeddings.
Provides:
- ingest_documents() -> create or refresh collection from rag_docs folder
- search(query, k) -> return top-k doc texts + metadata
"""

import os
import glob
from config import CHROMA_DB_PATH, RAG_DOCS_PATH, EMBEDDING_MODEL_NAME, RAG_TOP_K, RAG_CHUNK_SIZE, DEBUG, COLLECTION_NAME
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from typing import List, Dict

# Initialize embedding function using SentenceTransformer embedding function
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)

# Persistent Chroma client
client = PersistentClient(path=CHROMA_DB_PATH)
# COLLECTION_NAME is now imported from config

def _get_or_create_collection():
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        return client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    else:
        return client.create_collection(name=COLLECTION_NAME, embedding_function=embed_fn)

def _chunk_text(text: str, chunk_size: int = RAG_CHUNK_SIZE) -> List[str]:
    """
    Simple chunker by characters (safe for markdown). Could be replaced by a smarter
    sentence/token based splitter later.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)
        start += chunk_size
    return chunks

def ingest_documents():
    """
    Walk rag_docs folder and ingest markdown files into ChromaDB.
    Recreates collection (clean) each run.
    """
    collection = _get_or_create_collection()
    # simple strategy: delete collection and recreate
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embed_fn)

    files = sorted(glob.glob(os.path.join(RAG_DOCS_PATH, "*.md")))
    docs_added = 0
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        fname = os.path.basename(filepath)
        chunks = _chunk_text(content)
        ids = [f"{fname}::{i}" for i in range(len(chunks))]
        metadatas = [{"source": fname, "chunk_index": i} for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        docs_added += len(chunks)
        if DEBUG:
            print(f"[RAG] Ingested {len(chunks)} chunks from {fname}")
    if DEBUG:
        print(f"[RAG] Total chunks ingested: {docs_added}")

def search(query: str, k: int = RAG_TOP_K) -> List[Dict]:
    """
    Returns list of dicts: [{"document": text, "id": id, "metadata": {...}, "distance": ...}, ...]
    """
    collection = _get_or_create_collection()
    res = collection.query(query_texts=[query], n_results=k, include=["documents", "metadatas", "distances"])
    # format results
    docs = []
    if res and "documents" in res and res["documents"]:
        docs_list = res["documents"][0]
        metas = res["metadatas"][0]
        ids = res["ids"][0]
        dists = res["distances"][0] if "distances" in res else [None]*len(ids)
        for doc_text, meta, id_, dist in zip(docs_list, metas, ids, dists):
            docs.append({"document": doc_text, "metadata": meta, "id": id_, "distance": dist})
    return docs
