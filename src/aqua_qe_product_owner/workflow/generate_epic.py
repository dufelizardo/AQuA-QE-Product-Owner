from ..models import AcceptanceCriteria, Epic, StoryStatus, UnresolvedItem, UserStory
from ..skills.extract_prd_context import extract_prd_context
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


def generate_epic_shape(texto: str) -> Epic:
    """Extrai os requisitos e o contexto do PRD, e define o Epic (titulo/objetivo/escopo/valor/criterios) a partir da fonte, antes de gerar qualquer User Story.

    epic.prd_context preserva a parte do PRD que não é requisito funcional
    (visão, requisitos não funcionais, restrições, critérios de sucesso, riscos,
    dependências) — hoje descartada após a extração, mas necessária para
    rastreabilidade completa do PRD (ver docs/standards/prd_standard.md).

    O status reflete apenas o checklist automático (validate_epic) — review_epic
    avalia coerência com as stories agrupadas, que ainda não existem neste ponto.
    """
    requisitos = extract_requirements(texto)
    prd_context = extract_prd_context(texto)
    metadados = generate_epic_metadata(texto, requisitos)
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
        requirements=requisitos,
        prd_context=prd_context,
    )
    epic.status = (
        StoryStatus.DRAFT_VALIDATED if validate_epic(epic) else StoryStatus.PENDING_CLARIFICATION
    )
    return epic


def generate_epic_stories(epic: Epic) -> Epic:
    """Divide o Epic em User Stories (uma por requisito já extraído em epic.requirements) e finaliza o Epic.

    Ao final, aplica finalize_epic — agora com as stories geradas, review_epic
    consegue avaliar coerência real entre o objetivo do Epic e o que as
    stories entregam.
    """
    stories: list[UserStory] = []
    unresolved: list[UnresolvedItem] = []

    for i, requisito in enumerate(epic.requirements, start=1):
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

    epic.stories = stories
    epic.unresolved_items = unresolved
    return finalize_epic(epic)


def generate_epic(texto: str) -> Epic:
    """Processa uma fonte completa em modo lote, gerando um Epic com as User Stories e itens não resolvidos.

    Conveniência de uma chamada só (sem checkpoint humano intermediário) — para
    o checkpoint humano entre a definição do Epic e a geração das stories, use
    generate_epic_shape / generate_epic_stories separadamente (ver run.py).
    """
    return generate_epic_stories(generate_epic_shape(texto))
