from ..services.jira_service import get_issue_text


def read_jira_issue(issue_key: str) -> str:
    """Busca um ticket do Jira Cloud (resumo + descrição) e retorna como texto simples."""
    return get_issue_text(issue_key)
