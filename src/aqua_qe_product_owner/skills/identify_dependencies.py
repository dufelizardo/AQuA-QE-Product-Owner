from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica dependências — outras histórias, sistemas ou decisões — "
    "mencionadas implícita ou explicitamente em um texto. Só responda com "
    "dependências literalmente sustentadas pelo texto. Nunca invente."
)


def identify_dependencies(texto: str) -> list[str]:
    """Identifica dependências (outras histórias, sistemas ou decisões) mencionadas no texto."""
    prompt = (
        "Identifique as dependências presentes no texto abaixo — outras "
        "histórias, sistemas, integrações ou decisões das quais o que está "
        "descrito depende.\n"
        'Responda apenas em JSON: {"dependencias": ["..."]}\n\n'
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("dependencias", [])
