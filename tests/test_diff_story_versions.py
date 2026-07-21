from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, UserStory
from aqua_qe_product_owner.skills.diff_story_versions import diff_story_versions


def _story(business_rules=None, acceptance_criteria=None) -> UserStory:
    return UserStory(
        id="US-001",
        title="titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        business_rules=business_rules or [],
        acceptance_criteria=acceptance_criteria or [],
        source_reference="fonte",
    )


def test_identifies_new_and_discontinued_business_rules():
    antes = _story(business_rules=[BusinessRule(id="BR-001", description="regra A", source_reference="f")])
    depois = _story(business_rules=[BusinessRule(id="BR-001", description="regra B", source_reference="f")])

    resultado = diff_story_versions(antes, depois)

    assert resultado["regras_novas"] == ["regra B"]
    assert resultado["regras_descontinuadas"] == ["regra A"]


def test_identifies_new_and_discontinued_acceptance_criteria():
    antes = _story(
        acceptance_criteria=[AcceptanceCriteria(id="AC-001", scenario="s", given="g1", when="w1", then="t1")]
    )
    depois = _story(
        acceptance_criteria=[AcceptanceCriteria(id="AC-001", scenario="s", given="g2", when="w2", then="t2")]
    )

    resultado = diff_story_versions(antes, depois)

    assert resultado["criterios_novos"] == [("g2", "w2", "t2")]
    assert resultado["criterios_descontinuados"] == [("g1", "w1", "t1")]


def test_no_changes_yields_empty_diff():
    regra = BusinessRule(id="BR-001", description="regra A", source_reference="f")
    criterio = AcceptanceCriteria(id="AC-001", scenario="s", given="g", when="w", then="t")
    antes = _story(business_rules=[regra], acceptance_criteria=[criterio])
    depois = _story(business_rules=[regra], acceptance_criteria=[criterio])

    resultado = diff_story_versions(antes, depois)

    assert resultado == {
        "regras_novas": [],
        "regras_descontinuadas": [],
        "criterios_novos": [],
        "criterios_descontinuados": [],
    }
