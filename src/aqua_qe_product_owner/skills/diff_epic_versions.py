from ..models import Epic


def diff_epic_versions(antes: Epic, depois: Epic) -> dict:
    """Compara duas versões de um Épico: critérios de aceitação novos/descontinuados, e se objetivo/escopo/valor mudaram."""
    criterios_antes = {(c.given, c.when, c.then) for c in antes.acceptance_criteria}
    criterios_depois = {(c.given, c.when, c.then) for c in depois.acceptance_criteria}

    return {
        "criterios_novos": sorted(criterios_depois - criterios_antes),
        "criterios_descontinuados": sorted(criterios_antes - criterios_depois),
        "objetivo_antes": antes.objective,
        "objetivo_depois": depois.objective,
        "escopo_antes": antes.scope,
        "escopo_depois": depois.scope,
        "valor_antes": antes.value,
        "valor_depois": depois.value,
    }
