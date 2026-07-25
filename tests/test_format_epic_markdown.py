from aqua_qe_product_owner.models import AcceptanceCriteria, Epic, Requirement
from aqua_qe_product_owner.skills.format_epic_markdown import format_epic_markdown


def test_format_epic_markdown_inclui_todos_os_campos():
    epic = Epic(
        id="EPIC-001",
        title="Consulta de saldo",
        objective="Permitir consulta de saldo",
        scope="App mobile",
        value="Reduz atendimento em agencia",
        requirements=[
            Requirement(id="REQ-001", text="Consultar saldo", source_reference="trecho 1")
        ],
        acceptance_criteria=[
            AcceptanceCriteria(id="AC-001", scenario="Saldo ok", given="g", when="w", then="t")
        ],
    )

    resultado = format_epic_markdown(epic)

    assert "# Consulta de saldo" in resultado
    assert "**ID**: EPIC-001" in resultado
    assert "## Objetivo\nPermitir consulta de saldo" in resultado
    assert "## Escopo\nApp mobile" in resultado
    assert "## Valor\nReduz atendimento em agencia" in resultado
    assert "- Consultar saldo" in resultado
    assert "> trecho 1" in resultado
    assert "### Saldo ok" in resultado
    assert "- Given g" in resultado
    assert "- When w" in resultado
    assert "- Then t" in resultado


def test_format_epic_markdown_sem_requisitos_nem_criterios():
    epic = Epic(id="EPIC-002", title="t", objective="o", scope="e", value="v")

    resultado = format_epic_markdown(epic)

    assert "(nenhum)" in resultado
