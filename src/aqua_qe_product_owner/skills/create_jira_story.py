import os

from ..models import UserStory
from ..services.jira_service import create_issue
from .update_jira_issue import story_para_texto


def create_jira_story(story: UserStory, epic_key: str) -> str:
    """Cria a User Story como ticket filho do Épico no Jira Cloud e retorna a chave gerada."""
    project_key = os.environ["JIRA_PROJECT_KEY"]
    issue_type_id = os.environ["JIRA_STORY_ISSUE_TYPE_ID"]
    return create_issue(
        project_key,
        issue_type_id,
        story.title or story.id,
        story_para_texto(story),
        parent_key=epic_key,
    )
