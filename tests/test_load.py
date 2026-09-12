"""Pruebas de carga para src/load.py."""

from src import load


# ---------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------

def test_markdown_valido_produce_un_documento(tmp_path, monkeypatch):
    archivo = tmp_path / "prueba.md"
    archivo.write_text("Contenido de prueba", encoding="utf-8")
    monkeypatch.setitem(
        load.MANIFIESTO, "prueba.md",
        {"category": "historia", "corpus_group": "historia_monumentos_jardines"},
    )

    documentos = load._leer_markdown(archivo)

    assert len(documentos) == 1
    doc = documentos[0]
    assert doc["document_id"] == "prueba"
    assert doc["category"] == "historia"
    assert doc["corpus_group"] == "historia_monumentos_jardines"
    assert "page" not in doc  # un .md nunca lleva page


def test_markdown_sin_entrada_manifiesto_lanza_error(tmp_path):
    archivo = tmp_path / "no_registrado.md"
    archivo.write_text("Contenido", encoding="utf-8")

    try:
        load._leer_markdown(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "MANIFIESTO" in str(error)


def test_markdown_vacio_lanza_error(tmp_path, monkeypatch):
    archivo = tmp_path / "vacio.md"
    archivo.write_text("   ", encoding="utf-8")
    monkeypatch.setitem(
        load.MANIFIESTO, "vacio.md",
        {"category": "historia", "corpus_group": "historia_monumentos_jardines"},
    )

    try:
        load._leer_markdown(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "vacio" in str(error)


# ---------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------

def _escribir_csv(ruta, filas):
    import csv
    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(
            f, fieldnames=["nombre", "categoria", "corpus_group", "descripcion", "fuente"]
        )
        escritor.writeheader()
        escritor.writerows(filas)


def test_csv_valido_produce_documentos(tmp_path):
    archivo = tmp_path / "datos.csv"
    _escribir_csv(archivo, [
        {"nombre": "Estanque", "categoria": "jardines",
         "corpus_group": "historia_monumentos_jardines",
         "descripcion": "Un estanque grande", "fuente": "x"},
    ])

    documentos = load._leer_csv(archivo)

    assert len(documentos) == 1
    assert documentos[0]["category"] == "jardines"
    assert documentos[0]["document_id"] == "datos-estanque"


def test_csv_categoria_invalida_lanza_error(tmp_path):
    archivo = tmp_path / "malo.csv"
    _escribir_csv(archivo, [
        {"nombre": "X", "categoria": "no_existe",
         "corpus_group": "historia_monumentos_jardines",
         "descripcion": "texto", "fuente": "x"},
    ])

    try:
        load._leer_csv(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "category invalida" in str(error)


def test_csv_sin_filas_validas_lanza_error(tmp_path):
    archivo = tmp_path / "sin_descripcion.csv"
    _escribir_csv(archivo, [
        {"nombre": "X", "categoria": "jardines",
         "corpus_group": "historia_monumentos_jardines",
         "descripcion": "", "fuente": "x"},
    ])

    try:
        load._leer_csv(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "no produjo ningun documento valido" in str(error)


# ---------------------------------------------------------------------
# PDF (se simula PdfReader para no depender de un PDF real)
# ---------------------------------------------------------------------

class _PaginaFalsa:
    def __init__(self, texto):
        self._texto = texto

    def extract_text(self):
        return self._texto


class _PdfReaderFalso:
    def __init__(self, _ruta, paginas):
        self.pages = paginas


def test_pdf_multipagina_mismo_document_id(tmp_path, monkeypatch):
    archivo = tmp_path / "folleto.pdf"
    archivo.write_bytes(b"")  # el contenido no importa, PdfReader esta simulado
    monkeypatch.setitem(
        load.MANIFIESTO, "folleto.pdf",
        {"category": "monumentos", "corpus_group": "historia_monumentos_jardines"},
    )
    paginas = [_PaginaFalsa("Texto pagina 1"), _PaginaFalsa("Texto pagina 2")]
    monkeypatch.setattr(load, "PdfReader", lambda ruta: _PdfReaderFalso(ruta, paginas))

    documentos = load._leer_pdf(archivo)

    assert len(documentos) == 2
    assert documentos[0]["document_id"] == documentos[1]["document_id"] == "folleto"
    assert documentos[0]["page"] == 1
    assert documentos[1]["page"] == 2


def test_pdf_pagina_sin_texto_se_omite(tmp_path, monkeypatch):
    archivo = tmp_path / "escaneado.pdf"
    archivo.write_bytes(b"")
    monkeypatch.setitem(
        load.MANIFIESTO, "escaneado.pdf",
        {"category": "monumentos", "corpus_group": "historia_monumentos_jardines"},
    )
    paginas = [_PaginaFalsa(""), _PaginaFalsa("Solo esta pagina tiene texto")]
    monkeypatch.setattr(load, "PdfReader", lambda ruta: _PdfReaderFalso(ruta, paginas))

    documentos = load._leer_pdf(archivo)

    assert len(documentos) == 1
    assert documentos[0]["page"] == 2


def test_pdf_sin_texto_extraible_lanza_error(tmp_path, monkeypatch):
    archivo = tmp_path / "vacio.pdf"
    archivo.write_bytes(b"")
    monkeypatch.setitem(
        load.MANIFIESTO, "vacio.pdf",
        {"category": "monumentos", "corpus_group": "historia_monumentos_jardines"},
    )
    monkeypatch.setattr(load, "PdfReader", lambda ruta: _PdfReaderFalso(ruta, [_PaginaFalsa("")]))

    try:
        load._leer_pdf(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "no tiene texto extraible" in str(error)


# ---------------------------------------------------------------------
# load_documents: recorrido completo, exclusiones y duplicados
# ---------------------------------------------------------------------

def test_carpeta_excluida_se_ignora(tmp_path, monkeypatch):
    carpeta = tmp_path / "flora_fauna"
    carpeta.mkdir()
    archivo = carpeta / "excluido.md"
    archivo.write_text("Contenido", encoding="utf-8")
    monkeypatch.setitem(
        load.MANIFIESTO, "excluido.md",
        {"category": "flora_fauna", "corpus_group": "flora_fauna_arte_cultura_actividades"},
    )

    documentos = load.load_documents(str(tmp_path))

    assert documentos == []


def test_duplicado_document_id_page_lanza_error(tmp_path):
    archivo = tmp_path / "repetidos.csv"
    _escribir_csv(archivo, [
        {"nombre": "Estanque", "categoria": "jardines",
         "corpus_group": "historia_monumentos_jardines",
         "descripcion": "Primera descripcion", "fuente": "x"},
        {"nombre": "Estanque", "categoria": "jardines",
         "corpus_group": "historia_monumentos_jardines",
         "descripcion": "Segunda descripcion, mismo nombre", "fuente": "x"},
    ])

    try:
        load.load_documents(str(tmp_path))
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "duplicada" in str(error)


def test_formato_no_soportado_lanza_error(tmp_path):
    archivo = tmp_path / "notas.txt"
    archivo.write_text("texto", encoding="utf-8")

    try:
        load._extract_text(archivo)
        assert False, "Debia lanzar ValueError"
    except ValueError as error:
        assert "no soportado" in str(error)