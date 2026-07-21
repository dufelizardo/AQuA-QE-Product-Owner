import pytest

from aqua_qe_product_owner.orchestrator import product_owner


def test_modo_unitario_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_user_story(texto):
        chamada["texto"] = texto
        return "story-fake"

    monkeypatch.setattr(product_owner, "generate_user_story", fake_generate_user_story)

    resultado = product_owner.handle_request("entrada", "unitario")

    assert resultado == "story-fake"
    assert chamada["texto"] == "entrada"


def test_modo_lote_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_epic(texto):
        chamada["texto"] = texto
        return "epic-fake"

    monkeypatch.setattr(product_owner, "generate_epic", fake_generate_epic)

    resultado = product_owner.handle_request("entrada", "lote")

    assert resultado == "epic-fake"
    assert chamada["texto"] == "entrada"


def test_modo_invalido_levanta_not_implemented():
    with pytest.raises(NotImplementedError):
        product_owner.handle_request("entrada", "modo-inexistente")
