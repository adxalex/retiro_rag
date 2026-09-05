"""Generacion de respuesta anclada al contexto recuperado.

Responsable: Alex (Parte 3), sobre la salida de retrieve.py.
TODO:
- build_prompt(pregunta: str, chunks: list[dict]) -> str
  Bloques claros: instrucciones + --- CONTEXTO --- + --- PREGUNTA ---
- generate_answer(prompt: str) -> str
  Llamada al LLM elegido.
- responder(pregunta: str) -> dict
  {"respuesta": ..., "fuentes": [...], "chunks": [...], "abstuvo": bool}
- rag_ask(consulta: str) -> str
  Wrapper de responder() para reutilizar en el proyecto de Agentes.
"""


def build_prompt(pregunta, chunks):
    raise NotImplementedError


def generate_answer(prompt):
    raise NotImplementedError


def responder(pregunta):
    raise NotImplementedError


def rag_ask(consulta):
    raise NotImplementedError
