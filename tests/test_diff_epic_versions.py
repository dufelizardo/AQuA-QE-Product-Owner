from aqua_qe_product_owner.models import AcceptanceCriteria, Epic
from aqua_qe_product_owner.skills.diff_epic_versions import diff_epic_versions


def _epic(objective="objetivo", scope="escopo", value="valor", acceptance_criteria=None) -> Epic:
    return Epic(
        id="EPIC-001",
        title="titulo",
        objective=objective,
        scope=scope,
        value=value,
        acceptance_criteria=acceptance_criteria or [],
    )


def test_identifies_new_and_discontinued_acceptance_criteria():
    antes = _epic(
        acceptance_criteria=[AcceptanceCriteria(id="AC-001", scenario="s", given="g1", when="w1", then="t1")]
    )
    depois = _epic(
        acceptance_criteria=[AcceptanceCriteria(id="AC-001", scenario="s", given="g2", when="w2", then="t2")]
    )

    resultado = diff_epic_versions(antes, depois)

    assert resultado["criterios_novos"] == [("g2", "w2", "t2")]
    assert resultado["criterios_descontinuados"] == [("g1", "w1", "t1")]


def test_identifies_objective_scope_and_value_changes():
    antes = _epic(objective="objetivo antigo", scope="escopo antigo", value="valor antigo")
    depois = _epic(objective="objetivo novo", scope="escopo novo", value="valor novo")

    resultado = diff_epic_versions(antes, depois)

    assert resultado["objetivo_antes"] == "objetivo antigo"
    assert resultado["objetivo_depois"] == "objetivo novo"
    assert resultado["escopo_antes"] == "escopo antigo"
    assert resultado["escopo_depois"] == "escopo novo"
    assert resultado["valor_antes"] == "valor antigo"
    assert resultado["valor_depois"] == "valor novo"


def test_no_changes_yields_empty_diff_and_same_text():
    criterio = AcceptanceCriteria(id="AC-001", scenario="s", given="g", when="w", then="t")
    antes = _epic(acceptance_criteria=[criterio])
    depois = _epic(acceptance_criteria=[criterio])

    resultado = diff_epic_versions(antes, depois)

    assert resultado["criterios_novos"] == []
    assert resultado["criterios_descontinuados"] == []
    assert resultado["objetivo_antes"] == resultado["objetivo_depois"]
    assert resultado["escopo_antes"] == resultado["escopo_depois"]
    assert resultado["valor_antes"] == resultado["valor_depois"]
