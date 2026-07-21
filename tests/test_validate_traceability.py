from aqua_qe_product_owner.models import Epic, Requirement, UnresolvedItem, UserStory
from aqua_qe_product_owner.skills.validate_traceability import validate_traceability


def _story(**overrides) -> UserStory:
    base = {
        "id": "US-001",
        "title": "titulo",
        "actor": "ator",
        "goal": "objetivo",
        "benefit": "beneficio",
        "description": "descricao",
        "source_reference": "fonte",
    }
    base.update(overrides)
    return UserStory(**base)


def test_no_issues_returns_all_empty():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[_story(id="US-001", goal="objetivo 1", source_reference="req-1")],
        requirements=[Requirement(id="REQ-001", text="requisito 1", source_reference="req-1")],
    )

    resultado = validate_traceability(epic)

    assert resultado == {
        "stories_duplicadas": [],
        "stories_sem_valor": [],
        "requisitos_orfaos": [],
    }


def test_detects_duplicated_goals():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[
            _story(id="US-001", goal="Mesmo objetivo"),
            _story(id="US-002", goal="mesmo objetivo"),
        ],
    )

    resultado = validate_traceability(epic)

    assert resultado["stories_duplicadas"] == [("US-001", "US-002")]


def test_detects_stories_without_benefit():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[_story(id="US-001", benefit=""), _story(id="US-002", benefit="  ")],
    )

    resultado = validate_traceability(epic)

    assert resultado["stories_sem_valor"] == ["US-001", "US-002"]


def test_detects_orphan_requirements():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[_story(id="US-001", source_reference="req-1")],
        unresolved_items=[UnresolvedItem(source_reference="req-2", reason="motivo")],
        requirements=[
            Requirement(id="REQ-001", text="r1", source_reference="req-1"),
            Requirement(id="REQ-002", text="r2", source_reference="req-2"),
            Requirement(id="REQ-003", text="r3", source_reference="req-3"),
        ],
    )

    resultado = validate_traceability(epic)

    assert resultado["requisitos_orfaos"] == ["REQ-003"]
