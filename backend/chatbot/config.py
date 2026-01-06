# backend/config.py
"""
Central config for the MahaSaathi backend.
Non-secrets (paths, model names) go here.
Secrets like DB DSN live in .env and are loaded via dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Secrets / DSNs
PG_DSN = os.getenv("PG_DSN")  # e.g. postgresql://postgres:pw@localhost:5432/Mahasaathi

# LLM and embedding models
LLM_MODEL = os.getenv("LLM_MODEL", "gemma2:9b")  # Ollama model for chat / intent
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Paths (project relative)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)  # Go up to backend/ directory
CHROMA_DB_PATH = os.path.join(BACKEND_DIR, "chroma_db")
RAG_DOCS_PATH = os.path.join(BACKEND_DIR, "rag_docs")

# RAG settings
RAG_TOP_K = 3
RAG_CHUNK_SIZE = 500  # approx characters when chunking docs (simple splitter)
COLLECTION_NAME = "mahasaathi_v2"  # Changed to v2 to avoid embedding conflict

# Chat settings
MAX_HISTORY = 5

# CLI / debug
DEBUG = True

APP_NAME = "MahaSaathi Assistant (CLI Test)"
