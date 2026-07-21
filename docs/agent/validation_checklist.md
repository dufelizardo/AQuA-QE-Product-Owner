# Validation Checklist

> Checklist aplicado pela skill `validate_story` antes de qualquer User Story ser marcada como `draft_validated` (ver `output_schema.md` e RULE-002/RULE-005 em `rules.md`).

## 1. Rastreabilidade (GR-1)

- [ ] Ator, objetivo e regras de negócio têm origem identificável na fonte de entrada (`source_reference` preenchido).
- [ ] Nenhum campo foi preenchido por suposição não sinalizada.

## 2. INVEST (`../../knowledge/methodology/invest.md`)

- [ ] **Independent** — a história não depende obrigatoriamente de outra história não concluída.
- [ ] **Negotiable** — a descrição é uma narrativa aberta, não uma especificação técnica fechada.
- [ ] **Valuable** — o benefício ("para que") está claro e é atribuível a um stakeholder.
- [ ] **Estimable** — há informação suficiente para o time estimar o esforço.
- [ ] **Small** — a história é pequena o suficiente para caber em um Sprint (não descreve um Epic inteiro).
- [ ] **Testable** — existe ao menos um critério de aceitação em Given-When-Then verificável.

## 3. Critérios de aceitação (`../../knowledge/methodology/iso29148.md`, `.../gherkin.md`)

- [ ] Cada critério é não ambíguo e singular (testa uma única condição).
- [ ] Cada critério está escrito no formato Given-When-Then.
- [ ] Nenhum critério descreve implementação técnica em vez de comportamento observável.

## 4. Regras de negócio (GR-3)

- [ ] Todas as regras de negócio identificadas em `identify_business_rules` estão listadas na história.

## 5. Formato

- [ ] A estrutura da saída segue `../../knowledge/templates/user_story.md` e `.../acceptance_criteria.md`.

## Resultado

- **Todos os itens satisfeitos** → status `draft_validated` (ver `output_schema.md`).
- **Algum item de rastreabilidade ou testabilidade falha** → acionar RULE-004 (`rules.md`): interromper e solicitar esclarecimento, status `pending_clarification`.
- **Falha apenas em item de formato** → corrigir automaticamente antes de exportar (RULE-006), sem necessidade de interromper o fluxo.
