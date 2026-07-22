from ..models import Epic
from ..services.jira_service import update_issue_description
from .create_jira_epic import epic_para_texto


def update_jira_epic(issue_key: str, epic: Epic) -> None:
    """Persiste a versão final (aceita pelo usuário) de um Épico de volta na descrição do ticket Jira de origem."""
    update_issue_description(issue_key, epic_para_texto(epic))
