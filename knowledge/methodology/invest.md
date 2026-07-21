# INVEST

> Baseado no critério INVEST, cunhado por Bill Wake (2003) para avaliar a qualidade de User Stories.

## O que é

Um mnemônico com seis características que uma User Story bem escrita deve apresentar. Não é uma norma formal, mas uma heurística amplamente adotada em times ágeis para avaliar se uma história está pronta para ser trabalhada.

## As seis características

- **I — Independent (Independente)** — a história pode ser desenvolvida e entregue sem depender obrigatoriamente de outra história ainda não feita. Reduz acoplamento no planejamento e na priorização.
- **N — Negotiable (Negociável)** — a história não é um contrato fechado e detalhado; é um convite à conversa entre Product Owner e time sobre a melhor forma de resolver a necessidade. Detalhes emergem na conversa, não são impostos de antemão.
- **V — Valuable (Valiosa)** — entrega valor perceptível a um stakeholder (usuário, cliente ou negócio). Se não está claro o valor, a história não deveria existir.
- **E — Estimable (Estimável)** — o time consegue estimar o tamanho/esforço da história com informação razoável. Se não é estimável, geralmente falta clareza ou a história é grande demais.
- **S — Small (Pequena)** — cabe confortavelmente dentro de um Sprint; histórias grandes devem ser fatiadas (splitting) em histórias menores e ainda assim valiosas.
- **T — Testable (Testável)** — existe uma forma objetiva de verificar se a história foi implementada corretamente, geralmente expressa em critérios de aceitação.

## Relação com outros conceitos

- **Negotiable** reforça por que a User Story usa um formato conciso ("Como... quero... para que...") em vez de uma especificação exaustiva.
- **Testable** conecta diretamente com critérios de aceitação escritos em Gherkin (ver [[gherkin]] e [[bdd]]).
- **Small** e **Estimable** são pré-condições comuns em uma Definition of Ready (ver [[dor]]).

## Relevância para este agente

INVEST é o principal checklist de qualidade que o agente aplica à User Story como um todo, antes ou durante a validação (skill `validate_story`). Cada letra do mnemônico corresponde a uma pergunta de verificação objetiva sobre o texto gerado.
