# BDD

> Behavior-Driven Development, criado por Dan North (a partir de 2003) como evolução do Test-Driven Development (TDD).

## O que é

Uma abordagem de desenvolvimento ágil que estimula a colaboração entre desenvolvedores, QAs e stakeholders de negócio (Product Owner) para descrever o comportamento esperado do sistema em **linguagem natural estruturada**, compreensível por todos os envolvidos — não apenas por quem programa.

## Ideia central

Em vez de começar pela pergunta "como testo isso?" (TDD clássico), o BDD começa pela pergunta **"qual é o comportamento esperado, do ponto de vista de quem usa o sistema?"**. As especificações de comportamento, uma vez escritas, servem simultaneamente como:

1. Documentação legível por humanos.
2. Critério de aceitação compartilhado entre negócio e time técnico.
3. Especificação executável (quando conectada a uma ferramenta de automação, como Cucumber, Behave ou SpecFlow).

## Linguagem ubíqua (ubiquitous language)

O BDD reforça o uso de um vocabulário comum entre negócio e time técnico, para eliminar ambiguidade de tradução entre "o que o negócio pediu" e "o que foi construído" — conceito compartilhado com Domain-Driven Design.

## Three Amigos

Prática associada ao BDD em que **Product Owner (negócio), Desenvolvedor e Testador/QA** discutem uma funcionalidade antes da implementação, cada um trazendo uma perspectiva diferente (valor de negócio, viabilidade técnica, casos de borda), para chegar a exemplos concretos de comportamento esperado.

## Formato Given-When-Then

O comportamento é tipicamente descrito em três partes:

- **Given (Dado)** — o contexto/estado inicial antes do comportamento.
- **When (Quando)** — a ação ou evento que dispara o comportamento.
- **Then (Então)** — o resultado esperado, observável, após a ação.

Esse formato é a base da sintaxe Gherkin (ver [[gherkin]]), usada para tornar os exemplos executáveis por ferramentas de automação.

## Relevância para este agente

BDD fornece o raciocínio ("qual comportamento observável valida esta necessidade de negócio?") que a skill `identify_business_rules` e a geração de critérios de aceitação devem seguir. A materialização textual desse raciocínio é feita em Gherkin.
