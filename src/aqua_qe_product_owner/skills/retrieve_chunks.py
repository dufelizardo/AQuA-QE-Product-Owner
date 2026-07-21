from ..services.rag_service import search


def retrieve_chunks(consulta: str, k: int = 5) -> list[str]:
    """Recupera os trechos de conhecimento mais relevantes para a consulta."""
    return search(consulta, k=k)
