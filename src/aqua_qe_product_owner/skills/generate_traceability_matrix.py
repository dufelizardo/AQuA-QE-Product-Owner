from ..models import Epic
from .validate_traceability import validate_traceability


def _requisito_para_stories(epic: Epic) -> dict[str, list]:
    stories_por_referencia: dict[str, list] = {}
    for story in epic.stories:
        stories_por_referencia.setdefault(story.source_reference, []).append(story)

    mapa: dict[str, list] = {}
    for requisito in epic.requirements:
        chave = requisito.source_reference or requisito.text
        mapa[requisito.id] = stories_por_referencia.get(chave, [])
    return mapa


def generate_traceability_matrix(epic: Epic) -> str:
    """Formata a Matriz de Rastreabilidade do Epic em Markdown: Requisito -> Story -> Critérios de Aceitação -> Status."""
    requisito_para_stories = _requisito_para_stories(epic)

    linhas = [
        f"# Matriz de Rastreabilidade — {epic.id}",
        "",
        "| Requisito | Story | Critérios de Aceitação | Status |",
        "|---|---|---|---|",
    ]
    for requisito in epic.requirements:
        stories = requisito_para_stories[requisito.id]
        if not stories:
            linhas.append(f"| {requisito.id}: {requisito.text} | (órfão) | — | — |")
            continue
        for story in stories:
            criterios = ", ".join(c.id for c in story.acceptance_criteria) or "—"
            linhas.append(
                f"| {requisito.id}: {requisito.text} | {story.id}: {story.title or story.goal} "
                f"| {criterios} | {story.status.value} |"
            )

    resultado = validate_traceability(epic)
    linhas += ["", "## Inconsistências"]
    if not any(resultado.values()):
        linhas.append("")
        linhas.append("Nenhuma inconsistência encontrada.")
    else:
        linhas.append("")
        if resultado["stories_duplicadas"]:
            linhas.append("**Stories com objetivo duplicado:**")
            linhas += [f"- {a} e {b}" for a, b in resultado["stories_duplicadas"]]
        if resultado["stories_sem_valor"]:
            linhas.append("**Stories sem benefício (valor de negócio) definido:**")
            linhas += [f"- {s}" for s in resultado["stories_sem_valor"]]
        if resultado["requisitos_orfaos"]:
            linhas.append("**Requisitos não cobertos por nenhuma story:**")
            linhas += [f"- {r}" for r in resultado["requisitos_orfaos"]]

    return "\n".join(linhas) + "\n"
