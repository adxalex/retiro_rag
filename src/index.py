"""Construccion y persistencia del indice ChromaDB.

Responsable: Integrante Parte 2 (Alejandra).
TODO:
- build_index(chunks: list[dict], persist_dir: str, collection_name: str, recreate: bool = False) -> None
  Si recreate=True, borrar la coleccion/persist_dir existente ANTES de indexar
  (obligatorio regenerar desde cero si cambia el modelo de embeddings, MAX_CHUNKS,
  o el parser usado en load.py -- ver README / informe_decisiones.md).
- get_collection(persist_dir: str, collection_name: str)
"""


def build_index(chunks, persist_dir, collection_name, recreate: bool = False):
    raise NotImplementedError


def get_collection(persist_dir, collection_name):
    raise NotImplementedError
