from aqua_qe_product_owner.models import (
    AcceptanceCriteria,
    BusinessRule,
    PRDDraft,
    Requirement,
    UserStory,
)
from aqua_qe_product_owner.skills import extract_prd_context as extract_prd_context_module
from aqua_qe_product_owner.skills import extract_requirements as extract_requirements_module
from aqua_qe_product_owner.skills import generate_prd as generate_prd_module
from aqua_qe_product_owner.skills import (
    generate_prd_clarifying_questions as generate_prd_clarifying_questions_module,
)
from aqua_qe_product_owner.skills import generate_story as generate_story_module
from aqua_qe_product_owner.skills import identify_actor as identify_actor_module
from aqua_qe_product_owner.skills import identify_business_rules as identify_business_rules_module
from aqua_qe_product_owner.skills import identify_goal as identify_goal_module
from aqua_qe_product_owner.skills import refine_prd as refine_prd_module
from aqua_qe_product_owner.skills import review_prd as review_prd_module
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


def test_generate_prd_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        generate_prd_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "contexto_problema": "contexto",
            "objetivo": "objetivo do produto",
            "publico_alvo": "publico",
            "escopo": "escopo",
            "fora_de_escopo": "fora de escopo",
            "requisitos_funcionais": ["requisito 1"],
            "requisitos_nao_funcionais": ["requisito nf 1"],
            "criterios_sucesso": ["criterio 1"],
            "riscos_premissas": ["risco 1"],
        },
    )

    draft = generate_prd_module.generate_prd("uma ideia")

    assert draft.objective == "objetivo do produto"
    assert draft.functional_requirements == ["requisito 1"]
    assert draft.risks_assumptions == ["risco 1"]


def test_generate_prd_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(
        generate_prd_module, "complete_json", lambda prompt, system="", model=None: {}
    )

    draft = generate_prd_module.generate_prd("uma ideia")

    assert draft.objective == ""
    assert draft.functional_requirements == []


def test_review_prd_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": False, "problemas": ["escopo confuso"]}

    monkeypatch.setattr(review_prd_module, "complete_json", fake_complete_json)

    resultado = review_prd_module.review_prd(PRDDraft(objective="o", scope="e"))

    assert resultado == {"aprovado": False, "problemas": ["escopo confuso"]}
    assert captured["model"] == "phi4"


def test_generate_prd_clarifying_questions_returns_empty_without_review_notes():
    assert generate_prd_clarifying_questions_module.generate_prd_clarifying_questions(
        PRDDraft()
    ) == []


def test_generate_prd_clarifying_questions_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        generate_prd_clarifying_questions_module,
        "complete_json",
        lambda prompt, system="", model=None: {"perguntas": ["Qual o publico-alvo?"]},
    )

    draft = PRDDraft(objective="o", scope="e", review_notes=["publico-alvo indefinido"])
    perguntas = generate_prd_clarifying_questions_module.generate_prd_clarifying_questions(draft)

    assert perguntas == ["Qual o publico-alvo?"]


def test_refine_prd_rewrites_fields_from_answers(monkeypatch):
    monkeypatch.setattr(
        refine_prd_module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "contexto_problema": "contexto",
            "objetivo": "objetivo refinado",
            "publico_alvo": "publico refinado",
            "escopo": "escopo",
            "fora_de_escopo": "",
            "requisitos_funcionais": ["requisito 1"],
            "requisitos_nao_funcionais": [],
            "criterios_sucesso": ["criterio 1"],
            "riscos_premissas": [],
        },
    )

    draft = PRDDraft(
        context_problem="contexto",
        objective="objetivo antigo",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )
    resultado = refine_prd_module.refine_prd(
        draft, [{"pergunta": "qual o publico-alvo?", "resposta": "publico refinado"}]
    )

    assert resultado.objective == "objetivo refinado"
    assert resultado.target_audience == "publico refinado"
