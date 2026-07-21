import os

from ..models import Epic
from ..services.jira_service import create_issue


def epic_para_texto(epic: Epic) -> str:
    """Formata um Épico como texto simples para a descrição do ticket Jira."""
    linhas = [
        f"Objetivo: {epic.objective}",
        "",
        f"Escopo: {epic.scope}",
        "",
        f"Valor: {epic.value}",
    ]
    if epic.acceptance_criteria:
        linhas += ["", "Critérios de Aceitação:"]
        for criterio in epic.acceptance_criteria:
            linhas.append(
                f"- {criterio.scenario}: Dado {criterio.given}, "
                f"Quando {criterio.when}, Então {criterio.then}"
            )
    return "\n".join(linhas)


def create_jira_epic(epic: Epic) -> str:
    """Cria o Épico no Jira Cloud e retorna a chave do ticket criado."""
    project_key = os.environ["JIRA_PROJECT_KEY"]
    issue_type_id = os.environ["JIRA_EPIC_ISSUE_TYPE_ID"]
    return create_issue(project_key, issue_type_id, epic.title or epic.id, epic_para_texto(epic))
