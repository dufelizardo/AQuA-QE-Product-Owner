from aqua_qe_product_owner.skills import read_confluence_page as module


def test_extracts_page_id_from_full_url(monkeypatch):
    captured = {}

    def fake_get_page_text(page_id):
        captured["page_id"] = page_id
        return "texto"

    monkeypatch.setattr(module, "get_page_text", fake_get_page_text)

    url = (
        "https://edufelizardo.atlassian.net/wiki/spaces/~70121c6abcd6/"
        "pages/163841/Sistema+de+Agendamento"
    )
    resultado = module.read_confluence_page(url)

    assert captured["page_id"] == "163841"
    assert resultado == "texto"


def test_accepts_plain_page_id(monkeypatch):
    captured = {}
    monkeypatch.setattr(module, "get_page_text", lambda page_id: captured.setdefault("page_id", page_id) or "texto")

    module.read_confluence_page("163841")

    assert captured["page_id"] == "163841"
