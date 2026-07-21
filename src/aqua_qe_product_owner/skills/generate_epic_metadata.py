from ..models import UserStory
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você define o título, objetivo, escopo, valor de negócio e critérios de "
    "aceitação de alto nível de um Épico, a partir do texto de origem e das "
    "User Stories já geradas dentro dele. Baseie-se apenas nas informações "
    "fornecidas; nunca invente escopo ou valor que não seja sustentado pelo "
    "texto ou pelas stories. Responda sempre em português, mesmo que o texto "
    "de origem contenha trechos em outro idioma."
)


def generate_epic_metadata(texto: str, stories: list[UserStory]) -> dict:
    """Gera título, objetivo, escopo, valor e critérios de aceitação de um Épico a partir da fonte e das User Stories geradas."""
    resumo_stories = [{"titulo": s.title, "objetivo": s.goal} for s in stories]
    prompt = (
        f"Texto de origem:\n{texto}\n\n"
        f"User Stories já geradas neste Épico: {resumo_stories}\n\n"
        "Defina o título, objetivo, escopo e valor de negócio deste Épico, em "
        "português.\n\n"
        "Depois, escreva de 2 a 4 critérios de aceitação de alto nível no "
        "formato Given-When-Then. Cada critério tem exatamente três campos "
        "distintos e não vazios: 'dado' (o contexto/estado inicial, uma frase "
        "curta), 'quando' (a ação ou evento, uma frase curta) e 'entao' (o "
        "resultado esperado, uma frase curta). Nunca deixe 'quando' ou "
        "'entao' vazios, e nunca junte as três partes em um único campo.\n\n"
        "Exemplo do formato esperado de UM critério (não copie o conteúdo, "
        "só a estrutura):\n"
        '{"cenario": "Busca por especialidade", "dado": "o paciente está na '
        'tela de busca", "quando": "o paciente pesquisa por uma especialidade", '
        '"entao": "o sistema exibe a lista de médicos daquela especialidade"}\n\n'
        'Responda apenas em JSON: {"titulo": "...", "objetivo": "...", '
        '"escopo": "...", "valor": "...", "criterios_aceitacao": '
        '[{"cenario": "...", "dado": "...", "quando": "...", "entao": "..."}]}'
    )
    return complete_json(prompt, system=_SYSTEM)
