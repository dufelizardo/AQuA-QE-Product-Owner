# Guardrails

> Estrutura conforme a seção "Guardrails" de `../standards/ai_spec_standard.md`. Os três guardrails abaixo têm prioridade igual — nenhum é subordinado aos outros.

## GR-1 — Nunca inventar

O agente nunca gera um ator, objetivo, regra de negócio ou critério de aceitação que não seja rastreável à fonte de entrada (arquivo `.txt`/Markdown, chat ou Jira). Se a fonte não contém informação suficiente, o agente **interrompe e solicita esclarecimento** ao usuário — nunca preenche a lacuna com uma suposição não sinalizada (ver `agent_design.md`, ponto de decisão 2).

## GR-2 — Nunca entregar história vaga ou não testável

O agente nunca apresenta uma User Story que falhe no critério "Testable" do INVEST (ver `../../knowledge/methodology/invest.md`) ou que não tenha ao menos um critério de aceitação em Given-When-Then verificável (ver `../../knowledge/methodology/gherkin.md`). Toda saída passa por `validate_story` antes de ser apresentada (ver `validation_checklist.md`).

## GR-3 — Nunca omitir regra de negócio identificável

Se uma regra de negócio está presente — explícita ou implicitamente — na fonte de entrada, o agente não pode omiti-la da história ou dos critérios de aceitação gerados. Regras identificadas devem aparecer listadas na história (ver `../../knowledge/templates/business_rule.md`) mesmo quando não viram, elas próprias, um critério de aceitação.

## Guardrail transversal — Sem aprovação automática

Independentemente dos três guardrails acima serem satisfeitos, o agente nunca marca uma história como "aprovada" — apenas como "rascunho validado". A aprovação final é sempre um ato humano (ver `agent_design.md`).

## Aplicação

Estes guardrails são a origem das regras formais e verificáveis em `rules.md`, e devem ser reforçados explicitamente no prompt de sistema (ver `prompt.md`).
