from ..models import BusinessRule
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica regras de negócio implícitas ou explícitas em um texto. "
    "Só responda com regras literalmente sustentadas pelo texto. Nunca invente."
)


def identify_business_rules(texto: str) -> list[BusinessRule]:
    """Identifica as regras de negócio implícitas ou explícitas no texto."""
    prompt = (
        "Identifique as regras de negócio presentes no texto abaixo.\n"
        'Responda apenas em JSON: {"regras": '
        '[{"descricao": "...", "trecho_fonte": "..."}]}\n\n'
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        BusinessRule(
            id=f"BR-{i + 1:03d}",
            description=item.get("descricao", ""),
            source_reference=item.get("trecho_fonte", ""),
        )
        for i, item in enumerate(dados.get("regras", []))
    ]
