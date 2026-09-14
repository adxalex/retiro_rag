"""Streamlit: chat, contexto recuperado y tabla de metricas."""
import time

import streamlit as st

from config import LLM_MODEL, TOP_K
from src.generate import responder

st.set_page_config(page_title="Retiro RAG", page_icon="🌳")


def _inicializar_estado() -> None:
    """Crea las estructuras de sesion la primera vez que carga la pagina."""
    if "historial" not in st.session_state:
        st.session_state.historial = []  # lista de {"pregunta": ..., "respuesta": dict}
    if "metricas" not in st.session_state:
        st.session_state.metricas = []  # lista de filas para la tabla


def _renderizar_historial() -> None:
    """Vuelve a pintar todos los turnos de chat ya realizados."""
    for turno in st.session_state.historial:
        with st.chat_message("user"):
            st.write(turno["pregunta"])
        with st.chat_message("assistant"):
            _renderizar_respuesta(turno["respuesta"])


def _renderizar_respuesta(respuesta: dict) -> None:
    """Muestra respuesta, fuentes y chunks de un resultado de responder()."""
    if respuesta.get("abstuvo"):
        st.warning(respuesta["respuesta"])
    else:
        st.write(respuesta["respuesta"])

    fuentes = respuesta.get("fuentes") or []
    if fuentes:
        st.caption("Fuentes: " + ", ".join(fuentes))

    chunks = respuesta.get("chunks") or []
    if chunks:
        with st.expander(f"Ver {len(chunks)} chunk(s) recuperado(s)"):
            for chunk in chunks:
                st.markdown(f"**{chunk.get('source', 'desconocido')}**")
                st.text(chunk.get("text", ""))


def _procesar_pregunta(pregunta: str) -> None:
    """Llama a responder(), mide tiempo y actualiza historial y metricas."""
    inicio = time.perf_counter()
    try:
        respuesta = responder(pregunta)
        error = None
    except NotImplementedError:
        respuesta = {
            "respuesta": "El equipo todavia no ha implementado responder(). "
                         "Esta pantalla ya esta lista para conectarse en cuanto exista.",
            "fuentes": [],
            "chunks": [],
            "abstuvo": True,
        }
        error = "NotImplementedError"
    tiempo = time.perf_counter() - inicio

    st.session_state.historial.append(
        {"pregunta": pregunta, "respuesta": respuesta})
    st.session_state.metricas.append({
        "pregunta": pregunta,
        "k": TOP_K,
        "n_chunks": len(respuesta.get("chunks") or []),
        "tiempo_s": round(tiempo, 2),
        "modelo": LLM_MODEL,
        "abstuvo": respuesta.get("abstuvo", False),
        "error": error,
    })


def main() -> None:
    """Punto de entrada de la app de Streamlit."""
    st.title("Retiro RAG — Asistente del Parque de El Retiro")
    _inicializar_estado()
    _renderizar_historial()

    pregunta = st.chat_input("Pregunta algo sobre el Parque de El Retiro...")
    if pregunta:
        with st.chat_message("user"):
            st.write(pregunta)
        with st.chat_message("assistant"):
            _procesar_pregunta(pregunta)
            _renderizar_respuesta(st.session_state.historial[-1]["respuesta"])

    if st.session_state.metricas:
        st.subheader("Métricas de las consultas")
        st.dataframe(st.session_state.metricas, use_container_width=True)


if __name__ == "__main__":
    main()