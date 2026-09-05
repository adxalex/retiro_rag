"""CLI del sistema RAG: indexar el corpus (offline) y preguntar (online)."""
import argparse


def cmd_index(recreate: bool = False) -> None:
    """Carga, chunkea e indexa el corpus completo."""
    raise NotImplementedError


def cmd_query(pregunta: str) -> None:
    """Ejecuta solo retrieval y muestra los chunks recuperados."""
    raise NotImplementedError


def cmd_ask(pregunta: str) -> None:
    """Ejecuta el flujo RAG completo y muestra la respuesta."""
    raise NotImplementedError


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
