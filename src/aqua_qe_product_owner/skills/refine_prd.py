from ..models import PRDDraft
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você refina um PRD existente com base nas respostas que quem propôs a "
    "ideia deu às perguntas de esclarecimento levantadas por um revisor. "
    "Baseie-se apenas no PRD atual e nas respostas fornecidas; nunca invente "
    "requisito, risco ou critério que não tenha sido informado neles. "
    "Responda sempre em português, mesmo que o PRD atual contenha trechos em "
    "outro idioma."
)


def refine_prd(draft: PRDDraft, respostas: list[dict]) -> PRDDraft:
    """Reescreve os campos do PRD usando as respostas às perguntas de esclarecimento."""
    perguntas_respostas = [
        f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas
    ]

    prompt = (
        f"Contexto/problema atual: {draft.context_problem}\n"
        f"Objetivo atual: {draft.objective}\n"
        f"Escopo atual: {draft.scope}\n"
        f"Fora de escopo atual: {draft.out_of_scope}\n"
        f"Requisitos funcionais atuais: {draft.functional_requirements}\n"
        f"Requisitos não funcionais atuais: {draft.non_functional_requirements}\n"
        f"Critérios de sucesso atuais: {draft.success_criteria}\n"
        f"Riscos e premissas atuais: {draft.risks_assumptions}\n\n"
        "Respostas às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva os campos do PRD incorporando essas respostas, "
        "resolvendo as lacunas apontadas.\n\n"
        'Responda apenas em JSON: {"contexto_problema": "...", "objetivo": "...", '
        '"publico_alvo": "...", "escopo": "...", "fora_de_escopo": "...", '
        '"requisitos_funcionais": ["..."], "requisitos_nao_funcionais": ["..."], '
        '"criterios_sucesso": ["..."], "riscos_premissas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    draft.context_problem = dados.get("contexto_problema") or draft.context_problem
    draft.objective = dados.get("objetivo") or draft.objective
    draft.target_audience = dados.get("publico_alvo") or draft.target_audience
    draft.scope = dados.get("escopo") or draft.scope
    draft.out_of_scope = dados.get("fora_de_escopo") or draft.out_of_scope
    draft.functional_requirements = dados.get("requisitos_funcionais") or draft.functional_requirements
    draft.non_functional_requirements = (
        dados.get("requisitos_nao_funcionais") or draft.non_functional_requirements
    )
    draft.success_criteria = dados.get("criterios_sucesso") or draft.success_criteria
    draft.risks_assumptions = dados.get("riscos_premissas") or draft.risks_assumptions
    return draft
