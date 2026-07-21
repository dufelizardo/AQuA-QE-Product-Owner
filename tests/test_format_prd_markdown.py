from aqua_qe_product_owner.models import PRDDraft
from aqua_qe_product_owner.skills.format_prd_markdown import format_prd_markdown


def test_format_prd_markdown_includes_all_sections():
    draft = PRDDraft(
        context_problem="contexto do problema",
        objective="objetivo do produto",
        target_audience="publico alvo",
        scope="escopo",
        out_of_scope="fora de escopo",
        functional_requirements=["requisito funcional 1"],
        non_functional_requirements=["requisito nao funcional 1"],
        success_criteria=["criterio de sucesso 1"],
        risks_assumptions=["risco 1"],
    )

    texto = format_prd_markdown(draft)

    assert "## Contexto e problema" in texto
    assert "contexto do problema" in texto
    assert "## Objetivo do produto" in texto
    assert "objetivo do produto" in texto
    assert "## Público-alvo" in texto
    assert "## Escopo" in texto
    assert "## Fora de escopo" in texto
    assert "## Requisitos funcionais" in texto
    assert "requisito funcional 1" in texto
    assert "## Requisitos não funcionais" in texto
    assert "## Critérios de sucesso" in texto
    assert "## Riscos e premissas" in texto
    assert "risco 1" in texto


def test_format_prd_markdown_handles_empty_lists():
    draft = PRDDraft(context_problem="c", objective="o", scope="e")

    texto = format_prd_markdown(draft)

    assert "(nenhum)" in texto
