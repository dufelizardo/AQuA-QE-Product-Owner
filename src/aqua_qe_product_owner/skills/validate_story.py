from ..models import UserStory


def validate_story(story: UserStory) -> list[str]:
    """Valida a User Story contra os critérios INVEST e o checklist do agente, retornando os motivos de reprovação (lista vazia = aprovado no checklist)."""
    motivos = []

    # Rastreabilidade (GR-1) — ver docs/agent/validation_checklist.md, item 1.
    if not story.source_reference:
        motivos.append("referência à fonte ausente")

    # Valuable / Negotiable — ator, objetivo e benefício presentes.
    if not story.actor:
        motivos.append("ator ausente")
    if not story.goal:
        motivos.append("objetivo ausente")
    if not story.benefit:
        motivos.append("benefício ausente")

    # Testable — ao menos um critério de aceitação Given-When-Then completo.
    if not story.acceptance_criteria:
        motivos.append("nenhum critério de aceitação identificado")
    elif any(not (c.given and c.when and c.then) for c in story.acceptance_criteria):
        motivos.append("critério de aceitação incompleto (Given/When/Then)")

    return motivos
