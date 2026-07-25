from aqua_qe_product_owner.models import AcceptanceCriteria, Epic, UserStory
from aqua_qe_product_owner.skills import review_epic as module


def test_review_epic_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        captured["prompt"] = prompt
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    epic = Epic(
        id="EPIC-001",
        title="titulo",
        objective="objetivo",
        scope="escopo",
        value="valor",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
        ],
        stories=[
            UserStory(
                id="US-001",
                title="story",
                actor="ator",
                goal="objetivo story",
                benefit="beneficio",
                description="descricao",
                source_reference="fonte",
            )
        ],
    )

    resultado = module.review_epic(epic)

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"
    assert "objetivo story" in captured["prompt"]


def test_review_epic_sem_stories_nao_pede_coerencia_com_stories(monkeypatch):
    """Regressão (Issue #3): na fase de shape (sem stories ainda, por design), review_epic não deve
    pedir/considerar coerência com User Stories nem dar margem para reclamar da ausência delas."""
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["prompt"] = prompt
        captured["system"] = system
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    epic = Epic(
        id="EPIC-001",
        title="titulo",
        objective="objetivo",
        scope="escopo",
        value="valor",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
        ],
    )

    module.review_epic(epic)

    assert "User Stories agrupadas" not in captured["prompt"]
    assert "esperado nesta fase" in captured["system"]
