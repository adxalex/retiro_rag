"""Construccion y persistencia del indice ChromaDB.

Responsable: Integrante Parte 2 (Alejandra).
TODO:
- build_index(chunks: list[dict], persist_dir: str, collection_name: str) -> None
- get_collection(persist_dir: str, collection_name: str)
- Si cambia el modelo de embeddings o MAX_CHUNKS, el indice debe regenerarse desde cero.
"""


def build_index(chunks, persist_dir, collection_name):
    raise NotImplementedError


def get_collection(persist_dir, collection_name):
    raise NotImplementedError
