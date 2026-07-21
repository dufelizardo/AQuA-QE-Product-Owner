from aqua_qe_product_owner.models import PRDDraft
from aqua_qe_product_owner.skills import create_confluence_page as module


def test_create_confluence_page_delegates_to_service_and_returns_url(monkeypatch):
    monkeypatch.setenv("CONFLUENCE_SPACE_KEY", "AQUAQE")
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")

    captured = {}

    def fake_create_page(space_key, title, texto, parent_page_id=None):
        captured.update(space_key=space_key, title=title, texto=texto)
        return "163841"

    monkeypatch.setattr(module, "create_page", fake_create_page)

    draft = PRDDraft(
        context_problem="contexto",
        objective="objetivo do produto",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )

    resultado = module.create_confluence_page(draft, "PRD gerado")

    assert resultado == "https://example.atlassian.net/wiki/pages/viewpage.action?pageId=163841"
    assert captured["space_key"] == "AQUAQE"
    assert captured["title"] == "PRD gerado"
    assert "objetivo do produto" in captured["texto"]
