from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica o ator (persona) principal de um requisito. Só responda "
    "com um ator que esteja literalmente identificável no texto. Nunca invente."
)


def identify_actor(texto: str) -> str:
    """Identifica o ator (persona) principal descrito no texto."""
    prompt = (
        "Qual é o ator (persona) principal descrito no texto abaixo?\n"
        'Responda apenas em JSON: {"ator": "..." } ou {"ator": null} '
        "se não for identificável com confiança.\n\n"
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("ator") or ""
