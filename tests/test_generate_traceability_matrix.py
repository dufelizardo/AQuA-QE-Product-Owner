from aqua_qe_product_owner.models import (
    AcceptanceCriteria,
    Epic,
    Requirement,
    StoryStatus,
    UserStory,
)
from aqua_qe_product_owner.skills.generate_traceability_matrix import generate_traceability_matrix


def _story(**overrides) -> UserStory:
    base = {
        "id": "US-001",
        "title": "titulo",
        "actor": "ator",
        "goal": "objetivo",
        "benefit": "beneficio",
        "description": "descricao",
        "source_reference": "fonte",
        "status": StoryStatus.ACCEPTED,
    }
    base.update(overrides)
    return UserStory(**base)


def test_matriz_lista_requisito_story_e_criterios():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[
            _story(
                id="US-001",
                title="Consultar saldo",
                source_reference="req-1",
                acceptance_criteria=[
                    AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
                ],
            )
        ],
        requirements=[Requirement(id="REQ-001", text="requisito 1", source_reference="req-1")],
    )

    resultado = generate_traceability_matrix(epic)

    assert "REQ-001: requisito 1" in resultado
    assert "US-001: Consultar saldo" in resultado
    assert "AC-001" in resultado
    assert "accepted" in resultado
    assert "Nenhuma inconsistência encontrada." in resultado


def test_matriz_marca_requisito_orfao():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[],
        requirements=[Requirement(id="REQ-001", text="requisito 1", source_reference="req-1")],
    )

    resultado = generate_traceability_matrix(epic)

    assert "REQ-001: requisito 1 | (órfão)" in resultado
    assert "Requisitos não cobertos por nenhuma story:" in resultado
    assert "- REQ-001" in resultado


def test_matriz_reporta_stories_duplicadas_e_sem_valor():
    epic = Epic(
        id="EPIC-001",
        title="t",
        objective="o",
        stories=[
            _story(id="US-001", goal="mesmo objetivo", benefit="", source_reference="req-1"),
            _story(id="US-002", goal="mesmo objetivo", source_reference="req-2"),
        ],
        requirements=[
            Requirement(id="REQ-001", text="r1", source_reference="req-1"),
            Requirement(id="REQ-002", text="r2", source_reference="req-2"),
        ],
    )

    resultado = generate_traceability_matrix(epic)

    assert "Stories com objetivo duplicado:" in resultado
    assert "US-001 e US-002" in resultado
    assert "Stories sem benefício (valor de negócio) definido:" in resultado
    assert "- US-001" in resultado
