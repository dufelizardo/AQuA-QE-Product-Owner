from aqua_qe_product_owner.models import AcceptanceCriteria, Epic
from aqua_qe_product_owner.skills import create_jira_epic as module


def test_create_jira_epic_delegates_to_service_with_expected_fields(monkeypatch):
    monkeypatch.setenv("JIRA_PROJECT_KEY", "AQUAQE")
    monkeypatch.setenv("JIRA_EPIC_ISSUE_TYPE_ID", "10039")

    captured = {}

    def fake_create_issue(project_key, issue_type_id, summary, texto, parent_key=None):
        captured.update(
            project_key=project_key,
            issue_type_id=issue_type_id,
            summary=summary,
            texto=texto,
            parent_key=parent_key,
        )
        return "AQUAQE-10"

    monkeypatch.setattr(module, "create_issue", fake_create_issue)

    epic = Epic(
        id="EPIC-001",
        title="Titulo do Epico",
        objective="objetivo",
        scope="escopo",
        value="valor",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="cenario", given="g", when="w", then="t")
        ],
    )

    resultado = module.create_jira_epic(epic)

    assert resultado == "AQUAQE-10"
    assert captured["project_key"] == "AQUAQE"
    assert captured["issue_type_id"] == "10039"
    assert captured["summary"] == "Titulo do Epico"
    assert captured["parent_key"] is None
    assert "objetivo" in captured["texto"]
    assert "cenario" in captured["texto"]
