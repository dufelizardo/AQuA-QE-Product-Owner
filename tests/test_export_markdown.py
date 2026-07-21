from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, StoryStatus, UserStory
from aqua_qe_product_owner.skills.export_markdown import export_markdown


def test_export_markdown_writes_expected_sections(tmp_path):
    story = UserStory(
        id="US-001",
        title="Titulo",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="descricao",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="cenario", given="g", when="w", then="t")
        ],
        business_rules=[BusinessRule(id="BR-001", description="regra", source_reference="fonte")],
        review_notes=["ponto de atenção"],
        source_reference="texto fonte",
        status=StoryStatus.DRAFT_VALIDATED,
    )
    caminho = tmp_path / "story.md"

    export_markdown(story, str(caminho))

    conteudo = caminho.read_text(encoding="utf-8")
    assert "# Titulo" in conteudo
    assert "**Status**: draft_validated" in conteudo
    assert "## Regras de Negócio" in conteudo
    assert "BR-001" in conteudo
    assert "## Critérios de Aceitação" in conteudo
    assert "Given g" in conteudo
    assert "## Observações da Revisão" in conteudo
    assert "> texto fonte" in conteudo


def test_export_markdown_omits_empty_sections(tmp_path):
    story = UserStory(
        id="US-002",
        title="Sem extras",
        actor="ator",
        goal="objetivo",
        benefit="beneficio",
        description="",
        source_reference="fonte",
    )
    caminho = tmp_path / "story.md"

    export_markdown(story, str(caminho))

    conteudo = caminho.read_text(encoding="utf-8")
    assert "## Regras de Negócio" not in conteudo
    assert "## Critérios de Aceitação" not in conteudo
    assert "## Observações da Revisão" not in conteudo
