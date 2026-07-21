# Gherkin

> Linguagem de especificação criada junto com o Cucumber; hoje suportada também por Behave (Python), SpecFlow (.NET) e outras ferramentas de BDD.

## O que é

Uma linguagem de domínio específico (DSL), legível por humanos de negócio, usada para descrever o comportamento de um sistema de forma estruturada o suficiente para ser interpretada por ferramentas de automação (parsers). É a materialização textual dos exemplos discutidos em BDD (ver [[bdd]]).

## Estrutura de um arquivo `.feature`

```gherkin
# Comentários começam com #
Feature: <nome da funcionalidade>
  <descrição livre opcional, geralmente no formato "Como... quero... para que...">

  Background:
    Given <passo comum a todos os cenários deste Feature>

  Scenario: <nome do cenário>
    Given <contexto inicial>
    When <ação/evento>
    Then <resultado esperado>
    And <resultado adicional>
    But <resultado negativo esperado>

  Scenario Outline: <nome do cenário parametrizado>
    Given um valor "<entrada>"
    When o valor é processado
    Then o resultado é "<saida>"

    Examples:
      | entrada | saida |
      | 1       | um    |
      | 2       | dois  |
```

## Palavras-chave principais

- **Feature** — agrupa um conjunto de cenários relacionados a uma funcionalidade.
- **Scenario** — um exemplo concreto e único de comportamento.
- **Scenario Outline** + **Examples** — um cenário parametrizado, executado uma vez para cada linha da tabela de exemplos.
- **Given / When / Then** — os três passos centrais do BDD (contexto, ação, resultado).
- **And / But** — continuam o passo anterior (Given, When ou Then), evitando repetição da palavra-chave.
- **Background** — passos executados antes de cada Scenario do Feature, para eliminar repetição de contexto comum.
- **Tags** (`@tag`) — marcam Features ou Scenarios para categorização e execução seletiva (ex.: `@smoke`, `@regressao`).

## Boas práticas

- Um cenário deve descrever **um único comportamento observável**, não um fluxo inteiro de ponta a ponta.
- Passos devem ser escritos do ponto de vista do **comportamento do sistema**, não da implementação técnica (evitar detalhes de UI como "clica no botão de id `#submit`").
- A linguagem deve ser a mesma usada pelo negócio (linguagem ubíqua), permitindo que um Product Owner leia e valide o cenário sem apoio técnico.

## Relevância para este agente

Gherkin é o formato-alvo da skill de geração de critérios de aceitação: cada critério de aceitação de uma User Story deve poder ser expresso como um ou mais `Scenario` no formato Given-When-Then, tornando-o testável (ver [[invest]]) e verificável (ver [[iso29148]]).
