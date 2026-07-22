from ..models import PRDDraft
from ..services.llm_service import complete_json


def _como_texto(valor: object) -> str:
    """Normaliza um campo que deveria ser texto (escopo/fora_de_escopo), mas o LLM às vezes retorna como lista."""
    if isinstance(valor, list):
        return "; ".join(str(item) for item in valor)
    return str(valor) if valor else ""


_SYSTEM = (
    "Você escreve um PRD (Product Requirements Document) completo a partir de "
    "uma ideia informal, seguindo a estrutura padrão de mercado. Baseie-se "
    "apenas na ideia informada; nunca invente números, nomes de concorrentes, "
    "tecnologias ou funcionalidades que não decorram diretamente dela. Quando "
    "uma seção não puder ser sustentada pela ideia, deixe-a vazia — não "
    "preencha com suposição. Responda sempre em português, mesmo que a ideia "
    "esteja em outro idioma."
)


def generate_prd(ideia: str) -> PRDDraft:
    """Gera um PRD estruturado a partir de uma ideia crua, conforme docs/standards/prd_standard.md."""
    prompt = (
        f"Ideia:\n{ideia}\n\n"
        "Escreva um PRD com as seguintes seções:\n"
        "- contexto_problema: contexto e problema de negócio que motiva o PRD\n"
        "- objetivo: objetivo do produto, em uma frase\n"
        "- publico_alvo: público-alvo / personas\n"
        "- escopo: o que o produto faz\n"
        "- fora_de_escopo: o que o produto explicitamente não faz\n"
        "- requisitos_funcionais: lista de requisitos funcionais\n"
        "- requisitos_nao_funcionais: lista de requisitos não funcionais "
        "(desempenho, segurança, disponibilidade etc.)\n"
        "- criterios_sucesso: lista de critérios de sucesso\n"
        "- riscos_premissas: lista de riscos e premissas\n\n"
        'Responda apenas em JSON: {"contexto_problema": "...", "objetivo": "...", '
        '"publico_alvo": "...", "escopo": "...", "fora_de_escopo": "...", '
        '"requisitos_funcionais": ["..."], "requisitos_nao_funcionais": ["..."], '
        '"criterios_sucesso": ["..."], "riscos_premissas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return PRDDraft(
        context_problem=dados.get("contexto_problema") or "",
        objective=dados.get("objetivo") or "",
        target_audience=dados.get("publico_alvo") or "",
        scope=_como_texto(dados.get("escopo")),
        out_of_scope=_como_texto(dados.get("fora_de_escopo")),
        functional_requirements=dados.get("requisitos_funcionais") or [],
        non_functional_requirements=dados.get("requisitos_nao_funcionais") or [],
        success_criteria=dados.get("criterios_sucesso") or [],
        risks_assumptions=dados.get("riscos_premissas") or [],
    )
