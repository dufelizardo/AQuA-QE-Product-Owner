from dataclasses import dataclass, field

from .acceptance_criteria import AcceptanceCriteria
from .requirement import Requirement
from .status import StoryStatus
from .user_story import UserStory


@dataclass
class UnresolvedItem:
    """Item da fonte que não pôde virar User Story em modo lote (ver RULE-004)."""

    source_reference: str
    reason: str


@dataclass
class Epic:
    """Epic gerado em modo lote, conforme docs/agent/output_schema.md."""

    id: str
    title: str
    objective: str
    scope: str = ""
    value: str = ""
    acceptance_criteria: list[AcceptanceCriteria] = field(default_factory=list)
    stories: list[UserStory] = field(default_factory=list)
    unresolved_items: list[UnresolvedItem] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)
    status: StoryStatus = StoryStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
