from ..models import StoryStatus, UserStory
from ..skills.extract_requirements import extract_requirements
from ..skills.generate_story import generate_story
from ..skills.identify_actor import identify_actor
from ..skills.identify_business_rules import identify_business_rules
from ..skills.identify_goal import identify_goal
from ..skills.review_story import review_story
from ..skills.validate_story import validate_story


def finalize_story(story: UserStory) -> UserStory:
    """Aplica o checklist automático e a revisão por LLM, decidindo o status final da história."""
    if not validate_story(story):
        story.status = StoryStatus.PENDING_CLARIFICATION
        return story

    revisao = review_story(story)
    story.review_notes = revisao["problemas"]
    story.status = (
        StoryStatus.DRAFT_VALIDATED
        if revisao["aprovado"]
        else StoryStatus.PENDING_CLARIFICATION
    )
    return story


def generate_user_story(texto: str) -> UserStory:
    """Gera uma User Story unitária a partir do texto de entrada, orquestrando a sequência padrão de skills."""
    ator = identify_actor(texto)
    objetivo = identify_goal(texto)

    if not ator or not objetivo:
        faltando = [
            nome
            for nome, valor in (("ator", ator), ("objetivo", objetivo))
            if not valor
        ]
        return UserStory(
            id="US-000",
            title="",
            actor=ator,
            goal=objetivo,
            benefit="",
            description=(
                f"Não foi possível identificar {' e '.join(faltando)} com confiança "
                "suficiente no texto fornecido. Forneça mais detalhes antes de gerar "
                "a história (ver RULE-004 em docs/agent/rules.md)."
            ),
            source_reference=texto,
            status=StoryStatus.PENDING_CLARIFICATION,
        )

    requisitos = extract_requirements(texto)
    regras = identify_business_rules(texto)

    contexto = {
        "requirements": requisitos,
        "business_rules": regras,
        "texto_fonte": texto,
    }
    story = generate_story(ator, objetivo, contexto)
    return finalize_story(story)
