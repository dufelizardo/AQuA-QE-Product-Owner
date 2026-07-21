from ..models import Requirement
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um analista de requisitos. Extraia apenas requisitos literalmente "
    "presentes no texto informado pelo usuário. Nunca invente um requisito que "
    "não esteja no texto."
)


def extract_requirements(texto: str) -> list[Requirement]:
    """Extrai os requisitos candidatos presentes no texto de entrada."""
    prompt = (
        "Leia o texto abaixo e liste os requisitos candidatos nele contidos.\n"
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
