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
    assert validate_epic(_epic()) == []


def test_missing_title_fails():
    assert "título ausente" in validate_epic(_epic(title=""))


def test_missing_objective_fails():
    assert "objetivo ausente" in validate_epic(_epic(objective=""))


def test_missing_scope_fails():
    assert "escopo ausente" in validate_epic(_epic(scope=""))


def test_missing_value_fails():
    assert "valor ausente" in validate_epic(_epic(value=""))


def test_no_acceptance_criteria_fails():
    assert "nenhum critério de aceitação identificado" in validate_epic(
        _epic(acceptance_criteria=[])
    )


def test_incomplete_acceptance_criteria_fails():
    incompleto = [AcceptanceCriteria(id="AC-001", scenario="c", given="g", when="", then="t")]
    assert "critério de aceitação incompleto (Given/When/Then)" in validate_epic(
        _epic(acceptance_criteria=incompleto)
    )


def test_multiplos_motivos_acumulam_em_vez_de_parar_no_primeiro():
    motivos = validate_epic(_epic(title="", value=""))
    assert "título ausente" in motivos
    assert "valor ausente" in motivos
