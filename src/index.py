"""Construccion y persistencia del indice vectorial (ChromaDB)."""


def build_index(chunks: list[dict], persist_dir: str, collection_name: str, recreate: bool = False) -> None:
    """Indexa los chunks en ChromaDB. Si recreate=True, reconstruye la coleccion desde cero."""
    raise NotImplementedError


def get_collection(persist_dir: str, collection_name: str):
    """Devuelve la coleccion de ChromaDB persistida."""
    raise NotImplementedError
