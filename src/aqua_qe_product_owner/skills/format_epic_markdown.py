from ..models import Epic


def _lista_requisitos(epic: Epic) -> str:
    if not epic.requirements:
        return "(nenhum)"
    linhas = []
    for requisito in epic.requirements:
        linhas.append(f"- {requisito.text}")
        linhas.append(f"  > {requisito.source_reference}")
    return "\n".join(linhas)


def _lista_criterios(epic: Epic) -> str:
    if not epic.acceptance_criteria:
        return "(nenhum)"
    blocos = []
    for criterio in epic.acceptance_criteria:
        blocos += [
            f"### {criterio.scenario}",
            "",
            f"- Given {criterio.given}",
            f"- When {criterio.when}",
            f"- Then {criterio.then}",
            "",
        ]
    return "\n".join(blocos).rstrip()


def format_epic_markdown(epic: Epic) -> str:
    """Formata o Epic (estágio shape) em Markdown, invertível por parse_epic_markdown.

    Captura só título/objetivo/escopo/valor/critérios de aceitação/requisitos
    — o mesmo estágio em que generate_epic_shape entrega o Epic pronto para
    a recepção do CLI, antes de qualquer User Story existir. Não inclui
    stories, prd_context, status ou review_notes.
    """
    return (
        f"# {epic.title or epic.id}\n\n"
        f"**ID**: {epic.id}\n\n"
        f"## Objetivo\n{epic.objective}\n\n"
        f"## Escopo\n{epic.scope}\n\n"
        f"## Valor\n{epic.value}\n\n"
        f"## Requisitos\n{_lista_requisitos(epic)}\n\n"
        f"## Critérios de Aceitação\n\n{_lista_criterios(epic)}\n"
    )
