from aqua_qe_product_owner.models import Epic
from aqua_qe_product_owner.skills import generate_epic_clarifying_questions as module


def _epic(**overrides) -> Epic:
    base = {
        "id": "EPIC-001",
        "title": "titulo",
        "objective": "objetivo",
    }
    base.update(overrides)
    return Epic(**base)


def test_returns_empty_list_without_review_notes():
    epic = _epic(review_notes=[])

    assert module.generate_epic_clarifying_questions(epic) == []


def test_maps_json_response_to_question_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"perguntas": ["Como validar X?", "Qual o formato de Y?"]},
    )
    epic = _epic(review_notes=["escopo vago"])

    resultado = module.generate_epic_clarifying_questions(epic)

    assert resultado == ["Como validar X?", "Qual o formato de Y?"]


def test_normalizes_questions_returned_as_objects(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "perguntas": [{"texto": "Como validar X?"}, {"pergunta": "Qual o formato de Y?"}]
        },
    )
    epic = _epic(review_notes=["escopo vago"])

    resultado = module.generate_epic_clarifying_questions(epic)

    assert resultado == ["Como validar X?", "Qual o formato de Y?"]


def test_normalizes_questions_with_capitalized_keys(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "perguntas": [{"Pergunta": "Como validar X?", "Razão": "porque sim"}]
        },
    )
    epic = _epic(review_notes=["escopo vago"])

    resultado = module.generate_epic_clarifying_questions(epic)

    assert resultado == ["Como validar X?"]
