from aqua_qe_product_owner.models import AcceptanceCriteria, UserStory
from aqua_qe_product_owner.skills.validate_story import validate_story


def _story(**overrides) -> UserStory:
    base = {
        "id": "US-001",
        "title": "titulo",
        "actor": "ator",
        "goal": "objetivo",
        "benefit": "beneficio",
        "description": "descricao",
        "acceptance_criteria": [
            AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="w", then="t")
        ],
        "source_reference": "fonte",
    }
    base.update(overrides)
    return UserStory(**base)


def test_valid_story_passes():
    assert validate_story(_story()) is True


def test_missing_source_reference_fails():
    assert validate_story(_story(source_reference="")) is False


def test_missing_actor_fails():
    assert validate_story(_story(actor="")) is False


def test_missing_goal_fails():
    assert validate_story(_story(goal="")) is False


def test_missing_benefit_fails():
    assert validate_story(_story(benefit="")) is False


def test_no_acceptance_criteria_fails():
    assert validate_story(_story(acceptance_criteria=[])) is False


def test_incomplete_acceptance_criteria_fails():
    incompleto = [AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="", then="t")]
    assert validate_story(_story(acceptance_criteria=incompleto)) is False
