from ..models import PRDDraft


def _lista_md(itens: list[str]) -> str:
    return "\n".join(f"- {item}" for item in itens) if itens else "(nenhum)"


def format_prd_markdown(draft: PRDDraft) -> str:
    """Formata o PRD em Markdown, seções conforme docs/standards/prd_standard.md.

    Usado tanto para exportação local quanto como corpo da página do
    Confluence — o texto resultante pode alimentar extract_requirements/
    extract_prd_context/generate_epic_shape normalmente, como qualquer outra
    fonte de entrada.
    """
    return (
        "# PRD\n\n"
        f"## Contexto e problema\n{draft.context_problem}\n\n"
        f"## Objetivo do produto\n{draft.objective}\n\n"
        f"## Público-alvo\n{draft.target_audience}\n\n"
        f"## Escopo\n{draft.scope}\n\n"
        f"## Fora de escopo\n{draft.out_of_scope}\n\n"
        f"## Requisitos funcionais\n{_lista_md(draft.functional_requirements)}\n\n"
        f"## Requisitos não funcionais\n{_lista_md(draft.non_functional_requirements)}\n\n"
        f"## Critérios de sucesso\n{_lista_md(draft.success_criteria)}\n\n"
        f"## Riscos e premissas\n{_lista_md(draft.risks_assumptions)}\n"
    )
