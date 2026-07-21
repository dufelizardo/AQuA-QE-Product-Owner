from ..models import PRDDraft


def validate_prd(draft: PRDDraft) -> bool:
    """Valida se o PRD tem contexto/problema, objetivo, escopo, ao menos um requisito funcional e um critério de sucesso."""
    if not draft.context_problem or not draft.objective or not draft.scope:
        return False
    if not draft.functional_requirements:
        return False
    if not draft.success_criteria:
        return False
    return True
