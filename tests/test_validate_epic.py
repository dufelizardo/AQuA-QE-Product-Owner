from aqua_qe_product_owner.models import AcceptanceCriteria, Epic
from aqua_qe_product_owner.skills.validate_epic import validate_epic


def _epic(**overrides) -> Epic:
    base = {
        "id": "EPIC-001",
        "title": "titulo",
        "objective": "objetivo",
        "scope": "escopo",
        "value": "valor",
        "acceptance_criteria": [
            AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
        ],
    }
    base.update(overrides)
    return Epic(**base)


def test_valid_epic_passes():
    assert validate_epic(_epic()) is True


def test_missing_scope_fails():
    assert validate_epic(_epic(scope="")) is False


def test_missing_value_fails():
    assert validate_epic(_epic(value="")) is False


def test_no_acceptance_criteria_fails():
    assert validate_epic(_epic(acceptance_criteria=[])) is False


def test_incomplete_acceptance_criteria_fails():
    incompleto = [AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="", then="t")]
    assert validate_epic(_epic(acceptance_criteria=incompleto)) is False
