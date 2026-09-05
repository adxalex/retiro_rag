"""Configuracion centralizada del sistema RAG - Parque de El Retiro."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Rutas ---
DATA_DIR = "data"
CHROMA_DIR = "chroma"
COLLECTION_NAME = "retiro_madrid"

# --- Modelos ---
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

# --- Chunking ---
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# --- Retrieval ---
TOP_K = 3
MAX_CHUNKS = 200  # limite de chunks indexados; documentar si se cambia
