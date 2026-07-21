from dataclasses import dataclass


@dataclass
class AcceptanceCriteria:
    """Critério de aceitação no formato Given-When-Then, conforme knowledge/templates/acceptance_criteria.md."""

    id: str
    scenario: str
    given: str
    when: str
    then: str
