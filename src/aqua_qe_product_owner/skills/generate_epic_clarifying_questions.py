from ..models import Epic
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você transforma apontamentos de revisão de um Épico em perguntas diretas "
    "e acionáveis para quem propôs a ideia responder. Cada pergunta deve "
    "buscar exatamente a informação que falta para resolver um apontamento, "
    "sem repetir a crítica literalmente."
)


def generate_epic_clarifying_questions(epic: Epic) -> list[str]:
    """Gera perguntas de esclarecimento a partir dos apontamentos da revisão do Épico."""
    if not epic.review_notes:
        return []

    prompt = (
        f"Título: {epic.title}\nObjetivo: {epic.objective}\nEscopo: {epic.scope}\n"
        f"Valor: {epic.value}\n\n"
        f"Apontamentos do revisor: {epic.review_notes}\n\n"
        "Para cada apontamento, gere uma pergunta direta que obtenha a "
        "informação necessária para resolvê-lo.\n"
        'Responda apenas em JSON: {"perguntas": ["...", "..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [_texto_da_pergunta(pergunta) for pergunta in dados.get("perguntas", [])]


_CHAVES_TEXTO = ("texto", "pergunta", "question", "text")


def _texto_da_pergunta(pergunta: str | dict) -> str:
    """Normaliza uma pergunta retornada pelo LLM, que às vezes vem como objeto (com chaves variáveis) em vez de string simples."""
    if not isinstance(pergunta, dict):
        return str(pergunta)

    por_chave_minuscula = {chave.lower(): valor for chave, valor in pergunta.items()}
    for chave in _CHAVES_TEXTO:
        if chave in por_chave_minuscula:
            return str(por_chave_minuscula[chave])
    return str(pergunta)
