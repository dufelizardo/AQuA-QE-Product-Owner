from aqua_qe_product_owner.models import AcceptanceCriteria, BusinessRule, StoryStatus, UserStory
from aqua_qe_product_owner.skills.export_markdown import export_markdown
from aqua_qe_product_owner.skills.parse_story_markdown import parse_story_markdown


def test_parse_story_markdown_reconstroi_campos_basicos():
    texto = (
        "# Consultar saldo\n\n"
        "**ID**: US-001\n"
        "**Status**: accepted\n"
        "**Prioridade**: Alta\n\n"
        "## Descrição\n\n"
        "Como cliente,\n"
        "Quero consultar meu saldo,\n"
        "Para que eu acompanhe minhas finanças.\n\n"
        "descrição livre adicional\n\n"
        "## Rastreabilidade\n\n> texto fonte\n"
    )

    story = parse_story_markdown(texto)

    assert story.id == "US-001"
    assert story.title == "Consultar saldo"
    assert story.actor == "cliente"
    assert story.goal == "consultar meu saldo"
    assert story.benefit == "eu acompanhe minhas finanças"
    assert story.description == "descrição livre adicional"
    assert story.priority == "Alta"
    assert story.source_reference == "texto fonte"
    # status/review_notes nunca são restaurados do arquivo (ver docstring)
    assert story.status == StoryStatus.PENDING_CLARIFICATION


def test_parse_story_markdown_reconstroi_regras_criterios_e_listas():
    texto = (
        "# t\n\n**ID**: US-001\n\n"
        "## Descrição\n\nComo a,\nQuero b,\nPara que c.\n\n"
        "## Regras de Negócio\n\n"
        "- **BR-001**: regra um\n"
        "- **BR-002**: regra dois\n\n"
        "## Critérios de Aceitação\n\n"
        "### Cenario um\n\n- Given g1\n- When w1\n- Then t1\n\n"
        "### Cenario dois\n\n- Given g2\n- When w2\n- Then t2\n\n"
        "## Suposições\n\n- suposicao 1\n\n"
        "## Dependências\n\n- dependencia 1\n\n"
        "## Rastreabilidade\n\n> fonte original\n"
    )

    story = parse_story_markdown(texto)

    assert [r.id for r in story.business_rules] == ["BR-001", "BR-002"]
    assert [r.description for r in story.business_rules] == ["regra um", "regra dois"]
    assert all(r.source_reference == "fonte original" for r in story.business_rules)
    assert [c.scenario for c in story.acceptance_criteria] == ["Cenario um", "Cenario dois"]
    assert story.acceptance_criteria[0].given == "g1"
    assert story.acceptance_criteria[1].then == "t2"
    assert story.assumptions == ["suposicao 1"]
    assert story.dependencies == ["dependencia 1"]


def test_round_trip_preserva_conteudo(tmp_path):
    original = UserStory(
        id="US-001",
        title="Consultar saldo",
        actor="cliente",
        goal="consultar meu saldo",
        benefit="acompanhar minhas financas",
        description="descricao livre",
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-999", scenario="Saldo ok", given="g", when="w", then="t")
        ],
        business_rules=[
            BusinessRule(id="BR-999", description="regra", source_reference="fonte original")
        ],
        assumptions=["suposicao 1"],
        dependencies=["dependencia 1"],
        source_reference="fonte original",
        priority="Alta",
    )
    caminho = tmp_path / "story.md"
    export_markdown(original, str(caminho))

    reconstruido = parse_story_markdown(caminho.read_text(encoding="utf-8"))

    assert reconstruido.id == original.id
    assert reconstruido.title == original.title
    assert reconstruido.actor == original.actor
    assert reconstruido.goal == original.goal
    assert reconstruido.benefit == original.benefit
    assert reconstruido.description == original.description
    assert reconstruido.priority == original.priority
    assert reconstruido.source_reference == original.source_reference
    assert [c.scenario for c in reconstruido.acceptance_criteria] == [
        c.scenario for c in original.acceptance_criteria
    ]
    assert [r.description for r in reconstruido.business_rules] == [
        r.description for r in original.business_rules
    ]
    assert reconstruido.assumptions == original.assumptions
    assert reconstruido.dependencies == original.dependencies
