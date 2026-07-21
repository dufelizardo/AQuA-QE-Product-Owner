import pytest

from aqua_qe_product_owner.services import llm_service


def test_complete_returns_content(monkeypatch):
    def fake_chat(self, model, messages, format=None):
        return {"message": {"content": "resposta de teste"}}

    monkeypatch.setattr("ollama.Client.chat", fake_chat)

    assert llm_service.complete("prompt qualquer") == "resposta de teste"


def test_complete_json_parses_valid_json(monkeypatch):
    def fake_chat(self, model, messages, format=None):
        return {"message": {"content": '{"chave": "valor"}'}}

    monkeypatch.setattr("ollama.Client.chat", fake_chat)

    assert llm_service.complete_json("prompt qualquer") == {"chave": "valor"}


def test_complete_json_raises_on_invalid_json(monkeypatch):
    def fake_chat(self, model, messages, format=None):
        return {"message": {"content": "isso não é JSON"}}

    monkeypatch.setattr("ollama.Client.chat", fake_chat)

    with pytest.raises(ValueError):
        llm_service.complete_json("prompt qualquer")


def test_complete_json_uses_explicit_model_override(monkeypatch):
    captured = {}

    def fake_chat(self, model, messages, format=None):
        captured["model"] = model
        return {"message": {"content": "{}"}}

    monkeypatch.setattr("ollama.Client.chat", fake_chat)

    llm_service.complete_json("prompt", model="phi4")

    assert captured["model"] == "phi4"
