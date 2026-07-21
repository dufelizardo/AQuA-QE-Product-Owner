from ..models import UserStory


def diff_story_versions(antes: UserStory, depois: UserStory) -> dict:
    """Compara duas versões de uma User Story e identifica regras de negócio e critérios de aceitação novos e descontinuados."""
    regras_antes = {regra.description for regra in antes.business_rules}
    regras_depois = {regra.description for regra in depois.business_rules}
    criterios_antes = {(c.given, c.when, c.then) for c in antes.acceptance_criteria}
    criterios_depois = {(c.given, c.when, c.then) for c in depois.acceptance_criteria}

    return {
        "regras_novas": sorted(regras_depois - regras_antes),
        "regras_descontinuadas": sorted(regras_antes - regras_depois),
        "criterios_novos": sorted(criterios_depois - criterios_antes),
        "criterios_descontinuados": sorted(criterios_antes - criterios_depois),
    }
