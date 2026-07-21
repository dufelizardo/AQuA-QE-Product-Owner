import os

from ..models import PRDDraft
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um revisor crítico de PRDs, independente de quem os gerou. Avalie "
    "se o objetivo, o escopo e os requisitos são claros, coerentes entre si e "
    "sustentam os critérios de sucesso definidos. Aponte problemas reais; "
    "nunca aprove um PRD com objetivo vago ou escopo incoerente com os "
    "requisitos listados."
)

_DEFAULT_REVIEW_MODEL = "phi4"


def review_prd(draft: PRDDraft) -> dict:
    """Revisa o PRD com um LLM diferente do gerador, apontando problemas de clareza e coerência."""
    modelo = os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)
    prompt = (
        f"Contexto/problema: {draft.context_problem}\n"
        f"Objetivo: {draft.objective}\n"
        f"Público-alvo: {draft.target_audience}\n"
        f"Escopo: {draft.scope}\n"
        f"Fora de escopo: {draft.out_of_scope}\n"
        f"Requisitos funcionais: {draft.functional_requirements}\n"
        f"Requisitos não funcionais: {draft.non_functional_requirements}\n"
        f"Critérios de sucesso: {draft.success_criteria}\n"
        f"Riscos e premissas: {draft.risks_assumptions}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
