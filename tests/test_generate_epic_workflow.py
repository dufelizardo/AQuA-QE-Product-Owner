from aqua_qe_product_owner.models import Requirement, StoryStatus, UserStory
from aqua_qe_product_owner.workflow import generate_epic as workflow_module

_METADADOS_PADRAO = {
    "titulo": "titulo do epico",
    "objetivo": "objetivo do epico",
    "escopo": "escopo do epico",
    "valor": "valor do epico",
    "criterios_aceitacao": [
        {"cenario": "c", "dado": "g", "quando": "w", "entao": "t"}
    ],
}


def _fake_requirement(i: int) -> Requirement:
    return Requirement(id=f"REQ-{i:03d}", text=f"requisito {i}", source_reference=f"trecho {i}")


def _mockar_finalize_epic_aprovado(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_epic", lambda epic: True)
    monkeypatch.setattr(
        workflow_module, "review_epic", lambda epic: {"aprovado": True, "problemas": []}
    )


def test_items_ambiguos_vao_para_unresolved_items(monkeypatch):
    monkeypatch.setattr(
        workflow_module, "extract_requirements", lambda texto: [_fake_requirement(1)]
    )
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "")
    monkeypatch.setattr(
        workflow_module, "generate_epic_metadata", lambda texto, requisitos: _METADADOS_PADRAO
    )
    _mockar_finalize_epic_aprovado(monkeypatch)

    epic = workflow_module.generate_epic("fonte qualquer")

    assert epic.stories == []
    assert len(epic.unresolved_items) == 1
    assert epic.unresolved_items[0].source_reference == "trecho 1"


def test_items_identificaveis_viram_stories(monkeypatch):
    monkeypatch.setattr(
        workflow_module,
        "extract_requirements",
        lambda texto: [_fake_requirement(1), _fake_requirement(2)],
    )
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "cliente")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "fazer algo")
    monkeypatch.setattr(workflow_module, "identify_business_rules", lambda texto: [])
    monkeypatch.setattr(
        workflow_module, "generate_epic_metadata", lambda texto, requisitos: _METADADOS_PADRAO
    )
    _mockar_finalize_epic_aprovado(monkeypatch)

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id=contexto["id"],
            title="titulo",
            actor=ator,
            goal=objetivo,
            benefit="beneficio",
            description="descricao",
            source_reference=contexto["texto_fonte"],
        )

    def fake_finalize_story(story):
        story.status = StoryStatus.DRAFT_VALIDATED
        return story

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(workflow_module, "finalize_story", fake_finalize_story)

    epic = workflow_module.generate_epic("fonte qualquer")

    assert len(epic.stories) == 2
    assert epic.unresolved_items == []
    assert {s.id for s in epic.stories} == {"US-001", "US-002"}
    assert all(s.status == StoryStatus.DRAFT_VALIDATED for s in epic.stories)
    assert epic.title == "titulo do epico"
    assert epic.objective == "objetivo do epico"
    assert epic.scope == "escopo do epico"
    assert epic.value == "valor do epico"
    assert epic.acceptance_criteria[0].given == "g"
    assert epic.status == StoryStatus.DRAFT_VALIDATED
    assert {r.id for r in epic.requirements} == {"REQ-001", "REQ-002"}


def test_itens_mistos_nao_bloqueiam_o_lote(monkeypatch):
    monkeypatch.setattr(
        workflow_module,
        "extract_requirements",
        lambda texto: [_fake_requirement(1), _fake_requirement(2)],
    )

    def fake_identify_actor(texto):
        return "" if texto == "requisito 1" else "cliente"

    def fake_identify_goal(texto):
        return "" if texto == "requisito 1" else "fazer algo"

    monkeypatch.setattr(workflow_module, "identify_actor", fake_identify_actor)
    monkeypatch.setattr(workflow_module, "identify_goal", fake_identify_goal)
    monkeypatch.setattr(workflow_module, "identify_business_rules", lambda texto: [])
    monkeypatch.setattr(
        workflow_module, "generate_epic_metadata", lambda texto, requisitos: _METADADOS_PADRAO
    )
    _mockar_finalize_epic_aprovado(monkeypatch)

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id=contexto["id"],
            title="titulo",
            actor=ator,
            goal=objetivo,
            benefit="beneficio",
            description="descricao",
            source_reference=contexto["texto_fonte"],
        )

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(workflow_module, "finalize_story", lambda story: story)

    epic = workflow_module.generate_epic("fonte qualquer")

    assert len(epic.unresolved_items) == 1
    assert len(epic.stories) == 1
    assert epic.stories[0].id == "US-002"


