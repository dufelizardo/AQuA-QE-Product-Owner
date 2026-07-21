from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica o objetivo (goal) principal de um requisito. Só responda "
    "com um objetivo que esteja literalmente identificável no texto. Nunca invente."
)


def identify_goal(texto: str) -> str:
    """Identifica o objetivo (goal) descrito no texto."""
    prompt = (
        "Qual é o objetivo (goal) principal descrito no texto abaixo?\n"
        'Responda apenas em JSON: {"objetivo": "..." } ou {"objetivo": null} '
        "se não for identificável com confiança.\n\n"
        f"Texto:\n{texto}"
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("objetivo") or ""
