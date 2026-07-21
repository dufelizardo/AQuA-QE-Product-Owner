# Output Schema

> Estrutura de dados retornada por `generate_story` e exportada por `export_markdown`, alinhada a `../../knowledge/templates/user_story.md`. Implementada como dataclasses reais em `../../src/aqua_qe_product_owner/models/` (`UserStory`, `AcceptanceCriteria`, `BusinessRule`, `Epic`, `UnresolvedItem`) — o JSON abaixo é a representação conceitual; `business_rules` na implementação é `list[BusinessRule]` (objetos com `id`/`description`/`source_reference`), não strings soltas.

## Schema de uma User Story (modo unitário)

```
{
  "id": "<string, ex.: US-001>",
  "title": "<string>",
  "actor": "<string>",
  "goal": "<string>",
  "benefit": "<string>",
  "description": "<string — narrativa Como/Quero/Para que>",
  "acceptance_criteria": [
    {
      "id": "<string, ex.: AC-001>",
      "scenario": "<string — nome do cenário>",
      "given": "<string>",
      "when": "<string>",
      "then": "<string>"
    }
  ],
  "business_rules": ["<referência ou texto da regra — ver business_rule.md>"],
  "assumptions": ["<suposição sinalizada, se houver — deveria estar vazio quando RULE-004 é seguida>"],
  "source_reference": "<trecho ou localização na fonte de entrada, para rastreabilidade — GR-1>",
  "status": "draft_validated | pending_clarification | accepted",
  "priority": "<opcional>",
  "estimate": "<opcional>",
  "dependencies": ["<opcional>"],
  "review_notes": ["<apontamento do revisor (review_story), se houver>"]
}
```

## Schema de saída em modo lote (Epic)

```
{
  "epic": {
    "id": "<string, ex.: EPIC-001>",
    "title": "<string — gerado por generate_epic_metadata>",
    "objective": "<string — gerado por generate_epic_metadata>",
    "scope": "<string — gerado por generate_epic_metadata>",
    "value": "<string — valor de negócio, gerado por generate_epic_metadata>",
    "acceptance_criteria": ["<mesma estrutura Given-When-Then da User Story, em nível de Épico>"],
    "requirements": ["<Requirement extraído da fonte que originou o Épico — ver extract_requirements>"],
    "status": "draft_validated | pending_clarification | accepted",
    "review_notes": ["<apontamento do revisor (review_epic), se houver>"]
  },
  "stories": ["<lista de objetos User Story, schema acima>"],
  "unresolved_items": [
    {
      "source_reference": "<trecho da fonte>",
      "reason": "<motivo pelo qual não foi possível gerar uma história — ver RULE-004>"
    }
  ]
}
```

O Epic passa pelo mesmo ciclo `validate_epic` + `review_epic` (`workflow/generate_epic.py:finalize_epic`) que a User Story passa em `validate_story`/`review_story` — mesmos valores de `status` descritos abaixo, aplicados ao Épico como um todo. Antes do refinamento por story, o CLI roda `validate_traceability(epic)` (ver `skills.md`), verificando duplicidade entre stories, stories sem valor de negócio e requisitos órfãos.

Ao aceitar o Épico (CLI, `run.py --criar-jira`), `create_jira_epic` cria o ticket no Jira e `create_jira_story` cria cada `UserStory` do Epic como ticket filho (`parent`), retornando as chaves criadas.

## Valores válidos de `status`

- **`draft_validated`** — passou no checklist automático (`validation_checklist.md`) e na revisão por LLM (`review_story`); ainda não tem aceitação humana (ver RULE-005 em `rules.md`).
- **`pending_clarification`** — o agente interrompeu a geração por ambiguidade/incompletude na fonte (RULE-004), ou `review_story` reprovou a história; use `generate_clarifying_questions` + `refine_story` (ver `skills.md`) para endereçar os apontamentos.
- **`accepted`** — setado **apenas** pelo CLI (`run.py`), nunca pela lógica automática do agente, após confirmação explícita do usuário. Dispara `diff_story_versions` (comparação com a versão original) e, opcionalmente, `update_jira_issue`.

## Formato de exportação (`export_markdown`)

A saída em Markdown segue diretamente a estrutura de `../../knowledge/templates/user_story.md` (campos narrativos) e `../../knowledge/templates/acceptance_criteria.md` (blocos Gherkin), preenchidos a partir deste schema.
