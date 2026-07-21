from aqua_qe_product_owner.models import PRDDraft, StoryStatus
from aqua_qe_product_owner.workflow import generate_prd as workflow_module


def _draft_valido() -> PRDDraft:
    return PRDDraft(
        context_problem="contexto",
        objective="objetivo",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )


def test_finalize_prd_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: False)

    resultado = workflow_module.finalize_prd(PRDDraft())

    assert resultado.status == StoryStatus.PENDING_CLARIFICATION


def test_finalize_prd_marca_pending_clarification_quando_review_reprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module,
        "review_prd",
        lambda draft: {"aprovado": False, "problemas": ["escopo confuso"]},
    )

    resultado = workflow_module.finalize_prd(_draft_valido())

    assert resultado.status == StoryStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["escopo confuso"]


def test_finalize_prd_marca_draft_validated_quando_review_aprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    resultado = workflow_module.finalize_prd(_draft_valido())

    assert resultado.status == StoryStatus.DRAFT_VALIDATED


def test_generate_prd_draft_gera_e_finaliza(monkeypatch):
    monkeypatch.setattr(workflow_module, "generate_prd", lambda ideia: _draft_valido())
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft = workflow_module.generate_prd_draft("uma ideia qualquer")

    assert draft.status == StoryStatus.DRAFT_VALIDATED
    assert draft.objective == "objetivo"


def test_refine_prd_draft_refina_e_finaliza(monkeypatch):
    def fake_refine_prd(draft, respostas):
        draft.objective = "objetivo refinado"
        return draft

    monkeypatch.setattr(workflow_module, "refine_prd", fake_refine_prd)
    monkeypatch.setattr(workflow_module, "validate_prd", lambda draft: True)
    monkeypatch.setattr(
        workflow_module, "review_prd", lambda draft: {"aprovado": True, "problemas": []}
    )

    draft = workflow_module.refine_prd_draft(
        _draft_valido(), [{"pergunta": "qual objetivo?", "resposta": "objetivo refinado"}]
    )

    assert draft.objective == "objetivo refinado"
    assert draft.status == StoryStatus.DRAFT_VALIDATED
