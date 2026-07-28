from aqua_qe_product_owner.skills.record_refinement_answer import (
    record_refinement_answer,
)
from aqua_qe_product_owner.skills.suggest_refinement_answer import (
    suggest_refinement_answer,
)


def test_record_refinement_answer_delega_para_rag_service(monkeypatch):
    capturado = {}

    def fake_record(pergunta, resposta, tipo_artefato):
        capturado["pergunta"] = pergunta
        capturado["resposta"] = resposta
        capturado["tipo_artefato"] = tipo_artefato

    monkeypatch.setattr(
        "aqua_qe_product_owner.skills.record_refinement_answer._record_refinement_answer",
        fake_record,
    )

    record_refinement_answer("pergunta?", "resposta.", "story")

    assert capturado == {"pergunta": "pergunta?", "resposta": "resposta.", "tipo_artefato": "story"}


def test_suggest_refinement_answer_retorna_none_quando_sem_resultado(monkeypatch):
    monkeypatch.setattr(
        "aqua_qe_product_owner.skills.suggest_refinement_answer.find_similar_refinement_answers",
        lambda pergunta, k=1: [],
    )

    assert suggest_refinement_answer("pergunta?") is None


def test_suggest_refinement_answer_retorna_primeiro_resultado(monkeypatch):
    resultado_esperado = {"pergunta": "p", "resposta": "r", "tipo_artefato": "epic", "score": 0.9}

    monkeypatch.setattr(
        "aqua_qe_product_owner.skills.suggest_refinement_answer.find_similar_refinement_answers",
        lambda pergunta, k=1: [resultado_esperado],
    )

    assert suggest_refinement_answer("pergunta?") == resultado_esperado
