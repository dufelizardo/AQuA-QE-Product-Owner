from aqua_qe_product_owner.skills import read_jira_issue as module


def test_read_jira_issue_delegates_to_service(monkeypatch):
    monkeypatch.setattr(module, "get_issue_text", lambda issue_key: f"texto-{issue_key}")

    assert module.read_jira_issue("PROJ-1") == "texto-PROJ-1"
