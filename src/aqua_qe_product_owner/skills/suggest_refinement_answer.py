from ..services.rag_service import find_similar_refinement_answers


def suggest_refinement_answer(pergunta: str) -> dict | None:
    """Sugere a resposta de refinamento mais parecida já dada antes (memória institucional),
    ou None se nenhuma resposta parecida existir ainda. Nunca aplicada automaticamente — só
    exibida como sugestão editável antes do humano responder."""
    resultados = find_similar_refinement_answers(pergunta, k=1)
    return resultados[0] if resultados else None
