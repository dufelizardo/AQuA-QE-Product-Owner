from aqua_qe_product_owner.models import PRDDraft
from aqua_qe_product_owner.skills import refine_prd as module


def _draft() -> PRDDraft:
    return PRDDraft(
        context_problem="contexto",
        objective="objetivo",
        scope="escopo antigo",
        out_of_scope="fora antigo",
        functional_requirements=["req 1"],
    )


def test_refine_prd_com_escopo_como_string(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"escopo": "escopo novo", "fora_de_escopo": "fora novo"},
    )

    draft = module.refine_prd(_draft(), [{"pergunta": "p", "resposta": "r"}])

    assert draft.scope == "escopo novo"
    assert draft.out_of_scope == "fora novo"


def test_refine_prd_com_escopo_como_lista_normaliza_para_string(monkeypatch):
    """O LLM às vezes devolve escopo/fora_de_escopo como lista JSON em vez de string; deve virar texto, nunca repr de lista."""
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "escopo": ["item A", "item B"],
            "fora_de_escopo": ["item C"],
        },
    )

    draft = module.refine_prd(_draft(), [{"pergunta": "p", "resposta": "r"}])

    assert draft.scope == "item A; item B"
    assert draft.out_of_scope == "item C"
    assert "[" not in draft.scope
