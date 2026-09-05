"""Carga de documentos crudos desde DATA_DIR (PDF, CSV, TXT/MD).

Punto de extension futuro: '_extract_text' es el UNICO lugar que decide como
se saca texto de un archivo. Cuando se anada el document_gate + router de
parsers (pypdf vs docling), solo hay que reemplazar el cuerpo de esta
funcion para que delegue en 'src/parsing/' -- load_documents() y todo lo
que viene despues (chunk, embed, index...) no cambian.
"""
from pathlib import Path

from pypdf import PdfReader
import pandas as pd


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texto = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not texto.strip():
        print(f"[AVISO] '{path.name}' no tiene texto extraible (posible PDF escaneado sin OCR). Se omite.")
        return ""
    return texto


def _extract_csv(path: Path) -> str:
    df = pd.read_csv(path)
    # Cada fila se convierte en una linea de texto tipo "columna: valor, columna: valor"
    filas = df.apply(lambda row: ", ".join(f"{c}: {row[c]}" for c in df.columns), axis=1)
    return "\n".join(filas)


def _extract_texto_plano(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


_EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".csv": _extract_csv,
    ".txt": _extract_texto_plano,
    ".md": _extract_texto_plano,
}


def _extract_text(path: Path) -> str:
    """Unico punto que decide como convertir un archivo en texto.

    HOY: dispatch simple por extension (pypdf / pandas / lectura directa).
    FUTURO: si existe 'src/parsing/', delegar aqui en el document_gate +
    router (pypdf_parser vs docling_parser) sin cambiar la firma ni el
    valor de retorno (sigue siendo un str).
    """
    extractor = _EXTRACTORS.get(path.suffix.lower())
    if extractor is None:
        raise ValueError(f"Formato no soportado: {path.suffix}")
    return extractor(path)


def load_documents(data_dir: str) -> list[dict]:
    """Carga todos los archivos soportados de data_dir.

    Devuelve una lista de {"text": ..., "source": <nombre de fichero>}.
    Este contrato de salida es estable: no debe cambiar aunque cambie
    como se extrae el texto por dentro.
    """
    documentos = []
    for path in sorted(Path(data_dir).glob("*")):
        if path.name.startswith("."):
            continue
        if path.suffix.lower() not in _EXTRACTORS:
            print(f"[AVISO] Formato no soportado, se omite: {path.name}")
            continue
        try:
            texto = _extract_text(path)
        except Exception as e:
            print(f"[ERROR] No se pudo leer '{path.name}': {e}")
            continue
        if texto.strip():
            documentos.append({"text": texto, "source": path.name})
    return documentos
