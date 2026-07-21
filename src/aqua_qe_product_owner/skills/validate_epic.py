from ..models import Epic


def validate_epic(epic: Epic) -> bool:
    """Valida se o Epic tem título, objetivo, escopo, valor e ao menos um critério de aceitação completo."""
    if not epic.title or not epic.objective or not epic.scope or not epic.value:
        return False

    if not epic.acceptance_criteria:
        return False
    for criterio in epic.acceptance_criteria:
        if not (criterio.given and criterio.when and criterio.then):
            return False

    return True
