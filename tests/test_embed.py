from copy import deepcopy
from types import SimpleNamespace

import pytest

import src.embed as embed_module
from src.embed import embed_chunks, embed_query, limitar_chunks


def make_chunk(index: int, group: str = "grupo_a") -> dict:
    """Crea un chunk mínimo válido para las pruebas."""
    return {
        "chunk_id": f"documento__{index:04d}",
        "document_id": "documento",
        "text": f"Texto del fragmento número {index}.",
        "source": "documento.md",
        "chunk_index": index,
        "category": "flora_fauna",
        "corpus_group": group,
    }


class FakeModels:
    """Simula client.models y registra las llamadas realizadas."""

    def __init__(self):
        self.calls = []

    def embed_content(self, *, model, contents, config):
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )

        embeddings = []
        for content in contents:
            text = content.parts[0].text
            embeddings.append(
                SimpleNamespace(
                    values=[
                        float(len(text)),
                        1.0,
                        2.0,
                    ]
                )
            )

        return SimpleNamespace(embeddings=embeddings)


class FakeClient:
    """Cliente Gemini falso con la misma interfaz usada por embed.py."""

    def __init__(self, models=None):
        self.models = models or FakeModels()


class IncompleteModels(FakeModels):
    """Simula que Gemini devuelve menos vectores de los solicitados."""

    def embed_content(self, *, model, contents, config):
        result = super().embed_content(
            model=model,
            contents=contents,
            config=config,
        )
        result.embeddings = result.embeddings[:-1]
        return result


class InconsistentModels(FakeModels):
    """Simula vectores con dimensiones diferentes."""

    def embed_content(self, *, model, contents, config):
        result = super().embed_content(
            model=model,
            contents=contents,
            config=config,
        )
        if len(result.embeddings) >= 2:
            result.embeddings[1].values = [1.0, 2.0]
        return result


class NonFiniteModels(FakeModels):
    """Simula un embedding que contiene un valor NaN."""

    def embed_content(self, *, model, contents, config):
        result = super().embed_content(
            model=model,
            contents=contents,
            config=config,
        )
        result.embeddings[0].values = [1.0, float("nan"), 2.0]
        return result


class MissingEmbeddingsModels(FakeModels):
    """Simula una respuesta de Gemini sin el campo embeddings."""

    def embed_content(self, *, model, contents, config):
        self.calls.append(
            {
                "model": model,
                "contents": contents,
                "config": config,
            }
        )
        return SimpleNamespace()


# Comprueba que una entrada vacía no realiza llamadas al proveedor.
def test_empty_chunks_return_empty_list_without_api_call():
    client = FakeClient()

    result = embed_chunks([], client=client)

    assert result == []
    assert client.models.calls == []


# Comprueba que cada chunk recibe exactamente un vector.
def test_embed_chunks_adds_one_vector_per_chunk():
    chunks = [make_chunk(0), make_chunk(1), make_chunk(2)]
    client = FakeClient()

    result = embed_chunks(chunks, client=client)

    assert len(result) == len(chunks)
    assert all("vector" in chunk for chunk in result)
    assert all(len(chunk["vector"]) == 3 for chunk in result)


# Comprueba que la función conserva el orden de entrada.
def test_embed_chunks_preserves_input_order():
    chunks = [make_chunk(0), make_chunk(1), make_chunk(2)]
    client = FakeClient()

    result = embed_chunks(chunks, client=client)

    assert [chunk["chunk_id"] for chunk in result] == [
        chunk["chunk_id"]
        for chunk in chunks
    ]


# Comprueba que embed_chunks no modifica los diccionarios originales.
def test_embed_chunks_does_not_mutate_input():
    chunks = [make_chunk(0), make_chunk(1)]
    original = deepcopy(chunks)
    client = FakeClient()

    result = embed_chunks(chunks, client=client)

    assert chunks == original
    assert result is not chunks
    assert all("vector" not in chunk for chunk in chunks)


# Comprueba que la metadata original se conserva en la salida.
def test_embed_chunks_preserves_metadata():
    chunks = [make_chunk(0)]
    client = FakeClient()

    result = embed_chunks(chunks, client=client)

    for field in (
        "chunk_id",
        "document_id",
        "text",
        "source",
        "chunk_index",
        "category",
        "corpus_group",
    ):
        assert result[0][field] == chunks[0][field]


# Comprueba que se registran el modelo y la dimensión del embedding.
def test_embed_chunks_adds_embedding_metadata():
    chunks = [make_chunk(0)]
    client = FakeClient()

    result = embed_chunks(chunks, client=client)

    assert result[0]["embedding_model"] == embed_module.EMBEDDING_MODEL
    assert result[0]["embedding_dimension"] == 3


# Comprueba que los textos se distribuyen según el tamaño de lote.
def test_embed_chunks_uses_configured_batch_size(monkeypatch):
    monkeypatch.setattr(embed_module, "EMBED_BATCH_SIZE", 2)
    chunks = [make_chunk(index) for index in range(5)]
    client = FakeClient()

    embed_chunks(chunks, client=client)

    assert len(client.models.calls) == 3
    assert [
        len(call["contents"])
        for call in client.models.calls
    ] == [2, 2, 1]


# Comprueba que los chunks usan el tipo de tarea documental.
def test_embed_chunks_uses_document_task_type():
    client = FakeClient()

    embed_chunks([make_chunk(0)], client=client)

    config = client.models.calls[0]["config"]
    assert config.task_type == "RETRIEVAL_DOCUMENT"


