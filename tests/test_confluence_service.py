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


def test_texto_para_storage_wraps_lines_in_paragraphs_and_escapes_html():
    resultado = confluence_service._texto_para_storage("Linha 1\n\nLinha & <2>")

    assert resultado == "<p>Linha 1</p><p>Linha &amp; &lt;2&gt;</p>"


def test_create_page_posts_expected_body_and_returns_id(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_post(url, auth=None, json=None, timeout=None):
        captured.update(url=url, auth=auth, json=json)
        return _FakeResponse({"id": "163841"})

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = confluence_service.create_page("AQUAQE", "Titulo", "Corpo da pagina")

    assert resultado == "163841"
    assert captured["url"] == "https://example.atlassian.net/wiki/rest/api/content"
    assert captured["json"]["space"] == {"key": "AQUAQE"}
    assert captured["json"]["title"] == "Titulo"
    assert captured["json"]["body"]["storage"]["value"] == "<p>Corpo da pagina</p>"
    assert "ancestors" not in captured["json"]


def test_create_page_includes_ancestors_when_parent_given(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    captured = {}

    def fake_post(url, auth=None, json=None, timeout=None):
        captured.update(json=json)
        return _FakeResponse({"id": "163842"})

    monkeypatch.setattr(httpx, "post", fake_post)

    confluence_service.create_page("AQUAQE", "Titulo", "Corpo", parent_page_id="163841")

    assert captured["json"]["ancestors"] == [{"id": "163841"}]


def test_update_page_fetches_current_version_and_puts_incremented(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    def fake_get(url, auth=None, params=None, timeout=None):
        assert url == "https://example.atlassian.net/wiki/rest/api/content/163841"
        assert params == {"expand": "version"}
        return _FakeResponse({"title": "PRD existente", "version": {"number": 1}})

    captured = {}

    def fake_put(url, auth=None, json=None, timeout=None):
        captured.update(url=url, json=json)
        return _FakeResponse({"version": {"number": 2}})

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(httpx, "put", fake_put)

    confluence_service.update_page("163841", "Corpo atualizado")

    assert captured["url"] == "https://example.atlassian.net/wiki/rest/api/content/163841"
    assert captured["json"]["title"] == "PRD existente"
    assert captured["json"]["version"] == {"number": 2}
    assert captured["json"]["body"]["storage"]["value"] == "<p>Corpo atualizado</p>"
