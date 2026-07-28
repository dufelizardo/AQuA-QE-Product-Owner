from ..models import Epic
from ..services.llm_service import complete_json, reviewer_model

_SYSTEM_COM_STORIES = (
    "Você é um revisor crítico de Épicos, independente de quem os gerou. "
    "Avalie se o objetivo, o escopo e o valor de negócio estão claros e "
    "coerentes com as User Stories que o Épico agrupa, e se os critérios de "
    "aceitação de alto nível fazem sentido. Aponte problemas reais; nunca "
    "aprove um Épico com objetivo vago ou incoerente com suas stories."
)

_SYSTEM_SEM_STORIES = (
    "Você é um revisor crítico de Épicos, independente de quem os gerou. "
    "Este Épico ainda está na fase de definição de escopo — por design, "
    "nenhuma User Story foi gerada ainda. Avalie apenas se o objetivo, o "
    "escopo e o valor de negócio estão claros e coerentes entre si, e se os "
    "critérios de aceitação de alto nível fazem sentido. Nunca aponte a "
    "ausência de User Stories como um problema — isso é esperado nesta fase."
)

def review_epic(epic: Epic) -> dict:
    """Revisa o Epic com um LLM diferente do gerador — coerência com as stories agrupadas quando já existem, ou só clareza interna (título/objetivo/escopo/valor/critérios) na fase de shape, antes de qualquer story existir."""
    modelo = reviewer_model()
    criterios = [
        {"dado": c.given, "quando": c.when, "entao": c.then} for c in epic.acceptance_criteria
    ]

    if epic.stories:
        system = _SYSTEM_COM_STORIES
        resumo_stories = [{"titulo": story.title, "objetivo": story.goal} for story in epic.stories]
        prompt = (
            f"Título: {epic.title}\n"
            f"Objetivo: {epic.objective}\n"
            f"Escopo: {epic.scope}\n"
            f"Valor: {epic.value}\n"
            f"User Stories agrupadas neste Épico: {resumo_stories}\n"
            f"Critérios de aceitação: {criterios}\n\n"
            'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
        )
    else:
        system = _SYSTEM_SEM_STORIES
        prompt = (
            f"Título: {epic.title}\n"
            f"Objetivo: {epic.objective}\n"
            f"Escopo: {epic.scope}\n"
            f"Valor: {epic.value}\n"
            f"Critérios de aceitação: {criterios}\n\n"
            'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
        )

    dados = complete_json(prompt, system=system, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
