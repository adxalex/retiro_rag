"""Logging basico de las consultas realizadas al sistema."""


def log_query(pregunta: str, k: int, n_chunks: int, tiempo: float, modelo: str, abstuvo: bool = False) -> None:
    """Registra una consulta: pregunta, k, numero de chunks, tiempo, modelo y si hubo abstencion."""
    raise NotImplementedError
