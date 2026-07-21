from ..models import Requirement
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você agrupa requisitos extraídos de um PRD em Épicos candidatos, por "
    "coerência temática. Se os requisitos formarem um único produto ou "
    "funcionalidade coesa, responda com um único grupo contendo todos eles — "
    "nunca divida artificialmente quando não houver frentes temáticas "
    "distintas e claras no texto."
)


def identify_epic_groups(texto: str, requisitos: list[Requirement]) -> list[list[Requirement]]:
    """Agrupa os requisitos extraídos em Épicos candidatos por coerência temática.

    Se os requisitos formarem um único produto coeso, retorna um grupo só —
    nunca força divisão que não exista no texto (GR-1). Se a resposta do LLM
    não cobrir todos os requisitos exatamente uma vez, cai no fallback seguro
    de um único grupo com todos eles.
    """
    if not requisitos:
        return []

    resumo = [{"id": r.id, "texto": r.text} for r in requisitos]
    prompt = (
        f"Texto de origem:\n{texto}\n\n"
        f"Requisitos extraídos: {resumo}\n\n"
        "Agrupe os IDs desses requisitos em Épicos candidatos, por coerência "
        "temática.\n"
        'Responda apenas em JSON: {"grupos": [{"requisitos_ids": ["REQ-001", "REQ-002"]}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    por_id = {r.id: r for r in requisitos}
    grupos_ids = [grupo.get("requisitos_ids", []) for grupo in dados.get("grupos", [])]

    ids_vistos: set[str] = set()
    grupos: list[list[Requirement]] = []
    for ids_grupo in grupos_ids:
        if not ids_grupo:
            continue
        grupo: list[Requirement] = []
        for req_id in ids_grupo:
            if req_id not in por_id or req_id in ids_vistos:
                return [requisitos]  # agrupamento inconsistente -- fallback seguro
            ids_vistos.add(req_id)
            grupo.append(por_id[req_id])
        grupos.append(grupo)

    if ids_vistos != set(por_id):
        return [requisitos]  # cobertura incompleta -- fallback seguro

    return grupos or [requisitos]
