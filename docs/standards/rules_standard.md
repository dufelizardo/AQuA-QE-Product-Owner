# Padrão de Rules

> Estrutura padrão para as Rules (regras explícitas de comportamento) de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/rules.md`.

## Propósito

Rules são restrições **explícitas, verificáveis e de aplicação direta** que o agente deve obedecer — a camada mais rígida entre a AI Spec (comportamento esperado, descritivo) e a implementação (skills, prompt). Diferem de uma regra de negócio de domínio (`../../knowledge/templates/business_rule.md`), que é conhecimento sobre o domínio do cliente, não sobre o comportamento do próprio agente.

## Campos por regra

- **ID**: `<identificador único, ex.: RULE-001>`
- **Descrição**: `<enunciado da regra, em linguagem não ambígua>`
- **Gatilho/condição**: `<quando esta regra se aplica>`
- **Ação esperada**: `<o que o agente deve fazer quando a condição é atendida>`
- **Severidade/prioridade**: `<bloqueante | recomendação | aviso>`
- **Origem**: `<de qual objetivo, guardrail ou requisito do PRD esta regra deriva>`

## Tipos comuns de regras

- **Guardrails** — limites do que o agente nunca deve fazer (ex.: nunca inventar um requisito que não veio da fonte).
- **Regras de formatação** — como a saída deve ser estruturada (conectam com `../agent/output_schema.md`).
- **Regras de escalonamento** — quando o agente deve sinalizar incerteza em vez de decidir sozinho.
- **Regras de qualidade** — critérios mínimos que uma saída deve satisfazer antes de ser entregue (ex.: aplicar INVEST antes de finalizar uma User Story, ver `../../knowledge/methodology/invest.md`).

## Critérios de qualidade

- Cada regra deve seguir a mesma disciplina de um requisito bem escrito: singular, não ambígua, verificável (ver `../../knowledge/methodology/iso29148.md`).
- Regras não devem se sobrepor de forma conflitante; conflitos devem ser resolvidos explicitamente por prioridade.
- Toda regra deve ser testável por um caso de avaliação (ver `evaluation_standard.md`).
