from aqua_qe_product_owner.models import AcceptanceCriteria, Epic
from aqua_qe_product_owner.skills import update_jira_epic as module


def test_update_jira_epic_delegates_to_service_with_epic_text(monkeypatch):
    captured = {}

    def fake_update_issue_description(issue_key, texto):
        captured["issue_key"] = issue_key
        captured["texto"] = texto

    monkeypatch.setattr(module, "update_issue_description", fake_update_issue_description)

    epic = Epic(
        id="EPIC-001",
        title="Titulo",
        objective="objetivo",
        scope="escopo",
        value="valor",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="cenario", given="g", when="w", then="t")
        ],
    )

    module.update_jira_epic("PROJ-1", epic)

    assert captured["issue_key"] == "PROJ-1"
    assert "objetivo" in captured["texto"]
    assert "escopo" in captured["texto"]
    assert "cenario" in captured["texto"]
