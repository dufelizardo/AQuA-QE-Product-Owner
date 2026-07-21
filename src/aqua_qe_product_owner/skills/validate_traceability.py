from ..models import Epic


def validate_traceability(epic: Epic) -> dict:
    """Verifica consistência entre os artefatos de um Epic: stories duplicadas, sem valor de negócio associado, e requisitos não cobertos por nenhuma story ou item não resolvido."""
    metas_vistas: dict[str, str] = {}
    duplicadas: list[tuple[str, str]] = []
    for story in epic.stories:
        chave = story.goal.strip().lower()
        if not chave:
            continue
        if chave in metas_vistas:
            duplicadas.append((metas_vistas[chave], story.id))
        else:
            metas_vistas[chave] = story.id

    sem_valor = [story.id for story in epic.stories if not story.benefit.strip()]

    referencias_cobertas = {story.source_reference for story in epic.stories}
    referencias_cobertas |= {item.source_reference for item in epic.unresolved_items}
    orfaos = [
        requisito.id
        for requisito in epic.requirements
        if (requisito.source_reference or requisito.text) not in referencias_cobertas
    ]

    return {
        "stories_duplicadas": duplicadas,
        "stories_sem_valor": sem_valor,
        "requisitos_orfaos": orfaos,
    }
