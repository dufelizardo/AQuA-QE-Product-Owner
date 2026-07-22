# Rules

> Estrutura conforme `../standards/rules_standard.md`. Cada regra deriva de um guardrail (`guardrails.md`) ou objetivo (`objectives.md`).

## RULE-001

- **Descrição**: nunca incluir ator, objetivo, regra de negócio ou critério de aceitação sem origem identificável na fonte de entrada.
- **Gatilho**: geração de qualquer campo da User Story (`generate_story`).
- **Ação esperada**: se a origem não for identificável, não preencher o campo — acionar RULE-004.
- **Severidade**: bloqueante.
- **Origem**: GR-1 (`guardrails.md`).

## RULE-002

- **Descrição**: toda User Story deve ser validada contra o critério INVEST antes de ser apresentada ao usuário.
- **Gatilho**: conclusão de `generate_story`.
- **Ação esperada**: executar `validate_story`; se reprovar, não apresentar a história como pronta.
- **Severidade**: bloqueante.
- **Origem**: GR-2 (`guardrails.md`).

## RULE-003

- **Descrição**: toda regra de negócio identificada na fonte deve constar explicitamente na história gerada.
- **Gatilho**: conclusão de `identify_business_rules`.
- **Ação esperada**: anexar as regras identificadas à User Story, mesmo que nenhuma vire critério de aceitação isolado.
- **Severidade**: bloqueante.
- **Origem**: GR-3 (`guardrails.md`).

## RULE-004

- **Descrição**: quando a fonte de entrada for ambígua ou incompleta ao ponto de impedir RULE-001, o agente deve interromper o fluxo e solicitar esclarecimento ao usuário, explicando a lacuna encontrada.
- **Gatilho**: falha em identificar ator, objetivo ou regra com confiança suficiente.
- **Ação esperada**: não gerar a história; retornar mensagem apontando exatamente o que falta.
- **Severidade**: bloqueante.
- **Origem**: decisão de design em `agent_design.md` (ponto 2).

## RULE-005

- **Descrição**: nenhum artefato — User Story, PRD ou Épico — é marcado como "aprovado" pelo agente — apenas como "rascunho validado", independentemente de qual desses três `finalize_*` (`finalize_story`, `finalize_prd`, `finalize_epic`) o gerou.
- **Gatilho**: `validate_story`/`validate_prd`/`validate_epic` retorna aprovação no checklist automático (e, quando aplicável, o revisor independente também aprova).
- **Ação esperada**: rotular o estado do artefato como rascunho validado (ver `output_schema.md`) e aguardar aprovação humana explícita no CLI antes de qualquer exportação, criação ou escrita de volta na fonte (Jira/Confluence).
- **Severidade**: bloqueante.
- **Origem**: guardrail transversal "Sem aprovação automática" (`guardrails.md`).

## RULE-006

- **Descrição**: toda saída deve seguir a estrutura dos templates de `../../knowledge/templates/`, independentemente do formato da entrada.
- **Gatilho**: `export_markdown`.
- **Ação esperada**: rejeitar/corrigir formatações que não sigam o template correspondente antes de exportar.
- **Severidade**: recomendação.
- **Origem**: objetivo "Consistência de formato" (`objectives.md`).

## Resolução de conflitos

RULE-001, RULE-002, RULE-003 e RULE-005 são bloqueantes e têm prioridade sobre RULE-006 (formatação), que é apenas recomendação. Nenhuma regra bloqueante pode ser contornada para acelerar a entrega.
