from ..models import AcceptanceCriteria, BusinessRule, StoryStatus, UserStory
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você gera User Stories no formato Como/Quero/Para que, com critérios de "
    "aceitação em Given-When-Then. Baseie-se apenas nas informações fornecidas; "
    "nunca invente ator, objetivo ou regra que não tenha sido informado. "
    "Responda sempre em português, mesmo que o texto de origem contenha "
    "trechos em outro idioma."
)


def generate_story(ator: str, objetivo: str, contexto: dict) -> UserStory:
    """Gera uma User Story a partir do ator, objetivo e contexto informados."""
    regras: list[BusinessRule] = contexto.get("business_rules", [])
    fonte = contexto.get("texto_fonte", "")

    prompt = (
        f"Ator: {ator}\n"
        f"Objetivo: {objetivo}\n"
        f"Regras de negócio conhecidas: {[regra.description for regra in regras]}\n"
        f"Texto de origem:\n{fonte}\n\n"
        "Gere uma User Story em português a partir dessas informações.\n\n"
        "Escreva de 1 a 3 critérios de aceitação no formato Given-When-Then. "
        "Cada critério tem quatro campos distintos e não vazios: 'cenario' "
        "(um nome curto, de 2 a 5 palavras, para o cenário — nunca uma frase "
        "completa), 'dado' (o contexto/estado inicial), 'quando' (a ação ou "
        "evento) e 'entao' (o resultado esperado). Nunca junte duas dessas "
        "partes em um único campo.\n\n"
        "Exemplo do formato esperado de UM critério (não copie o conteúdo, "
        "só a estrutura):\n"
        '{"cenario": "Busca sem resultados", "dado": "não há médicos da '
        'especialidade escolhida", "quando": "o paciente pesquisa por essa '
        'especialidade", "entao": "o sistema exibe uma mensagem informando '
        'que não há médicos disponíveis"}\n\n'
        'Responda apenas em JSON, no formato: {"titulo": "...", "beneficio": "...", '
        '"descricao": "...", "criterios_aceitacao": [{"cenario": "...", "dado": "...", '
        '"quando": "...", "entao": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    criterios = [
        AcceptanceCriteria(
            id=f"AC-{i + 1:03d}",
            scenario=criterio.get("cenario", ""),
            given=criterio.get("dado", ""),
            when=criterio.get("quando", ""),
            then=criterio.get("entao", ""),
        )
        for i, criterio in enumerate(dados.get("criterios_aceitacao", []))
    ]

    return UserStory(
        id=contexto.get("id", "US-001"),
        title=dados.get("titulo", ""),
        actor=ator,
        goal=objetivo,
        benefit=dados.get("beneficio", ""),
        description=dados.get("descricao", ""),
        acceptance_criteria=criterios,
        business_rules=regras,
        source_reference=fonte,
        status=StoryStatus.PENDING_CLARIFICATION,
    )
