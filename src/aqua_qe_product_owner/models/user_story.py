from dataclasses import dataclass, field

from .acceptance_criteria import AcceptanceCriteria
from .business_rule import BusinessRule
from .status import StoryStatus


@dataclass
class UserStory:
    """User Story estruturada, conforme docs/agent/output_schema.md."""

    id: str
    title: str
    actor: str
    goal: str
    benefit: str
    description: str
    acceptance_criteria: list[AcceptanceCriteria] = field(default_factory=list)
    business_rules: list[BusinessRule] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    source_reference: str = ""
    status: StoryStatus = StoryStatus.PENDING_CLARIFICATION
    priority: str | None = None
    estimate: str | None = None
    dependencies: list[str] = field(default_factory=list)
    review_notes: list[str] = field(default_factory=list)
