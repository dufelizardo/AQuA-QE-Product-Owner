import httpx

from aqua_qe_product_owner.services import jira_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_get_issue_text_extracts_summary_and_description(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {
        "fields": {
            "summary": "Titulo do ticket",
            "description": {
                "type": "doc",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "Primeira linha."}]},
                    {"type": "paragraph", "content": [{"type": "text", "text": "Segunda linha."}]},
                ],
            },
        }
    }

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/rest/api/3/issue/PROJ-123"
        assert auth == ("user@example.com", "token")
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    resultado = jira_service.get_issue_text("PROJ-123")

    assert "Titulo do ticket" in resultado
    assert "Primeira linha." in resultado
    assert "Segunda linha." in resultado


def test_get_issue_text_handles_missing_description(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {"fields": {"summary": "Só resumo", "description": None}}
    monkeypatch.setattr(httpx, "get", lambda *a, **k: _FakeResponse(payload))

    assert jira_service.get_issue_text("PROJ-1") == "Só resumo"


def test_get_issue_text_strips_trailing_slash_from_base_url(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net/")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_get(url, auth=None, params=None, timeout=None):
        captured["url"] = url
        return _FakeResponse({"fields": {"summary": "s", "description": None}})

    monkeypatch.setattr(httpx, "get", fake_get)

    jira_service.get_issue_text("PROJ-1")

    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue/PROJ-1"


def test_texto_para_adf_creates_one_paragraph_per_nonempty_line():
    adf = jira_service._texto_para_adf("linha 1\n\nlinha 2")

    assert adf["type"] == "doc"
    assert len(adf["content"]) == 2
    assert adf["content"][0]["content"][0]["text"] == "linha 1"
    assert adf["content"][1]["content"][0]["text"] == "linha 2"


def test_update_issue_description_sends_put_with_adf_body(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_put(url, auth=None, json=None, timeout=None):
        captured["url"] = url
        captured["auth"] = auth
        captured["json"] = json
        return _FakeResponse({})

    monkeypatch.setattr(httpx, "put", fake_put)

    jira_service.update_issue_description("PROJ-123", "novo texto")

    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue/PROJ-123"
    assert captured["auth"] == ("user@example.com", "token")
    assert captured["json"]["fields"]["description"]["type"] == "doc"


def test_create_issue_sends_post_and_returns_key(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_post(url, auth=None, json=None, timeout=None):
        captured["url"] = url
        captured["auth"] = auth
        captured["json"] = json
        return _FakeResponse({"key": "PROJ-42"})

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = jira_service.create_issue("PROJ", "10039", "Meu titulo", "meu texto")

    assert resultado == "PROJ-42"
    assert captured["url"] == "https://example.atlassian.net/rest/api/3/issue"
    assert captured["json"]["fields"]["project"] == {"key": "PROJ"}
    assert captured["json"]["fields"]["issuetype"] == {"id": "10039"}
    assert captured["json"]["fields"]["summary"] == "Meu titulo"
    assert "parent" not in captured["json"]["fields"]


def test_create_issue_includes_parent_when_provided(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_post(url, auth=None, json=None, timeout=None):
        captured["json"] = json
        return _FakeResponse({"key": "PROJ-43"})

    monkeypatch.setattr(httpx, "post", fake_post)

    jira_service.create_issue("PROJ", "10041", "titulo", "texto", parent_key="PROJ-42")

    assert captured["json"]["fields"]["parent"] == {"key": "PROJ-42"}
