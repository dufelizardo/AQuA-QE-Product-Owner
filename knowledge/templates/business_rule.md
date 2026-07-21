# Template — Business Rule

> Estrutura padrão, sem conteúdo de domínio. Regras de negócio são restrições ou definições que existem independentemente de qualquer User Story específica, mas que podem afetar várias delas.

## Campos

- **ID**: `<identificador único, ex.: BR-001>`
- **Nome**: `<nome curto da regra>`
- **Descrição**: `<enunciado da regra, em linguagem clara e não ambígua>`
- **Tipo**: `<restrição | definição de termo | cálculo | fato de negócio — classificação livre conforme necessidade>`
- **Origem**: `<de onde a regra vem: legislação, política interna, decisão de stakeholder etc.>`
- **User Stories/Features afetadas**: `<lista de itens do backlog onde esta regra se aplica>`
- **Exceções**: `<casos em que a regra não se aplica, se houver>`

## Diferença em relação a um Critério de Aceitação

Uma regra de negócio é **transversal** — pode valer para múltiplas histórias e existir independentemente de qualquer uma delas. Um critério de aceitação é **local** a uma história específica e costuma *aplicar* uma ou mais regras de negócio ao contexto daquela história (ver `acceptance_criteria.md`).

## Checklist de qualidade

Seguir as mesmas características de um requisito individual bem escrito (ver `../methodology/iso29148.md`): necessária, não ambígua, completa, singular e verificável.
