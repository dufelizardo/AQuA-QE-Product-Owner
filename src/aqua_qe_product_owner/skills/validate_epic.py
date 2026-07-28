from ..models import Epic


def validate_epic(epic: Epic) -> list[str]:
    """Valida o Epic (título, objetivo, escopo, valor e ao menos um critério de aceitação completo), retornando os motivos de reprovação (lista vazia = aprovado no checklist)."""
    motivos = []

    if not epic.title:
        motivos.append("título ausente")
    if not epic.objective:
        motivos.append("objetivo ausente")
    if not epic.scope:
        motivos.append("escopo ausente")
    if not epic.value:
        motivos.append("valor ausente")

    if not epic.acceptance_criteria:
        motivos.append("nenhum critério de aceitação identificado")
    elif any(not (c.given and c.when and c.then) for c in epic.acceptance_criteria):
        motivos.append("critério de aceitação incompleto (Given/When/Then)")

    return motivos
