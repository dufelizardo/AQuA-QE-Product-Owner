from ..models import Requirement
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um analista de requisitos. Extraia apenas requisitos funcionais "
    "literalmente presentes no texto informado pelo usuário. Nunca invente um "
    "requisito que não esteja no texto."
)


def extract_requirements(texto: str) -> list[Requirement]:
    """Extrai os requisitos funcionais candidatos presentes no texto de entrada."""
    prompt = (
        "Leia o texto abaixo e liste apenas os requisitos FUNCIONAIS candidatos "
        "nele contidos — ações ou capacidades concretas que o sistema deve "
        "executar (o que o usuário consegue fazer).\n\n"
        "Não liste como requisito: requisitos não funcionais (desempenho, "
        "disponibilidade, segurança, escalabilidade, usabilidade, "
        "manutenibilidade, conformidade regulatória), critérios de sucesso ou "
        "métricas, riscos/premissas, nem itens explicitamente marcados como "
        "'fora de escopo'. Se o texto tiver seções com esses rótulos (ex.: "
        "'Requisitos não funcionais', 'Critérios de sucesso', 'Riscos e "
        "premissas', 'Fora de escopo'), ignore o conteúdo dessas seções por "
        "completo.\n\n"
        'Responda apenas em JSON, no formato: {"requisitos": '
        '[{"texto": "...", "trecho_fonte": "..."}]}\n\n'
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        Requirement(
            id=f"REQ-{i + 1:03d}",
            text=item.get("texto", ""),
            source_reference=item.get("trecho_fonte", ""),
        )
        for i, item in enumerate(dados.get("requisitos", []))
    ]
