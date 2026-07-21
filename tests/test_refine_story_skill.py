from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, UserStory
from aqua_qe_product_owner.skills import refine_story as module


def test_refine_story_rewrites_fields_from_llm_response(monkeypatch):
    captured_prompt = {}

    def fake_complete_json(prompt, system="", model=None):
        captured_prompt["prompt"] = prompt
        return {
            "descricao": "descrição refinada",
            "regras_negocio": ["regra refinada"],
            "criterios_aceitacao": [
                {"cenario": "c1", "dado": "g1", "quando": "w1", "entao": "t1"}
            ],
        }

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    story = UserStory(
        id="US-001",
        title="titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao original",
        business_rules=[BusinessRule(id="BR-001", description="regra antiga", source_reference="fonte")],
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="antigo", given="g", when="w", then="t")
        ],
        source_reference="fonte",
    )
    respostas = [{"pergunta": "Como validar X?", "resposta": "Assim."}]

    resultado = module.refine_story(story, respostas)

    assert resultado.description == "descrição refinada"
    assert [r.description for r in resultado.business_rules] == ["regra refinada"]
    assert resultado.acceptance_criteria[0].given == "g1"
    assert "Como validar X?" in captured_prompt["prompt"]
    assert "Assim." in captured_prompt["prompt"]


def test_refine_story_keeps_existing_fields_when_llm_returns_nothing(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="", model=None: {})

    story = UserStory(
        id="US-001",
        title="titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao original",
        business_rules=[BusinessRule(id="BR-001", description="regra antiga", source_reference="fonte")],
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="antigo", given="g", when="w", then="t")
        ],
        source_reference="fonte",
    )

    resultado = module.refine_story(story, [])

    assert resultado.description == "descricao original"
    assert [r.description for r in resultado.business_rules] == ["regra antiga"]
    assert resultado.acceptance_criteria[0].scenario == "antigo"
