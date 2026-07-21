from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, Requirement, UserStory
from aqua_qe_product_owner.skills import extract_prd_context as extract_prd_context_module
from aqua_qe_product_owner.skills import extract_requirements as extract_requirements_module
from aqua_qe_product_owner.skills import generate_story as generate_story_module
from aqua_qe_product_owner.skills import identify_actor as identify_actor_module
from aqua_qe_product_owner.skills import identify_business_rules as identify_business_rules_module
from aqua_qe_product_owner.skills import identify_goal as identify_goal_module
from aqua_qe_product_owner.skills import review_story as review_story_module


def test_extract_requirements_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        extract_requirements_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "requisitos": [{"texto": "requisito 1", "trecho_fonte": "trecho 1"}]
        },
    )

    resultado = extract_requirements_module.extract_requirements("texto")

    assert resultado == [Requirement(id="REQ-001", text="requisito 1", source_reference="trecho 1")]


def test_extract_prd_context_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        extract_prd_context_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "visao": "visao do produto",
            "problema": "problema de negocio",
            "objetivos": ["objetivo 1"],
            "publico_alvo": "clientes pessoa fisica",
            "requisitos_nao_funcionais": ["responder em menos de 2s"],
            "restricoes": ["so app mobile"],
            "criterios_sucesso": ["90% de conclusao"],
            "riscos": ["indisponibilidade do provedor de pagamento"],
            "dependencias": ["servico de KYC"],
        },
    )

    contexto = extract_prd_context_module.extract_prd_context("texto")

    assert contexto.vision == "visao do produto"
    assert contexto.problem == "problema de negocio"
    assert contexto.objectives == ["objetivo 1"]
    assert contexto.target_audience == "clientes pessoa fisica"
    assert contexto.non_functional_requirements == ["responder em menos de 2s"]
    assert contexto.constraints == ["so app mobile"]
    assert contexto.success_criteria == ["90% de conclusao"]
    assert contexto.risks == ["indisponibilidade do provedor de pagamento"]
    assert contexto.dependencies == ["servico de KYC"]


def test_extract_prd_context_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(
        extract_prd_context_module,
        "complete_json",
        lambda prompt, system="", model=None: {},
    )

    contexto = extract_prd_context_module.extract_prd_context("texto")

    assert contexto.vision == ""
    assert contexto.objectives == []
    assert contexto.non_functional_requirements == []


def test_identify_actor_returns_empty_when_llm_finds_none(monkeypatch):
    monkeypatch.setattr(
        identify_actor_module,
        "complete_json",
        lambda prompt, system="", model=None: {"ator": None},
    )

    assert identify_actor_module.identify_actor("texto") == ""


def test_identify_goal_returns_value(monkeypatch):
    monkeypatch.setattr(
        identify_goal_module,
        "complete_json",
        lambda prompt, system="", model=None: {"objetivo": "fazer algo"},
    )

    assert identify_goal_module.identify_goal("texto") == "fazer algo"


def test_identify_business_rules_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        identify_business_rules_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "regras": [{"descricao": "regra 1", "trecho_fonte": "trecho"}]
        },
    )

    resultado = identify_business_rules_module.identify_business_rules("texto")

    assert resultado == [BusinessRule(id="BR-001", description="regra 1", source_reference="trecho")]


def test_generate_story_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        generate_story_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "titulo": "titulo gerado",
            "beneficio": "beneficio gerado",
            "descricao": "descricao gerada",
            "criterios_aceitacao": [{"cenario": "c", "dado": "g", "quando": "w", "entao": "t"}],
        },
    )

    story = generate_story_module.generate_story(
        "ator", "objetivo", {"business_rules": [], "texto_fonte": "fonte"}
    )

    assert story.title == "titulo gerado"
    assert story.acceptance_criteria[0].given == "g"
    assert story.source_reference == "fonte"


def test_review_story_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(review_story_module, "complete_json", fake_complete_json)
    story = UserStory(
        id="US-001",
        title="t",
        actor="a",
        goal="g",
        benefit="b",
        description="d",
        acceptance_criteria=[AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")],
        source_reference="fonte",
    )

    resultado = review_story_module.review_story(story)

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"
