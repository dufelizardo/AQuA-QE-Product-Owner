from ..models import UserStory


def export_markdown(story: UserStory, caminho: str) -> None:
    """Exporta a User Story validada em formato Markdown para o caminho informado."""
    linhas = [
        f"# {story.title or story.id}",
        "",
        f"**ID**: {story.id}",
        f"**Status**: {story.status.value}",
        "",
        "## Descrição",
        "",
        f"Como {story.actor},",
        f"Quero {story.goal},",
        f"Para que {story.benefit}.",
        "",
    ]
    if story.description:
        linhas += [story.description, ""]

    if story.business_rules:
        linhas += ["## Regras de Negócio", ""]
        linhas += [f"- **{regra.id}**: {regra.description}" for regra in story.business_rules]
        linhas.append("")

    if story.acceptance_criteria:
        linhas += ["## Critérios de Aceitação", ""]
        for criterio in story.acceptance_criteria:
            linhas += [
                f"### {criterio.scenario}",
                "",
                f"- Given {criterio.given}",
                f"- When {criterio.when}",
                f"- Then {criterio.then}",
                "",
            ]

    if story.assumptions:
        linhas += ["## Suposições", ""]
        linhas += [f"- {suposicao}" for suposicao in story.assumptions]
        linhas.append("")

    if story.review_notes:
        linhas += ["## Observações da Revisão", ""]
        linhas += [f"- {nota}" for nota in story.review_notes]
        linhas.append("")

    linhas += ["## Rastreabilidade", "", f"> {story.source_reference}", ""]

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))