def test_finalize_epic_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_epic", lambda epic: False)

    from aqua_qe_product_owner.models import Epic

    epic = Epic(id="EPIC-001", title="t", objective="o")
    resultado = workflow_module.finalize_epic(epic)

    assert resultado.status == StoryStatus.PENDING_CLARIFICATION


def test_finalize_epic_marca_pending_clarification_quando_review_reprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_epic", lambda epic: True)
    monkeypatch.setattr(
        workflow_module,
        "review_epic",
        lambda epic: {"aprovado": False, "problemas": ["escopo confuso"]},
    )

    from aqua_qe_product_owner.models import Epic

    epic = Epic(id="EPIC-001", title="t", objective="o")
    resultado = workflow_module.finalize_epic(epic)

    assert resultado.status == StoryStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["escopo confuso"]


def test_generate_epic_shape_define_epico_sem_gerar_nenhuma_story(monkeypatch):
    monkeypatch.setattr(
        workflow_module,
        "extract_requirements",
        lambda texto: [_fake_requirement(1), _fake_requirement(2)],
    )
    monkeypatch.setattr(
        workflow_module, "generate_epic_metadata", lambda texto, requisitos: _METADADOS_PADRAO
    )
    monkeypatch.setattr(workflow_module, "validate_epic", lambda epic: True)

    epic = workflow_module.generate_epic_shape("fonte qualquer")

    assert epic.stories == []
    assert epic.unresolved_items == []
    assert epic.title == "titulo do epico"
    assert epic.objective == "objetivo do epico"
    assert epic.scope == "escopo do epico"
    assert epic.value == "valor do epico"
    assert epic.acceptance_criteria[0].given == "g"
    assert {r.id for r in epic.requirements} == {"REQ-001", "REQ-002"}
    assert epic.status == StoryStatus.DRAFT_VALIDATED


def test_generate_epic_shape_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "extract_requirements", lambda texto: [_fake_requirement(1)])
    monkeypatch.setattr(
        workflow_module, "generate_epic_metadata", lambda texto, requisitos: _METADADOS_PADRAO
    )
    monkeypatch.setattr(workflow_module, "validate_epic", lambda epic: False)

    epic = workflow_module.generate_epic_shape("fonte qualquer")

    assert epic.status == StoryStatus.PENDING_CLARIFICATION


def test_generate_epic_stories_divide_o_epico_ja_definido_em_stories(monkeypatch):
    from aqua_qe_product_owner.models import Epic

    epic_inicial = Epic(
        id="EPIC-001",
        title="titulo do epico",
        objective="objetivo do epico",
        requirements=[_fake_requirement(1), _fake_requirement(2)],
    )

    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "cliente")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "fazer algo")
    monkeypatch.setattr(workflow_module, "identify_business_rules", lambda texto: [])
    _mockar_finalize_epic_aprovado(monkeypatch)

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id=contexto["id"],
            title="titulo",
            actor=ator,
            goal=objetivo,
            benefit="beneficio",
            description="descricao",
            source_reference=contexto["texto_fonte"],
        )

    def fake_finalize_story(story):
        story.status = StoryStatus.DRAFT_VALIDATED
        return story

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(workflow_module, "finalize_story", fake_finalize_story)

    epic = workflow_module.generate_epic_stories(epic_inicial)

    assert len(epic.stories) == 2
    assert {s.id for s in epic.stories} == {"US-001", "US-002"}
    assert all(s.status == StoryStatus.DRAFT_VALIDATED for s in epic.stories)
    assert epic.status == StoryStatus.DRAFT_VALIDATED
    # o epico ja vinha com titulo/objetivo definidos por generate_epic_shape; nao mudam aqui
    assert epic.title == "titulo do epico"
