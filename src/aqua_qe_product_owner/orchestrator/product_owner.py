from ..models import Epic, UserStory
from ..workflow.generate_epic import generate_epic
from ..workflow.generate_user_story import generate_user_story


def handle_request(entrada: str, modo: str) -> UserStory | Epic:
    """Decide e executa o workflow apropriado (unitário ou lote) para a entrada recebida, conforme docs/agent/agent_design.md."""
    if modo == "unitario":
        return generate_user_story(entrada)
    if modo == "lote":
        return generate_epic(entrada)
    raise NotImplementedError(
        f"Modo '{modo}' não suportado (esperado 'unitario' ou 'lote')."
    )
