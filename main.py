"""CLI del sistema RAG - Parque de El Retiro.

Uso previsto:
    python main.py --index                    # indexar el corpus (offline)
    python main.py --index --recreate-index    # borrar y reconstruir el indice desde cero
    python main.py --query "pregunta"          # solo retrieval, sin generacion
    python main.py --ask "pregunta"            # respuesta RAG completa

TODO: separar claramente offline (--index) de online (--query / --ask).
"""
import argparse

import config
from src.load import load_documents
from src.chunk import chunk_documents
from src.index import build_index
from src.retrieve import retrieve
from src.generate import responder


def cmd_index(recreate: bool = False):
    documents = load_documents(config.DATA_DIR)
    chunks = chunk_documents(documents, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    build_index(chunks, config.CHROMA_DIR, config.COLLECTION_NAME, recreate=recreate)
    print(f"Indexados {len(chunks)} chunks en '{config.COLLECTION_NAME}' (recreate={recreate}).")


def cmd_query(pregunta: str):
    resultados = retrieve(pregunta, config.TOP_K)
    for r in resultados:
        print(f"[{r['source']}] {r['text'][:200]}...")


def cmd_ask(pregunta: str):
    resultado = responder(pregunta)
    print(resultado["respuesta"])
    print("Fuentes:", resultado.get("fuentes"))


def main():
    parser = argparse.ArgumentParser(description="RAG - Parque de El Retiro")
    parser.add_argument("--index", action="store_true", help="Indexar el corpus")
    parser.add_argument("--recreate-index", action="store_true", help="Borrar y reconstruir el indice desde cero")
    parser.add_argument("--query", type=str, help="Solo retrieval, sin generacion")
    parser.add_argument("--ask", type=str, help="Respuesta RAG completa")
    args = parser.parse_args()

    if args.index:
        cmd_index(recreate=args.recreate_index)
    elif args.query:
        cmd_query(args.query)
    elif args.ask:
        cmd_ask(args.ask)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
