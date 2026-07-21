from aqua_qe_product_owner.models import PRDDraft
from aqua_qe_product_owner.skills.validate_prd import validate_prd


def _draft(**overrides) -> PRDDraft:
    base = {
        "context_problem": "contexto",
        "objective": "objetivo",
        "scope": "escopo",
        "functional_requirements": ["requisito 1"],
        "success_criteria": ["criterio 1"],
    }
    base.update(overrides)
    return PRDDraft(**base)


def test_valid_prd_passes():
    assert validate_prd(_draft()) is True


def test_missing_objective_fails():
    assert validate_prd(_draft(objective="")) is False


def test_missing_scope_fails():
    assert validate_prd(_draft(scope="")) is False


def test_no_functional_requirements_fails():
    assert validate_prd(_draft(functional_requirements=[])) is False


def test_no_success_criteria_fails():
    assert validate_prd(_draft(success_criteria=[])) is False
