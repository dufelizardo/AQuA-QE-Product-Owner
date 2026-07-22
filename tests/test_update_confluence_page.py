from aqua_qe_product_owner.models import PRDDraft
from aqua_qe_product_owner.skills import update_confluence_page as module


def test_update_confluence_page_delegates_to_service_with_formatted_prd(monkeypatch):
    captured = {}

    def fake_update_page(page_id, texto):
        captured["page_id"] = page_id
        captured["texto"] = texto

    monkeypatch.setattr(module, "update_page", fake_update_page)

    draft = PRDDraft(
        context_problem="contexto",
        objective="objetivo do produto",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )

    module.update_confluence_page("163841", draft)

    assert captured["page_id"] == "163841"
    assert "objetivo do produto" in captured["texto"]
    assert "requisito 1" in captured["texto"]
