"""Generacion de respuesta anclada al contexto recuperado."""


def build_prompt(pregunta: str, chunks: list[dict]) -> str:
    """Construye el prompt con bloques de instrucciones, contexto y pregunta."""
    raise NotImplementedError


def generate_answer(prompt: str) -> str:
    """Llama al LLM elegido con el prompt construido."""
    raise NotImplementedError


def responder(pregunta: str) -> dict:
    """Devuelve {"respuesta": ..., "fuentes": ..., "chunks": ..., "abstuvo": ...} para una pregunta."""
    raise NotImplementedError


def rag_ask(consulta: str) -> str:
    """Envuelve responder() devolviendo solo el texto de la respuesta."""
    raise NotImplementedError
