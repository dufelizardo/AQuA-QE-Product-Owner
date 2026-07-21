import os

from ..models import Epic
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um revisor crítico de Épicos, independente de quem os gerou. "
    "Avalie se o objetivo, o escopo e o valor de negócio estão claros e "
    "coerentes com as User Stories que o Épico agrupa, e se os critérios de "
    "aceitação de alto nível fazem sentido. Aponte problemas reais; nunca "
    "aprove um Épico com objetivo vago ou incoerente com suas stories."
)

_DEFAULT_REVIEW_MODEL = "phi4"


def review_epic(epic: Epic) -> dict:
    """Revisa o Epic com um LLM diferente do gerador, apontando problemas de clareza e coerência com as stories agrupadas."""
    modelo = os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)
    resumo_stories = [{"titulo": story.title, "objetivo": story.goal} for story in epic.stories]
    criterios = [
        {"dado": c.given, "quando": c.when, "entao": c.then} for c in epic.acceptance_criteria
    ]
    prompt = (
        f"Título: {epic.title}\n"
        f"Objetivo: {epic.objective}\n"
        f"Escopo: {epic.scope}\n"
        f"Valor: {epic.value}\n"
        f"User Stories agrupadas neste Épico: {resumo_stories}\n"
        f"Critérios de aceitação: {criterios}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
