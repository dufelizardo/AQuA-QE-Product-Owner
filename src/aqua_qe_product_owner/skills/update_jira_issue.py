from ..models import UserStory
from ..services.jira_service import update_issue_description


def story_para_texto(story: UserStory) -> str:
    """Formata uma User Story como texto simples, reutilizado por skills que escrevem no Jira."""
    linhas = [
        story.title or story.id,
        "",
        f"Como {story.actor}, quero {story.goal}, para que {story.benefit}.",
        "",
        story.description,
    ]
    if story.business_rules:
        linhas += ["", "Regras de Negócio:"]
        linhas += [f"- {regra.description}" for regra in story.business_rules]
    if story.acceptance_criteria:
        linhas += ["", "Critérios de Aceitação:"]
        for criterio in story.acceptance_criteria:
            linhas.append(
                f"- {criterio.scenario}: Dado {criterio.given}, "
                f"Quando {criterio.when}, Então {criterio.then}"
            )
    return "\n".join(linhas)


def update_jira_issue(issue_key: str, story: UserStory) -> None:
    """Persiste a versão final de uma User Story de volta na descrição do ticket Jira."""
    update_issue_description(issue_key, story_para_texto(story))
