from ..models import AcceptanceCriteria, Epic
from ..services.llm_service import complete_json


def _como_texto(valor: object) -> str:
    """Normaliza um campo que deveria ser texto (título/objetivo/escopo/valor), mas o LLM às vezes retorna como lista."""
    if isinstance(valor, list):
        return "; ".join(str(item) for item in valor)
    return str(valor) if valor else ""


_SYSTEM = (
    "Você refina um Épico existente com base nas respostas que quem propôs a "
    "ideia deu às perguntas de esclarecimento levantadas por um revisor. "
    "Baseie-se apenas no Épico atual e nas respostas fornecidas; nunca invente "
    "escopo, valor ou critério de aceitação que não tenha sido informado "
    "nelas. Responda sempre em português, mesmo que o Épico atual contenha "
    "trechos em outro idioma."
)


def refine_epic_metadata(epic: Epic, respostas: list[dict]) -> Epic:
    """Reescreve título, objetivo, escopo, valor e critérios de aceitação do Épico usando as respostas às perguntas de esclarecimento."""
    criterios_atuais = [
        {"cenario": c.scenario, "dado": c.given, "quando": c.when, "entao": c.then}
        for c in epic.acceptance_criteria
    ]
    perguntas_respostas = [
        f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas
    ]

    prompt = (
        f"Título atual: {epic.title}\nObjetivo atual: {epic.objective}\n"
        f"Escopo atual: {epic.scope}\nValor atual: {epic.value}\n"
        f"Critérios de aceitação atuais: {criterios_atuais}\n\n"
        "Respostas às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva o título, objetivo, escopo, valor e critérios de "
        "aceitação incorporando essas respostas, resolvendo as lacunas "
        "apontadas.\n\n"
        "Cada critério de aceitação tem quatro campos distintos e não "
        "vazios: 'cenario', 'dado', 'quando' e 'entao'. Nunca junte duas "
        "dessas partes em um único campo.\n\n"
        'Responda apenas em JSON: {"titulo": "...", "objetivo": "...", '
        '"escopo": "...", "valor": "...", "criterios_aceitacao": '
        '[{"cenario": "...", "dado": "...", "quando": "...", "entao": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    epic.title = _como_texto(dados.get("titulo")) or epic.title
    epic.objective = _como_texto(dados.get("objetivo")) or epic.objective
    epic.scope = _como_texto(dados.get("escopo")) or epic.scope
    epic.value = _como_texto(dados.get("valor")) or epic.value

    novos_criterios = [
        AcceptanceCriteria(
            id=f"AC-{i + 1:03d}",
            scenario=criterio.get("cenario", ""),
            given=criterio.get("dado", ""),
            when=criterio.get("quando", ""),
            then=criterio.get("entao", ""),
        )
        for i, criterio in enumerate(dados.get("criterios_aceitacao", []))
    ]
    epic.acceptance_criteria = novos_criterios or epic.acceptance_criteria
    return epic
