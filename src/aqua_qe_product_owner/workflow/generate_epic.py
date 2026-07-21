from ..models import AcceptanceCriteria, Epic, StoryStatus, UnresolvedItem, UserStory
from ..skills.extract_requirements import extract_requirements
from ..skills.generate_epic_metadata import generate_epic_metadata
from ..skills.generate_story import generate_story
from ..skills.identify_actor import identify_actor
from ..skills.identify_business_rules import identify_business_rules
from ..skills.identify_goal import identify_goal
from ..skills.review_epic import review_epic
from ..skills.validate_epic import validate_epic
from .generate_user_story import finalize_story


def finalize_epic(epic: Epic) -> Epic:
    """Aplica o checklist automático e a revisão por LLM ao Epic, decidindo seu status final."""
    if not validate_epic(epic):
        epic.status = StoryStatus.PENDING_CLARIFICATION
        return epic

    revisao = review_epic(epic)
    epic.review_notes = revisao["problemas"]
    epic.status = (
        StoryStatus.DRAFT_VALIDATED if revisao["aprovado"] else StoryStatus.PENDING_CLARIFICATION
    )
    return epic


def generate_epic(texto: str) -> Epic:
    """Processa uma fonte completa em modo lote, gerando um Epic com as User Stories e itens não resolvidos."""
    requisitos = extract_requirements(texto)

    stories: list[UserStory] = []
    unresolved: list[UnresolvedItem] = []

    for i, requisito in enumerate(requisitos, start=1):
        texto_item = requisito.text
        ator = identify_actor(texto_item)
        objetivo = identify_goal(texto_item)

        if not ator or not objetivo:
            faltando = [nome for nome, valor in (("ator", ator), ("objetivo", objetivo)) if not valor]
            unresolved.append(
                UnresolvedItem(
                    source_reference=requisito.source_reference or texto_item,
                    reason=(
                        f"Não foi possível identificar {' e '.join(faltando)} com "
                        "confiança suficiente (ver RULE-004 em docs/agent/rules.md)."
                    ),
                )
            )
            continue

        regras = identify_business_rules(texto_item)
        contexto = {
            "id": f"US-{i:03d}",
            "business_rules": regras,
            "texto_fonte": requisito.source_reference or texto_item,
        }
        story = generate_story(ator, objetivo, contexto)
        stories.append(finalize_story(story))

    metadados = generate_epic_metadata(texto, stories)
    criterios = [
        AcceptanceCriteria(
            id=f"AC-{i + 1:03d}",
            scenario=criterio.get("cenario", ""),
            given=criterio.get("dado", ""),
            when=criterio.get("quando", ""),
            then=criterio.get("entao", ""),
        )
        for i, criterio in enumerate(metadados.get("criterios_aceitacao", []))
    ]

    epic = Epic(
        id="EPIC-001",
        title=metadados.get("titulo", ""),
        objective=metadados.get("objetivo", ""),
        scope=metadados.get("escopo", ""),
        value=metadados.get("valor", ""),
        acceptance_criteria=criterios,
        stories=stories,
        unresolved_items=unresolved,
        requirements=requisitos,
    )
    return finalize_epic(epic)
