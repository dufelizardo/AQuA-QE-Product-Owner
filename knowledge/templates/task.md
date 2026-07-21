# Template — Task

> Estrutura padrão, sem conteúdo de domínio. Uma Task é a menor unidade de trabalho técnico necessária para implementar uma User Story.

## Campos

- **ID**: `<identificador único, ex.: TASK-001>`
- **Título**: `<descrição curta e técnica da atividade>`
- **User Story relacionada**: `<referência à história — ver template user_story.md>`
- **Descrição**: `<detalhamento técnico do que precisa ser feito>`
- **Tipo**: `<desenvolvimento | teste | design | infraestrutura | documentação>`
- **Responsável**: `<papel ou pessoa, quando aplicável>`
- **Estimativa**: `<horas ou pontos, conforme convenção do time>`
- **Dependências**: `<outras Tasks das quais esta depende>`
- **Critério de conclusão**: `<condição objetiva que indica que a Task está terminada>`

## Observação

Diferente da User Story (que descreve valor do ponto de vista do usuário), a Task descreve trabalho do ponto de vista técnico/interno do time e não precisa, por si só, ser INVEST-compliant. O conjunto de Tasks de uma User Story deve, ao final, satisfazer a Definition of Done (ver `../methodology/dod.md`).
