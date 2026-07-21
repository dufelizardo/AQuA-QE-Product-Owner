from ..models import PRDContext
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você extrai o contexto estrutural de um PRD (Product Requirements Document), "
    "além dos requisitos funcionais. Responda apenas com informação literalmente "
    "sustentada pelo texto; quando uma seção não estiver presente ou não for "
    "identificável, deixe o campo vazio (string vazia ou lista vazia) — nunca invente."
)


def extract_prd_context(texto: str) -> PRDContext:
    """Extrai visão, problema, objetivos, público-alvo, requisitos não funcionais, restrições, critérios de sucesso, riscos e dependências de um PRD, conforme docs/standards/prd_standard.md."""
    prompt = (
        "Leia o PRD abaixo e extraia as seguintes informações, quando presentes:\n"
        "- visao: visão do produto (uma ou duas frases)\n"
        "- problema: problema de negócio que motiva o PRD\n"
        "- objetivos: lista de objetivos de negócio\n"
        "- publico_alvo: público-alvo / personas\n"
        "- requisitos_nao_funcionais: lista de requisitos não funcionais "
        "(desempenho, segurança, disponibilidade etc.)\n"
        "- restricoes: lista de restrições\n"
        "- criterios_sucesso: lista de critérios de sucesso\n"
        "- riscos: lista de riscos\n"
        "- dependencias: lista de dependências\n\n"
        'Responda apenas em JSON: {"visao": "...", "problema": "...", '
        '"objetivos": ["..."], "publico_alvo": "...", '
        '"requisitos_nao_funcionais": ["..."], "restricoes": ["..."], '
        '"criterios_sucesso": ["..."], "riscos": ["..."], "dependencias": ["..."]}\n\n'
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return PRDContext(
        vision=dados.get("visao") or "",
        problem=dados.get("problema") or "",
        objectives=dados.get("objetivos") or [],
        target_audience=dados.get("publico_alvo") or "",
        non_functional_requirements=dados.get("requisitos_nao_funcionais") or [],
        constraints=dados.get("restricoes") or [],
        success_criteria=dados.get("criterios_sucesso") or [],
        risks=dados.get("riscos") or [],
        dependencies=dados.get("dependencias") or [],
    )
