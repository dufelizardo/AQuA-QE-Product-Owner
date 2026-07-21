from aqua_qe_product_owner.models import UserStory
from aqua_qe_product_owner.skills import generate_epic_metadata as module


def test_generate_epic_metadata_passes_story_summaries_and_returns_llm_json(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        return {
            "titulo": "titulo",
            "objetivo": "objetivo",
            "escopo": "escopo",
            "valor": "valor",
            "criterios_aceitacao": [{"cenario": "c", "dado": "g", "quando": "w", "entao": "t"}],
        }

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    stories = [
        UserStory(
            id="US-001",
            title="titulo story",
            actor="ator",
            goal="objetivo story",
            benefit="beneficio",
            description="descricao",
            source_reference="fonte",
        )
    ]

    resultado = module.generate_epic_metadata("texto de origem", stories)

    assert resultado["titulo"] == "titulo"
    assert resultado["criterios_aceitacao"][0]["dado"] == "g"
    assert "titulo story" in captured["prompt"]
    assert "objetivo story" in captured["prompt"]
    assert "texto de origem" in captured["prompt"]
