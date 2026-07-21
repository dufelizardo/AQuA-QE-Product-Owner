from ..models import AcceptanceCriteria, UserStory
from ..services.llm_service import complete_json
from .generate_user_story import finalize_story

_SYSTEM = (
    "Você complementa critérios de aceitação de uma User Story existente, no "
    "formato Given-When-Then, cobrindo lacunas como casos de erro e casos de "
    "borda. Baseie-se apenas nas informações fornecidas; nunca invente ator, "
    "objetivo ou regra que não tenha sido informado."
)


def generate_acceptance(story: UserStory) -> UserStory:
    """Gera ou complementa os critérios de aceitação de uma User Story já existente."""
    existentes = [
        {"dado": c.given, "quando": c.when, "entao": c.then} for c in story.acceptance_criteria
    ]
    prompt = (
        f"Ator: {story.actor}\n"
        f"Objetivo: {story.goal}\n"
        f"Benefício: {story.benefit}\n"
        f"Descrição: {story.description}\n"
        f"Critérios de aceitação já existentes: {existentes}\n\n"
        "Gere critérios de aceitação adicionais que cubram lacunas (casos de "
        "erro, casos de borda) ainda não cobertas pelos critérios existentes.\n"
        'Responda apenas em JSON: {"criterios_aceitacao": [{"cenario": "...", '
        '"dado": "...", "quando": "...", "entao": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    inicio = len(story.acceptance_criteria) + 1
    novos = [
        AcceptanceCriteria(
            id=f"AC-{inicio + i:03d}",
            scenario=criterio.get("cenario", ""),
            given=criterio.get("dado", ""),
            when=criterio.get("quando", ""),
            then=criterio.get("entao", ""),
        )
        for i, criterio in enumerate(dados.get("criterios_aceitacao", []))
    ]
    story.acceptance_criteria = story.acceptance_criteria + novos
    return finalize_story(story)
