from aqua_qe_product_owner.models import UserStory
from aqua_qe_product_owner.skills import create_jira_story as module


def test_create_jira_story_delegates_to_service_with_parent_key(monkeypatch):
    monkeypatch.setenv("JIRA_PROJECT_KEY", "AQUAQE")
    monkeypatch.setenv("JIRA_STORY_ISSUE_TYPE_ID", "10041")

    captured = {}

    def fake_create_issue(project_key, issue_type_id, summary, texto, parent_key=None):
        captured.update(
            project_key=project_key,
            issue_type_id=issue_type_id,
            summary=summary,
            texto=texto,
            parent_key=parent_key,
        )
        return "AQUAQE-11"

    monkeypatch.setattr(module, "create_issue", fake_create_issue)

    story = UserStory(
        id="US-001",
        title="Titulo da Story",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        source_reference="fonte",
    )

    resultado = module.create_jira_story(story, "AQUAQE-10")

    assert resultado == "AQUAQE-11"
    assert captured["project_key"] == "AQUAQE"
    assert captured["issue_type_id"] == "10041"
    assert captured["summary"] == "Titulo da Story"
    assert captured["parent_key"] == "AQUAQE-10"
    assert "Como ator" in captured["texto"]
