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
    assert validate_story(_story()) == []


def test_missing_source_reference_fails():
    assert "referência à fonte ausente" in validate_story(_story(source_reference=""))


def test_missing_actor_fails():
    assert "ator ausente" in validate_story(_story(actor=""))


def test_missing_goal_fails():
    assert "objetivo ausente" in validate_story(_story(goal=""))


def test_missing_benefit_fails():
    assert "benefício ausente" in validate_story(_story(benefit=""))


def test_no_acceptance_criteria_fails():
    assert "nenhum critério de aceitação identificado" in validate_story(
        _story(acceptance_criteria=[])
    )


def test_incomplete_acceptance_criteria_fails():
    incompleto = [AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="", then="t")]
    assert "critério de aceitação incompleto (Given/When/Then)" in validate_story(
        _story(acceptance_criteria=incompleto)
    )


def test_multiplos_motivos_acumulam_em_vez_de_parar_no_primeiro():
    motivos = validate_story(_story(actor="", benefit=""))
    assert "ator ausente" in motivos
    assert "benefício ausente" in motivos
