"""Chunking de documentos cargados en fragmentos indexables."""

from collections import defaultdict
from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

_REQUIRED_FIELDS = (
    "document_id",
    "text",
    "source",
    "category",
    "corpus_group",
)


def _validate_chunk_config(chunk_size: int, chunk_overlap: int) -> None:
    """Valida la configuración utilizada por el splitter."""
    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que 0.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap no puede ser negativo.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap debe ser menor que chunk_size.")


def _validate_document(document: dict[str, Any]) -> None:
    """Comprueba que el documento cumple el contrato compartido."""
    missing_fields = [
        field
        for field in _REQUIRED_FIELDS
        if field not in document
    ]

    if missing_fields:
        raise ValueError(
            f"El documento no contiene los campos obligatorios: {fields}.")

    if not isinstance(document["text"], str):
        raise TypeError("El campo 'text' debe ser una cadena de texto.")

    if not document["text"].strip():
        raise ValueError(
            "El campo 'text' no puede estar vacío o contener solo espacios en blanco.")

    page = document.get("page")

    if page is not None:
        if not isinstance(page, int) or page < 1:
            raise ValueError(
                "El campo 'page' debe ser un entero positivo 1-based.")


def _create_splitter(
    chunk_size: int,
    chunk_overlap: int,
) -> RecursiveCharacterTextSplitter:
    """Construye el splitter recursivo con parámetros configurables."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        keep_separator="end",
        # Preferencia: párrafos, líneas, frases, pausas, palabras
        # y, como último recurso, caracteres individuales.
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ": ",
            ", ",
            " ",
            "",
        ],
    )


def chunk_documents(
    documents: list[dict],
    chunk_size: int,
    chunk_overlap: int
) -> list[dict]:
    """Divide documentos y devuelve chunks conformes al contrato.

    los índices son consecutivos dentro de cada documento, incluso cuando
    un PDF llega representado mediante varios LoadedDocument por página.
    Por ejemplo, si un PDF tiene 3 páginas y cada página se representa como un documento separado,
    los chunks resultantes tendrán índices consecutivos a través de todas las páginas del PDF.
    """
    _validate_chunk_config(chunk_size, chunk_overlap)

    if not documents:
        return []

    splitter = _create_splitter(chunk_size, chunk_overlap)
    next_index_by_document: dict[str, int] = defaultdict(int)
    chunks: list[dict] = []

    for document in documents:
        _validate_document(document)

        document_id = str(document["document_id"])
        text = document["text"].strip()

        for chunk_text in splitter.split_text(text):
            chunk_index = next_index_by_document[document_id]
            next_index_by_document[document_id] += 1

            chunk = {
                **document,
                "chunk_id": f"{document_id}__{chunk_index:04d}",
                "chunk_index": chunk_index,
                "text": chunk_text.strip(),
            }

            # ChromaDB no admite None en la metadata.
            if chunk.get("page") is None:
                chunk.pop("page", None)

            chunks.append(chunk)

    return chunks
