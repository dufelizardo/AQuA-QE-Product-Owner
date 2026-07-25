from aqua_qe_product_owner.models import AcceptanceCriteria, Epic, Requirement
from aqua_qe_product_owner.skills.format_epic_markdown import format_epic_markdown
from aqua_qe_product_owner.skills.parse_epic_markdown import parse_epic_markdown


def test_parse_epic_markdown_reconstroi_campos_escalares():
    texto = (
        "# Consulta de saldo\n\n"
        "**ID**: EPIC-001\n\n"
        "## Objetivo\nPermitir consulta de saldo\n\n"
        "## Escopo\nApp mobile\n\n"
        "## Valor\nReduz atendimento em agencia\n\n"
        "## Requisitos\n(nenhum)\n\n"
        "## Critérios de Aceitação\n\n(nenhum)\n"
    )

    epic = parse_epic_markdown(texto)

    assert epic.id == "EPIC-001"
    assert epic.title == "Consulta de saldo"
    assert epic.objective == "Permitir consulta de saldo"
    assert epic.scope == "App mobile"
    assert epic.value == "Reduz atendimento em agencia"
    assert epic.requirements == []
    assert epic.acceptance_criteria == []


def test_parse_epic_markdown_reconstroi_requisitos_e_criterios():
    texto = (
        "# t\n\n**ID**: EPIC-001\n\n"
        "## Objetivo\no\n\n## Escopo\ne\n\n## Valor\nv\n\n"
        "## Requisitos\n- Consultar saldo\n  > trecho 1\n- Solicitar cartao\n  > trecho 2\n\n"
        "## Critérios de Aceitação\n\n"
        "### Saldo ok\n\n- Given g1\n- When w1\n- Then t1\n\n"
        "### Cartao solicitado\n\n- Given g2\n- When w2\n- Then t2\n"
    )

    epic = parse_epic_markdown(texto)

    assert [r.text for r in epic.requirements] == ["Consultar saldo", "Solicitar cartao"]
    assert [r.source_reference for r in epic.requirements] == ["trecho 1", "trecho 2"]
    assert [r.id for r in epic.requirements] == ["REQ-001", "REQ-002"]
    assert [c.scenario for c in epic.acceptance_criteria] == ["Saldo ok", "Cartao solicitado"]
    assert epic.acceptance_criteria[0].given == "g1"
    assert epic.acceptance_criteria[1].then == "t2"
    assert [c.id for c in epic.acceptance_criteria] == ["AC-001", "AC-002"]


def test_round_trip_preserva_conteudo():
    original = Epic(
        id="EPIC-001",
        title="Consulta de saldo",
        objective="Permitir consulta de saldo",
        scope="App mobile",
        value="Reduz atendimento em agencia",
        requirements=[
            Requirement(id="REQ-999", text="Consultar saldo", source_reference="trecho 1"),
            Requirement(id="REQ-998", text="Solicitar cartao", source_reference="trecho 2"),
        ],
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-999", scenario="Saldo ok", given="g1", when="w1", then="t1"),
        ],
    )

    reconstruido = parse_epic_markdown(format_epic_markdown(original))

    assert reconstruido.id == original.id
    assert reconstruido.title == original.title
    assert reconstruido.objective == original.objective
    assert reconstruido.scope == original.scope
    assert reconstruido.value == original.value
    assert [r.text for r in reconstruido.requirements] == [r.text for r in original.requirements]
    assert [r.source_reference for r in reconstruido.requirements] == [
        r.source_reference for r in original.requirements
    ]
    assert [c.scenario for c in reconstruido.acceptance_criteria] == [
        c.scenario for c in original.acceptance_criteria
    ]
    assert [c.given for c in reconstruido.acceptance_criteria] == [
        c.given for c in original.acceptance_criteria
    ]
