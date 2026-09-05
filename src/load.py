"""Carga de documentos crudos desde DATA_DIR (PDF, CSV, TXT/MD)."""
from pathlib import Path


def _extract_text(path: Path) -> str:
    """Convierte un archivo en texto plano segun su formato."""
    raise NotImplementedError


def load_documents(data_dir: str) -> list[dict]:
    """Carga los documentos de data_dir. Devuelve [{"text": ..., "source": ...}, ...]."""
    raise NotImplementedError
