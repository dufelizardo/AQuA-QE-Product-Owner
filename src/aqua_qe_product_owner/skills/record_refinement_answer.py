from ..services.rag_service import record_refinement_answer as _record_refinement_answer


def record_refinement_answer(pergunta: str, resposta: str, tipo_artefato: str) -> None:
    """Grava uma resposta de refinamento dada pelo humano, para reaproveitamento futuro como
    sugestão editável em ciclos de refinamento posteriores."""
    _record_refinement_answer(pergunta, resposta, tipo_artefato)
