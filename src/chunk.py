"""Chunking de documentos cargados en fragmentos indexables."""


def chunk_documents(documents: list[dict], chunk_size: int, chunk_overlap: int) -> list[dict]:
    """Divide los documentos en chunks, conservando el metadato 'source'."""
    raise NotImplementedError
