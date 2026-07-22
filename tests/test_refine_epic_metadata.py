from aqua_qe_product_owner.models import AcceptanceCriteria, Epic
from aqua_qe_product_owner.skills import refine_epic_metadata as module


def _epic() -> Epic:
    return Epic(
        id="EPIC-001",
        title="titulo antigo",
        objective="objetivo antigo",
        scope="escopo antigo",
        value="valor antigo",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
        ],
    )


def test_refine_epic_metadata_com_campos_como_string(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "titulo": "titulo novo",
            "objetivo": "objetivo novo",
            "escopo": "escopo novo",
            "valor": "valor novo",
            "criterios_aceitacao": [
                {"cenario": "c2", "dado": "g2", "quando": "w2", "entao": "t2"}
            ],
        },
    )

    epic = module.refine_epic_metadata(_epic(), [{"pergunta": "p", "resposta": "r"}])

    assert epic.title == "titulo novo"
    assert epic.objective == "objetivo novo"
    assert epic.scope == "escopo novo"
    assert epic.value == "valor novo"
    assert epic.acceptance_criteria[0].given == "g2"


def test_refine_epic_metadata_com_campos_como_lista_normaliza_para_string(monkeypatch):
    """O LLM às vezes devolve escopo/objetivo/valor como lista JSON em vez de string; deve virar texto, nunca repr de lista."""
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "titulo": ["titulo A", "titulo B"],
            "objetivo": ["objetivo A"],
            "escopo": ["item A", "item B"],
            "valor": ["valor A"],
            "criterios_aceitacao": [],
        },
    )

    epic = module.refine_epic_metadata(_epic(), [{"pergunta": "p", "resposta": "r"}])

    assert epic.title == "titulo A; titulo B"
    assert epic.scope == "item A; item B"
    assert "[" not in epic.scope
    assert "[" not in epic.title
