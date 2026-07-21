# Evaluation

> Estrutura conforme `../standards/evaluation_standard.md`. Decisão de produto: avaliação combina checklist automático, revisão por um segundo LLM e revisão humana obrigatória (nenhum substitui o outro).

## Métricas

- **Taxa de aprovação automática** — % de histórias geradas que passam no checklist (`validation_checklist.md`) sem interrupção por ambiguidade (RULE-004).
- **Taxa de aceitação sem retrabalho** — % de histórias em `draft_validated` aceitas pelo time/PO sem edição substancial na revisão humana (métrica de sucesso do PRD).
- **Cobertura de requisitos** — % dos requisitos extraídos (`extract_requirements`) que resultaram em uma User Story `draft_validated` (não ficaram em `pending_clarification` nem foram descartados).
- **Taxa de interrupção por ambiguidade** — % de itens que acionaram RULE-004; alto valor indica fontes de entrada de baixa qualidade ou identificação excessivamente conservadora.

## Casos de teste

- **Caminho feliz** — fonte clara (arquivo `.txt`/Markdown, chat ou Jira) com ator, objetivo e regra de negócio explícitos; deve gerar história `draft_validated` sem interrupção.
- **Fonte ambígua** — ator ou objetivo não identificável; deve acionar RULE-004 e explicar a lacuna, nunca gerar suposição (GR-1).
- **Regra de negócio implícita** — regra não declarada explicitamente mas inferível do texto; deve ser identificada e listada na história (GR-3).
- **Modo lote com itens mistos** — fonte com alguns requisitos claros e outros ambíguos; itens claros devem virar `draft_validated`, os demais devem aparecer em `unresolved_items` sem bloquear o restante.
- **Critério de aceitação vago gerado** — verificação de que `validate_story` reprova histórias sem Given-When-Then verificável (GR-2).

## Método de avaliação

1. **Checklist automático** (`validate_story`) — roda em toda execução, aplicando `validation_checklist.md`. Sem LLM.
2. **LLM-como-juiz** (`review_story`) — roda após o checklist automático aprovar; usa um modelo diferente do gerador (`OLLAMA_REVIEW_MODEL`, padrão `phi4`, enquanto `generate_story` usa `mistral`) para evitar self-preference bias. Reprova histórias com critérios de aceitação incompletos, benefício não mensurável, ou lacunas de segurança/erro não cobertas; os problemas apontados ficam em `UserStory.review_notes`.
3. **Revisão humana obrigatória** — toda história `draft_validated` passa por aprovação humana antes de entrar de fato no Product Backlog; feedback da revisão (aceite direto vs. retrabalho) alimenta a métrica de taxa de aceitação.

## Frequência

- Casos de teste automatizados rodam a cada mudança em prompt, regras ou skills que possam afetar comportamento (ver `prompt.md`, `rules.md`).
- Métricas de aceitação humana são agregadas continuamente a partir do uso real do agente.

## Critério de aprovação de uma nova versão do agente

Uma nova versão do prompt/regras/skills só substitui a anterior se não piorar a taxa de aceitação sem retrabalho nem a taxa de aprovação automática nos casos de teste de regressão.

## Registro de regressões

Toda falha encontrada em produção (ex.: história aprovada automaticamente que não deveria, regra de negócio omitida) vira um novo caso de teste permanente nesta lista.
