from ..models import AcceptanceCriteria, BusinessRule, UserStory
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você refina uma User Story existente com base nas respostas que o "
    "Product Owner deu às perguntas de esclarecimento levantadas por um "
    "revisor. Baseie-se apenas na descrição atual e nas respostas fornecidas; "
    "nunca invente ator, objetivo, regra ou critério que não tenha sido "
    "informado nelas. Responda sempre em português, mesmo que a descrição "
    "atual contenha trechos em outro idioma."
)


def refine_story(story: UserStory, respostas: list[dict]) -> UserStory:
    """Reescreve descrição, regras de negócio e critérios de aceitação de uma User Story usando as respostas do usuário às perguntas de esclarecimento."""
    regras_atuais = [regra.description for regra in story.business_rules]
    criterios_atuais = [
        {"cenario": c.scenario, "dado": c.given, "quando": c.when, "entao": c.then}
        for c in story.acceptance_criteria
    ]
    perguntas_respostas = [
        f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas
    ]

    prompt = (
        f"Ator: {story.actor}\nObjetivo: {story.goal}\nBenefício: {story.benefit}\n"
        f"Descrição atual: {story.description}\n"
        f"Regras de negócio atuais: {regras_atuais}\n"
        f"Critérios de aceitação atuais: {criterios_atuais}\n\n"
        "Respostas do Product Owner às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva a descrição, as regras de negócio e os critérios de "
        "aceitação incorporando essas respostas, resolvendo as lacunas "
        "apontadas.\n\n"
        "Cada critério de aceitação tem quatro campos distintos e não "
        "vazios: 'cenario' (um nome curto, de 2 a 5 palavras — nunca uma "
        "frase completa), 'dado' (o contexto/estado inicial), 'quando' (a "
        "ação ou evento) e 'entao' (o resultado esperado). Nunca junte duas "
        "dessas partes em um único campo.\n\n"
        "Exemplo do formato esperado de UM critério (não copie o conteúdo, "
        "só a estrutura):\n"
        '{"cenario": "Busca sem resultados", "dado": "não há médicos da '
        'especialidade escolhida", "quando": "o paciente pesquisa por essa '
        'especialidade", "entao": "o sistema exibe uma mensagem informando '
        'que não há médicos disponíveis"}\n\n'
        'Responda apenas em JSON: {"descricao": "...", "regras_negocio": ["..."], '
        '"criterios_aceitacao": [{"cenario": "...", "dado": "...", "quando": "...", "entao": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    novas_regras = [
        BusinessRule(id=f"BR-{i + 1:03d}", description=regra, source_reference=story.source_reference)
        for i, regra in enumerate(dados.get("regras_negocio", []))
    ]
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

    story.description = dados.get("descricao", story.description)
    story.business_rules = novas_regras or story.business_rules
    story.acceptance_criteria = novos_criterios or story.acceptance_criteria
    return story
