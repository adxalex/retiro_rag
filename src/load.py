"""Carga de documentos crudos desde DATA_DIR (PDF, CSV, TXT/MD)."""
from pathlib import Path

from pypdf import PdfReader
import pandas as pd


def _load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texto = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not texto.strip():
        print(f"[AVISO] '{path.name}' no tiene texto extraible (posible PDF escaneado sin OCR). Se omite.")
        return ""
    return texto


def _load_csv(path: Path) -> str:
    df = pd.read_csv(path)
    # Cada fila se convierte en una linea de texto tipo "columna: valor, columna: valor"
    filas = df.apply(lambda row: ", ".join(f"{c}: {row[c]}" for c in df.columns), axis=1)
    return "\n".join(filas)


def _load_texto(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


PARSERS = {
    ".pdf": _load_pdf,
    ".csv": _load_csv,
    ".txt": _load_texto,
    ".md": _load_texto,
}


def load_documents(data_dir: str) -> list[dict]:
    documentos = []
    for path in sorted(Path(data_dir).glob("*")):
        if path.name.startswith("."):
            continue
        parser = PARSERS.get(path.suffix.lower())
        if parser is None:
            print(f"[AVISO] Formato no soportado, se omite: {path.name}")
            continue
        try:
            texto = parser(path)
        except Exception as e:
            print(f"[ERROR] No se pudo leer '{path.name}': {e}")
            continue
        if texto.strip():
            documentos.append({"text": texto, "source": path.name})
    return documentos
