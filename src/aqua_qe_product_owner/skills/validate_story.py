from ..models import UserStory


def validate_story(story: UserStory) -> bool:
    """Valida se a User Story atende aos critérios INVEST e ao checklist do agente."""
    # Rastreabilidade (GR-1) — ver docs/agent/validation_checklist.md, item 1.
    if not story.source_reference:
        return False

    # Valuable / Negotiable — ator, objetivo e benefício presentes.
    if not story.actor or not story.goal or not story.benefit:
        return False

    # Testable — ao menos um critério de aceitação Given-When-Then completo.
    if not story.acceptance_criteria:
        return False
    for criterio in story.acceptance_criteria:
        if not (criterio.given and criterio.when and criterio.then):
            return False

    return True
