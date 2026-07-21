from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, StoryStatus, UserStory
from aqua_qe_product_owner.workflow import generate_user_story as workflow_module


def test_ambiguous_input_returns_pending_clarification(monkeypatch):
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "")

    story = workflow_module.generate_user_story("texto vago")

    assert story.status == StoryStatus.PENDING_CLARIFICATION
    assert story.id == "US-000"


def test_happy_path_marks_draft_validated_when_review_approves(monkeypatch):
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "cliente")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "fazer algo")
    monkeypatch.setattr(workflow_module, "extract_requirements", lambda texto: [])
    monkeypatch.setattr(
        workflow_module,
        "identify_business_rules",
        lambda texto: [BusinessRule(id="BR-001", description="regra", source_reference="fonte")],
    )

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id="US-001",
            title="titulo",
            actor=ator,
            goal=objetivo,
            benefit="beneficio",
            description="descricao",
            acceptance_criteria=[
                AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
            ],
            business_rules=contexto["business_rules"],
            source_reference=contexto["texto_fonte"],
        )

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(workflow_module, "review_story", lambda story: {"aprovado": True, "problemas": []})

    story = workflow_module.generate_user_story("texto de entrada")

    assert story.status == StoryStatus.DRAFT_VALIDATED
    assert story.review_notes == []


def test_review_rejection_marks_pending_clarification(monkeypatch):
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "cliente")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "fazer algo")
    monkeypatch.setattr(workflow_module, "extract_requirements", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_business_rules", lambda texto: [])

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id="US-001",
            title="titulo",
            actor=ator,
            goal=objetivo,
            benefit="beneficio",
            description="descricao",
            acceptance_criteria=[
                AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
            ],
            source_reference=contexto["texto_fonte"],
        )

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(
        workflow_module,
        "review_story",
        lambda story: {"aprovado": False, "problemas": ["critério vago"]},
    )

    story = workflow_module.generate_user_story("texto de entrada")

    assert story.status == StoryStatus.PENDING_CLARIFICATION
    assert story.review_notes == ["critério vago"]


def test_validate_story_failure_skips_review(monkeypatch):
    monkeypatch.setattr(workflow_module, "identify_actor", lambda texto: "cliente")
    monkeypatch.setattr(workflow_module, "identify_goal", lambda texto: "fazer algo")
    monkeypatch.setattr(workflow_module, "extract_requirements", lambda texto: [])
    monkeypatch.setattr(workflow_module, "identify_business_rules", lambda texto: [])

    def fake_generate_story(ator, objetivo, contexto):
        return UserStory(
            id="US-001",
            title="",
            actor=ator,
            goal=objetivo,
            benefit="",
            description="",
            source_reference=contexto["texto_fonte"],
        )

    chamou_review = {"valor": False}

    def fake_review_story(story):
        chamou_review["valor"] = True
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(workflow_module, "generate_story", fake_generate_story)
    monkeypatch.setattr(workflow_module, "review_story", fake_review_story)

    story = workflow_module.generate_user_story("texto de entrada")

    assert story.status == StoryStatus.PENDING_CLARIFICATION
    assert chamou_review["valor"] is False
