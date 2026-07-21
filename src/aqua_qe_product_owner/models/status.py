from enum import Enum


class StoryStatus(str, Enum):
    """Estados possíveis de uma User Story, conforme docs/agent/output_schema.md."""

    DRAFT_VALIDATED = "draft_validated"
    PENDING_CLARIFICATION = "pending_clarification"
    ACCEPTED = "accepted"
