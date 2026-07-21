from dataclasses import dataclass, field

from .status import StoryStatus


@dataclass
class PRDDraft:
    """PRD gerado a partir de uma ideia, seções conforme docs/standards/prd_standard.md."""

    context_problem: str = ""
    objective: str = ""
    target_audience: str = ""
    scope: str = ""
    out_of_scope: str = ""
    functional_requirements: list[str] = field(default_factory=list)
    non_functional_requirements: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    risks_assumptions: list[str] = field(default_factory=list)
    status: StoryStatus = StoryStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
