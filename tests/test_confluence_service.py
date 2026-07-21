import httpx

from aqua_qe_product_owner.services import confluence_service


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_storage_para_texto_strips_tags_and_decodes_entities():
    html = "<h1>T&iacute;tulo</h1><p>Primeiro par&aacute;grafo.</p><ul><li>Item 1</li></ul>"

    resultado = confluence_service._storage_para_texto(html)

    assert "Título" in resultado
    assert "Primeiro parágrafo." in resultado
    assert "Item 1" in resultado


def test_get_page_text_extracts_title_and_body(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    payload = {
        "title": "Meu PRD",
        "body": {"storage": {"value": "<p>Conteúdo da página.</p>"}},
    }

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/wiki/rest/api/content/163841"
        assert auth == ("user@example.com", "token")
        assert params == {"expand": "body.storage"}
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "get", fake_get)

    resultado = confluence_service.get_page_text("163841")

    assert "Meu PRD" in resultado
    assert "Conteúdo da página." in resultado
