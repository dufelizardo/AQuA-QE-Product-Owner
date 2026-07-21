# Prompt

> Estrutura conforme `../standards/prompt_standard.md`. Este documento descreve a composição do prompt de sistema; o texto literal enviado ao LLM é implementação e deve apenas referenciar, não duplicar, o conteúdo dos documentos abaixo.

## Composição do prompt de sistema

1. **Papel/persona** — derivado integralmente de `persona.md` (colaborativo, didático, formal, consultivo).
2. **Objetivo da tarefa** — derivado de `objectives.md`, adaptado ao modo de operação (unitário ou lote — ver `agent_design.md`).
3. **Instruções de comportamento** — derivadas de `ai_spec.md` (comportamento em caminho feliz, fonte ambígua e fora de escopo).
4. **Regras/guardrails reforçados** — RULE-001 a RULE-006 (`rules.md`) e os guardrails GR-1/GR-2/GR-3 (`guardrails.md`) devem aparecer de forma explícita e não negociável no prompt, não apenas implícita no tom.
5. **Formato de saída** — schema de `output_schema.md`, incluindo os valores válidos de `status`.
6. **Exemplos (few-shot)** — extraídos de `../../knowledge/examples/` quando populados; ausência de exemplos não deve degradar o comportamento esperado, apenas reduzir a calibração fina de estilo.

## Convenções de versionamento

- Cada versão do prompt é identificada (ex.: comentário de versão no topo do texto de sistema), permitindo associar uma versão a um conjunto de resultados de `evaluation.md`.
- Mudanças que alterem comportamento observável (não apenas fraseado) exigem rodar os casos de teste de `evaluation.md` antes de substituir a versão em uso (critério de aprovação descrito lá).

## O que o prompt não deve conter

- Não deve conter conhecimento de domínio específico de cliente diretamente embutido — esse conhecimento entra via Context Engineering (`context_engineering.md`), não hardcoded no prompt.
- Não deve reafirmar informações já garantidas estruturalmente pelo schema de saída (evitar redundância que consome orçamento de tokens).
