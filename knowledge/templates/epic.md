# Template — Epic

> Estrutura padrão, sem conteúdo de domínio. Um Epic agrupa um conjunto de Features/User Stories relacionadas, grandes demais para caber em um único Sprint.

## Campos

- **ID**: `<identificador único, ex.: EPIC-001>`
- **Título**: `<nome do Epic>`
- **Objetivo**: `<problema ou oportunidade de negócio que o Epic endereça>`
- **Valor esperado**: `<benefício de negócio ao concluir o Epic>`
- **Stakeholders**: `<partes interessadas principais>`
- **Escopo**: `<o que está incluído>`
- **Fora do escopo**: `<o que explicitamente não está incluído>`
- **Features relacionadas**: `<lista de Features que compõem este Epic — ver template feature.md>`
- **Critérios de sucesso**: `<como medir que o Epic entregou o valor esperado>`
- **Restrições/Premissas**: `<restrições de prazo, tecnologia, regulação, dependências externas>`
- **Prioridade**: `<ordenação relativa a outros Epics>`

## Relação com a hierarquia de itens

```
Epic
 └── Feature
      └── User Story
           └── Task
```

Um Epic não é implementado diretamente — é fatiado em Features e, em seguida, em User Stories pequenas o suficiente para caber em um Sprint (ver `../methodology/invest.md`, critério "Small").
