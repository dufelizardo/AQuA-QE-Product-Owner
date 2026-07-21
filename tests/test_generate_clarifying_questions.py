from aqua_qe_product_owner.models import UserStory
from aqua_qe_product_owner.skills import generate_clarifying_questions as module


def _story(**overrides) -> UserStory:
    base = {
        "id": "US-001",
        "title": "titulo",
        "actor": "ator",
        "goal": "objetivo",
        "benefit": "beneficio",
        "description": "descricao",
        "source_reference": "fonte",
    }
    base.update(overrides)
    return UserStory(**base)


def test_returns_empty_list_without_review_notes():
    story = _story(review_notes=[])

    assert module.generate_clarifying_questions(story) == []


def test_maps_json_response_to_question_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "perguntas": ["Como validar X?", "Qual o formato de Y?"]
        },
    )
    story = _story(review_notes=["critério vago"])

    resultado = module.generate_clarifying_questions(story)

    assert resultado == ["Como validar X?", "Qual o formato de Y?"]


def test_normalizes_questions_returned_as_objects(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "perguntas": [{"texto": "Como validar X?"}, {"pergunta": "Qual o formato de Y?"}]
        },
    )
    story = _story(review_notes=["critério vago"])

    resultado = module.generate_clarifying_questions(story)

    assert resultado == ["Como validar X?", "Qual o formato de Y?"]


def test_normalizes_questions_with_capitalized_keys(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "perguntas": [{"Pergunta": "Como validar X?", "Razão": "porque sim"}]
        },
    )
    story = _story(review_notes=["critério vago"])

    resultado = module.generate_clarifying_questions(story)

    assert resultado == ["Como validar X?"]
