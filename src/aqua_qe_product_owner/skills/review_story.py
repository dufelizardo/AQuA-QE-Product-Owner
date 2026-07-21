import os

from ..models import UserStory
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um revisor crítico de User Stories, independente de quem as gerou. "
    "Avalie rigorosamente contra os critérios INVEST (Independent, Negotiable, "
    "Valuable, Estimable, Small, Testable) e aponte problemas reais. Nunca "
    "aprove uma história com critérios de aceitação vagos ou não testáveis."
)

_DEFAULT_REVIEW_MODEL = "phi4"


def review_story(story: UserStory) -> dict:
    """Revisa a User Story com um LLM diferente do gerador, apontando problemas de qualidade (INVEST)."""
    modelo = os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)
    criterios = [
        {"given": c.given, "when": c.when, "then": c.then} for c in story.acceptance_criteria
    ]
    prompt = (
        "Revise a User Story abaixo quanto aos critérios INVEST.\n\n"
        f"Ator: {story.actor}\n"
        f"Objetivo: {story.goal}\n"
        f"Benefício: {story.benefit}\n"
        f"Descrição: {story.description}\n"
        f"Critérios de aceitação: {criterios}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