# Comprueba que una consulta usa el tipo de tarea de retrieval.
def test_embed_query_uses_query_task_type():
    client = FakeClient()

    vector = embed_query("¿Qué árboles hay en El Retiro?", client=client)

    config = client.models.calls[0]["config"]
    assert config.task_type == "RETRIEVAL_QUERY"
    assert len(vector) == 3


# Comprueba que las consultas vacías o no textuales se rechazan.
@pytest.mark.parametrize("query", ["", "   ", None, 123])
def test_embed_query_rejects_invalid_text(query):
    with pytest.raises(ValueError):
        embed_query(query, client=FakeClient())


# Comprueba que los chunks deben ser diccionarios.
def test_embed_chunks_rejects_non_dictionary_chunk():
    with pytest.raises(TypeError):
        embed_chunks(["chunk inválido"], client=FakeClient())


# Comprueba que cada chunk contiene los campos mínimos de embeddings.
@pytest.mark.parametrize(
    "missing_field",
    ["chunk_id", "document_id", "text"],
)
def test_embed_chunks_rejects_missing_required_field(missing_field):
    chunk = make_chunk(0)
    chunk.pop(missing_field)

    with pytest.raises(ValueError):
        embed_chunks([chunk], client=FakeClient())


# Comprueba que los campos mínimos no estén vacíos.
@pytest.mark.parametrize(
    "field",
    ["chunk_id", "document_id", "text"],
)
def test_embed_chunks_rejects_empty_required_field(field):
    chunk = make_chunk(0)
    chunk[field] = "   "

    with pytest.raises(ValueError):
        embed_chunks([chunk], client=FakeClient())


# Comprueba que un tamaño de lote inválido detiene la operación.
@pytest.mark.parametrize("batch_size", [0, -1, True, "2"])
def test_embed_chunks_rejects_invalid_batch_size(
    monkeypatch,
    batch_size,
):
    monkeypatch.setattr(
        embed_module,
        "EMBED_BATCH_SIZE",
        batch_size,
    )

    with pytest.raises(ValueError):
        embed_chunks([make_chunk(0)], client=FakeClient())


# Comprueba que se detecta la pérdida de embeddings en una respuesta.
def test_embed_chunks_rejects_missing_vectors():
    client = FakeClient(models=IncompleteModels())

    with pytest.raises(
        RuntimeError,
        match="Falló el lote de embeddings",
    ):
        embed_chunks([make_chunk(0), make_chunk(1)], client=client)


# Comprueba que no se aceptan vectores con dimensiones diferentes.
def test_embed_chunks_rejects_inconsistent_dimensions():
    client = FakeClient(models=InconsistentModels())

    with pytest.raises(
        RuntimeError,
        match="Falló el lote de embeddings",
    ):
        embed_chunks([make_chunk(0), make_chunk(1)], client=client)


# Comprueba que no se aceptan valores NaN o infinitos.
def test_embed_chunks_rejects_non_finite_values():
    client = FakeClient(models=NonFiniteModels())

    with pytest.raises(
        RuntimeError,
        match="Falló el lote de embeddings",
    ):
        embed_chunks([make_chunk(0)], client=client)


# Comprueba que se detecta una respuesta sin embeddings.
def test_embed_chunks_rejects_response_without_embeddings():
    client = FakeClient(models=MissingEmbeddingsModels())

    with pytest.raises(
        RuntimeError,
        match="Falló el lote de embeddings",
    ):
        embed_chunks([make_chunk(0)], client=client)


# Comprueba que None conserva todos los chunks sin reutilizar la lista.
def test_limitar_chunks_with_none_keeps_all_chunks():
    chunks = [make_chunk(0), make_chunk(1)]

    result = limitar_chunks(chunks, max_chunks=None)

    assert result == chunks
    assert result is not chunks


# Comprueba que un límite cero produce una selección vacía.
def test_limitar_chunks_with_zero_returns_empty_list():
    chunks = [make_chunk(0), make_chunk(1)]

    result = limitar_chunks(chunks, max_chunks=0)

    assert result == []


# Comprueba que el límite respeta exactamente el máximo solicitado.
def test_limitar_chunks_respects_maximum():
    chunks = [
        make_chunk(0, group="grupo_a"),
        make_chunk(1, group="grupo_a"),
        make_chunk(2, group="grupo_b"),
        make_chunk(3, group="grupo_b"),
    ]

    result = limitar_chunks(chunks, max_chunks=3)

    assert len(result) == 3


# Comprueba que, si hay cupo, ningún grupo queda sin representación.
def test_limitar_chunks_preserves_groups_when_capacity_allows():
    chunks = [
        make_chunk(0, group="grupo_a"),
        make_chunk(1, group="grupo_a"),
        make_chunk(2, group="grupo_b"),
        make_chunk(3, group="grupo_b"),
    ]

    result = limitar_chunks(chunks, max_chunks=2)

    assert {
        chunk["corpus_group"]
        for chunk in result
    } == {"grupo_a", "grupo_b"}


# Comprueba que los límites negativos o no enteros se rechazan.
@pytest.mark.parametrize("max_chunks", [-1, True, 2.5, "2"])
def test_limitar_chunks_rejects_invalid_limit(max_chunks):
    with pytest.raises((TypeError, ValueError)):
        limitar_chunks([make_chunk(0)], max_chunks=max_chunks)


# Comprueba que el nombre del campo de agrupación sea válido.
@pytest.mark.parametrize("agrupar_por", ["", "   ", None])
def test_limitar_chunks_rejects_invalid_group_field(agrupar_por):
    with pytest.raises(ValueError):
        limitar_chunks(
            [make_chunk(0)],
            max_chunks=1,
            agrupar_por=agrupar_por,
        )
