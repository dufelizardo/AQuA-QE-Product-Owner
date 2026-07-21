# Definition of Ready (DoR)

> Prática popularizada por Bill Wake, Roman Pichler e amplamente adotada em times ágeis. Não é um artefato formal do Scrum Guide, mas um acordo de time que precede o Sprint Planning.

## O que é

Um checklist compartilhado pelo time que define quando um item do Product Backlog está claro e maduro o suficiente para ser puxado para dentro de um Sprint. É o "portão de entrada" do item — o oposto complementar da Definition of Done, que é o "portão de saída" (ver [[dod]]).

## Critérios comuns

Não existe uma lista universal fixa (cada time define a sua), mas os critérios recorrentes na literatura e na prática incluem:

- A história é **INVEST-compliant** (ver [[invest]]), em especial: independente, pequena e estimável.
- **Critérios de aceitação** estão definidos e compreendidos por todo o time.
- **Dependências** externas (times, sistemas, dados) foram identificadas e não bloqueiam o início.
- A história foi **estimada** pelo time (ex.: Planning Poker, story points).
- Não há **impedimentos conhecidos** (acesso, ambiente, decisão de negócio pendente).
- O time entende o **valor de negócio** e o objetivo por trás da história.
- Mockups, protótipos ou especificações de tela necessários (quando aplicável) estão anexados ou referenciados.

## Por que existe

Evita que o time comece a trabalhar em algo mal compreendido, gerando retrabalho, estouro de estimativa ou paralisação no meio do Sprint por falta de informação. É uma ferramenta de **prevenção**, não de burocracia — o item só entra no Sprint Backlog depois de passar por esse crivo no refinamento (Backlog Refinement / Grooming).

## Relevância para este agente

A DoR é o critério de saída da skill de geração/validação de User Stories: uma história só deveria ser considerada "pronta para entrega ao time" depois de passar pelos itens de checklist acima, o que em geral coincide com os resultados das skills `validate_story` e `identify_business_rules`.
