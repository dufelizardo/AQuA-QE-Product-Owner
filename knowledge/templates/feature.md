# Template — Feature

> Estrutura padrão, sem conteúdo de domínio. Uma Feature é um subconjunto coeso de um Epic, agrupando User Stories relacionadas.

## Campos

- **ID**: `<identificador único, ex.: FEAT-001>`
- **Título**: `<nome da Feature>`
- **Epic relacionado**: `<referência ao Epic pai — ver template epic.md>`
- **Descrição**: `<o que a Feature entrega, em linguagem de negócio>`
- **Ator(es) envolvido(s)**: `<persona(s) que interagem com esta Feature>`
- **User Stories relacionadas**: `<lista de histórias que compõem esta Feature — ver template user_story.md>`
- **Regras de negócio aplicáveis**: `<lista ou referência — ver template business_rule.md>`
- **Critérios de aceitação de alto nível**: `<condições gerais que validam a Feature como um todo>`
- **Dependências**: `<outras Features, sistemas ou integrações necessárias>`
- **Prioridade**: `<ordenação relativa dentro do Epic>`

## Observação

Uma Feature descreve *o que* será entregue do ponto de vista funcional; o comportamento detalhado e testável de cada parte fica nas User Stories e em seus critérios de aceitação (ver `../methodology/bdd.md` e `../methodology/gherkin.md`).
