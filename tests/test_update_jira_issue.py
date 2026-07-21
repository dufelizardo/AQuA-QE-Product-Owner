from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, UserStory
from aqua_qe_product_owner.skills import update_jira_issue as module


def test_update_jira_issue_delegates_to_service_with_story_text(monkeypatch):
    captured = {}

    def fake_update_issue_description(issue_key, texto):
        captured["issue_key"] = issue_key
        captured["texto"] = texto

    monkeypatch.setattr(module, "update_issue_description", fake_update_issue_description)

    story = UserStory(
        id="US-001",
        title="Titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        business_rules=[BusinessRule(id="BR-001", description="regra", source_reference="f")],
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="cenario", given="g", when="w", then="t")
        ],
        source_reference="fonte",
    )

    module.update_jira_issue("PROJ-1", story)

    assert captured["issue_key"] == "PROJ-1"
    assert "Titulo" in captured["texto"]
    assert "regra" in captured["texto"]
    assert "cenario" in captured["texto"]
