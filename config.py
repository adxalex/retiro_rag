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

# --- Embeddings ---
EMBED_BATCH_SIZE = 32  # chunks por lote enviado a la API de Gemini embeddings

# --- Indexación ---
INDEX_BATCH_SIZE = 100  # vectores por lote en collection.upsert()
HNSW_SPACE = "cosine"  # métrica del índice (contrato compartido)

# --- Retrieval ---
TOP_K = 3

# Límite opcional para el experimento de indexación.
# None representa ausencia de límite.
# Debe aplicarse mediante embed.limitar_chunks() en el futuro
# orquestador chunk -> embed -> index.
MAX_CHUNKS = None
