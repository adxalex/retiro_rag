"""Retrieval de los chunks mas relevantes para una consulta."""


def retrieve(query: str, top_k: int) -> list[dict]:
    """Devuelve los top_k chunks mas relevantes: [{"text": ..., "source": ..., "score": ...}, ...]."""
    raise NotImplementedError
