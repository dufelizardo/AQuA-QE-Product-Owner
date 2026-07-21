# Acceptance Patterns

> Padrões estruturais que distinguem uma saída aceitável de uma inaceitável, conforme `validation_checklist.md` e `guardrails.md`. Exemplos concretos de domínio (few-shot) ficam em `../../knowledge/examples/`, ainda não populados.

## Padrão aceitável

Uma User Story é aceitável quando:

- Todo campo (`actor`, `goal`, `business_rules`) tem `source_reference` rastreável à entrada (GR-1).
- Passa em todos os itens do checklist INVEST (`validation_checklist.md`).
- Tem pelo menos um critério de aceitação em Given-When-Then, singular e verificável.
- Regras de negócio identificadas na fonte aparecem listadas, mesmo que não virem critério de aceitação isolado (GR-3).
- O campo `status` reflete corretamente o resultado da validação (`draft_validated` ou `pending_clarification`).

## Padrão inaceitável

Uma saída é inaceitável quando apresenta qualquer um dos sinais abaixo:

- **Ator ou objetivo genérico demais** para ser rastreado a uma frase específica da fonte (sintoma de invenção — viola GR-1).
- **Critério de aceitação vago**, sem condição observável clara (ex.: "o sistema deve funcionar corretamente" em vez de um Given-When-Then concreto — viola GR-2).
- **Regra de negócio da fonte ausente** na história gerada, mesmo estando implícita no texto original (viola GR-3).
- **História marcada como aprovada** pelo próprio agente, sem passar por revisão humana (viola RULE-005).
- **Geração silenciosa diante de ambiguidade** — quando faltava informação e o agente gerou uma suposição em vez de acionar RULE-004.

## Como usar este documento

Ao avaliar (`evaluation.md`) ou revisar manualmente uma saída do agente, comparar contra os dois padrões acima antes de aceitar a história como rascunho válido para o Product Backlog.
