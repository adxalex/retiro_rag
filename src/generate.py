"""Generacion de respuesta anclada al contexto recuperado.

Flujo de responder():

    pregunta -> retrieve() -> compuerta de score -> build_prompt() ->
    generate_answer() -> compuerta del centinela -> dict de salida

La abstencion tiene dos compuertas, porque Chroma siempre devuelve vecinos,
tambien cuando el corpus no contiene la respuesta:

1. Compuerta de retrieval: si el mejor score no llega a SCORE_MINIMO, se
   abstiene sin llamar al LLM. Es determinista y ahorra coste.
2. Compuerta de generacion: el prompt obliga al modelo a devolver el
   centinela SIN_EVIDENCIA cuando el contexto no sostiene la respuesta.

SCORE_MINIMO se lee de .env (RAG_SCORE_MINIMO). El valor por defecto es
provisional: hay que fijarlo comparando la distribucion de scores de las
preguntas respondibles y las de abstencion de queries/, con el indice real y
gemini-embedding-001.
"""

from __future__ import annotations

import os
from typing import Any

from config import LLM_MODEL, TOP_K
from src.gemini_auth import get_gemini_client
from src.retrieve import retrieve

CENTINELA_SIN_EVIDENCIA = "SIN_EVIDENCIA"

MENSAJE_ABSTENCION = (
    "No he encontrado esa informacion en los documentos del Parque del Retiro "
    "que tengo disponibles. Puedes consultarlo en la web municipal "
    "(madrid.es) o en esmadrid.com."
)

# Sin calibrar todavia. 0.0 significa que la compuerta de score no descarta nada
# y la abstencion recae en el centinela del prompt: es preferible a inventarse un
# umbral que silencie respuestas correctas. Calibrarlo con
# scripts/validation/calibrar_umbral.py sobre el indice real y fijarlo en .env.
SCORE_MINIMO = float(os.getenv("RAG_SCORE_MINIMO", "0.0"))

INSTRUCCIONES = f"""Eres un asistente que informa sobre el Parque del Retiro de Madrid.

Reglas:
1. Responde unicamente con la informacion del CONTEXTO. No uses conocimiento propio.
2. Si el contexto no contiene la respuesta, responde exactamente {CENTINELA_SIN_EVIDENCIA} y nada mas.
3. Si el contexto solo responde una parte, responde esa parte y di con claridad que del resto no tienes informacion.
4. Cita las fuentes usando los numeros de fragmento, con este formato: [1], [2].
5. Si el contexto indica que un dato tiene fecha o procede de una fuente no oficial, dilo en la respuesta.
6. Responde en el idioma de la pregunta, en un maximo de seis frases, con un tono claro y cercano.
7. No inventes horarios, precios, distancias ni nombres que no aparezcan en el contexto."""


def _formatear_chunk(numero: int, chunk: dict) -> str:
    """Convierte un chunk en un fragmento numerado y citable del prompt."""
    cabecera = f"[{numero}] fuente: {chunk.get('source', 'desconocida')}"
    if chunk.get("page"):
        cabecera += f", pagina {chunk['page']}"
    if chunk.get("category"):
        cabecera += f", categoria: {chunk['category']}"
    return f"{cabecera}\n{chunk.get('text', '').strip()}"


def build_prompt(pregunta: str, chunks: list[dict]) -> str:
    """Construye el prompt con instrucciones, contexto numerado y pregunta."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia.")

    if chunks:
        contexto = "\n\n".join(
            _formatear_chunk(numero, chunk)
            for numero, chunk in enumerate(chunks, start=1)
        )
    else:
        contexto = "(no se ha recuperado ningun fragmento)"

    return (
        f"{INSTRUCCIONES}\n\n"
        f"CONTEXTO:\n{contexto}\n\n"
        f"PREGUNTA: {pregunta.strip()}\n\n"
        "RESPUESTA:"
    )


def generate_answer(prompt: str, client: Any | None = None) -> str:
    """Llama al LLM con el prompt construido y devuelve el texto."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("El prompt no puede estar vacio.")

    client = client if client is not None else get_gemini_client()
    respuesta = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )
    texto = getattr(respuesta, "text", None)
    if not texto or not texto.strip():
        raise ValueError("El modelo devolvio una respuesta vacia.")
    return texto.strip()


def _fuentes_de(chunks: list[dict]) -> list[str]:
    """Lista de fuentes citables, sin repetir y en el orden recuperado."""
    return list(dict.fromkeys(chunk.get("source", "desconocida") for chunk in chunks))


def _abstencion(pregunta: str, chunks: list[dict], motivo: str) -> dict:
    print(f"[GENERATE] abstencion ({motivo}) para: {pregunta[:60]}")
    return {
        "respuesta": MENSAJE_ABSTENCION,
        "fuentes": [],
        "chunks": chunks,
        "abstuvo": True,
        "motivo_abstencion": motivo,
    }


def responder(
    pregunta: str,
    top_k: int = TOP_K,
    score_minimo: float | None = None,
    collection: Any | None = None,
    client: Any | None = None,
    where: dict | None = None,
) -> dict:
    """Responde una pregunta con RAG, o se abstiene si no hay evidencia.

    Devuelve {"respuesta", "fuentes", "chunks", "abstuvo", "motivo_abstencion"}.
    collection y client son inyectables para los tests.
    """
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia.")

    umbral = SCORE_MINIMO if score_minimo is None else float(score_minimo)
    chunks = retrieve(pregunta, top_k=top_k, collection=collection, where=where)

    if not chunks:
        return _abstencion(pregunta, chunks, "sin_resultados")

    mejor_score = chunks[0]["score"]
    if mejor_score < umbral:
        return _abstencion(
            pregunta, chunks, f"score_bajo ({mejor_score:.3f} < {umbral:.3f})"
        )

    prompt = build_prompt(pregunta, chunks)
    texto = generate_answer(prompt, client=client)

    if CENTINELA_SIN_EVIDENCIA in texto.upper():
        return _abstencion(pregunta, chunks, "el_modelo_no_vio_evidencia")

    print(f"[GENERATE] respuesta generada (score_top1={mejor_score:.3f})")
    return {
        "respuesta": texto,
        "fuentes": _fuentes_de(chunks),
        "chunks": chunks,
        "abstuvo": False,
        "motivo_abstencion": None,
    }


def rag_ask(consulta: str, **kwargs: Any) -> str:
    """Envuelve responder() devolviendo solo el texto de la respuesta."""
    return responder(consulta, **kwargs)["respuesta"]
