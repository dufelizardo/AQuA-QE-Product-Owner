# PRD — AQuA-QE Product Owner

> Estrutura conforme `../standards/prd_standard.md`.

## Contexto e problema

O refinamento manual de requisitos em User Stories, Épicos e Critérios de Aceitação é lento, inconsistente entre autores e propenso a lacunas (regras de negócio implícitas que se perdem, critérios de aceitação vagos, histórias grandes demais). Product Owners, Analistas de Negócio/QA e Desenvolvedores gastam tempo desproporcional estruturando informação que já existe, de forma dispersa, em PRDs, documentos de requisitos e tickets.

## Objetivo do produto

Gerar User Stories, Épicos e Critérios de Aceitação a partir de fontes de requisitos (arquivo de texto `.txt`, Markdown, chat ou Jira), com rastreabilidade total à fonte e aderência aos critérios de qualidade estabelecidos (INVEST, DoR, ISO/IEC/IEEE 29148), reduzindo o esforço manual de refinamento sem substituir a decisão humana final.

## Público-alvo / personas

Múltiplos papéis podem invocar o agente, em momentos diferentes do refinamento:

- **Product Owner** — gera e refina User Stories a partir do PRD antes do Backlog Refinement.
- **Analista de Negócios/QA** — usa o agente para estruturar requisitos elicitados em artefatos formais.
- **Desenvolvedor** — consulta a saída do agente como especificação de comportamento esperado (ver `../../knowledge/methodology/bdd.md`).

## Escopo

- Ler fontes de entrada em arquivo de texto (`.txt`), Markdown, chat ou Jira.
- Extrair requisitos candidatos e identificar ator, objetivo e regras de negócio.
- Gerar User Story(s) com critérios de aceitação em Gherkin.
- Validar a saída contra INVEST e o checklist de qualidade do agente (ver `validation_checklist.md`) antes de apresentá-la.
- Suportar tanto a geração de uma única história pontual quanto o processamento em lote de uma fonte inteira (Epic completo).
- Exportar o resultado em Markdown.
- Reter memória de projeto (decisões dentro do mesmo Epic) e de longo prazo (preferências e glossário consolidado entre sessões) — ver `memory.md`.

## Fora de escopo

- Implementar o código da funcionalidade descrita na User Story.
- Gerenciar o Sprint em si (ordenação final do Product Backlog, cerimônias do Scrum) — isso permanece com o Scrum Team e suas ferramentas.
- Aprovar definitivamente uma User Story sem revisão humana (ver `guardrails.md`) — o agente sempre entrega um artefato em estado de rascunho validado, nunca aprovado por conta própria.

## Requisitos funcionais

1. Ler e interpretar entradas em arquivo de texto (`.txt`), Markdown, chat e Jira.
2. Identificar ator, objetivo e regras de negócio a partir do texto de entrada.
3. Gerar User Story no formato "Como... quero... para que..." com critérios de aceitação em Given-When-Then.
4. Validar a história gerada contra INVEST e o checklist de qualidade antes de apresentá-la.
5. Quando a fonte for ambígua ou incompleta, parar e solicitar esclarecimento em vez de gerar uma suposição não sinalizada (ver `guardrails.md`).
6. Suportar geração unitária e em lote (Epic completo).
7. Exportar o resultado validado em Markdown.

## Requisitos não funcionais

- **Rastreabilidade** — todo elemento gerado (ator, objetivo, regra, critério) deve ser rastreável à fonte de entrada.
- **Nenhuma aprovação automática** — toda saída é um rascunho validado, sujeito a revisão humana obrigatória.
- **Consistência de formato** — toda saída segue os templates em `../../knowledge/templates/`.

## Métricas de sucesso

- Redução do tempo de refinamento gasto por PO/BA na escrita de User Stories.
- Taxa de aceitação sem retrabalho — % de histórias geradas aceitas pelo time sem edição substancial.
- Cobertura de requisitos — % dos requisitos presentes na fonte de entrada que efetivamente viram User Story rastreável.

## Riscos e premissas

- Premissa: a fonte de entrada contém informação suficiente para identificar ator e objetivo na maioria dos casos; quando não contém, o agente deve pedir esclarecimento (não adivinhar).
- Risco: fontes de entrada de baixa qualidade (arquivos de texto malformatados, tickets muito informais, mensagens de chat fragmentadas) podem limitar a taxa de extração automática.
- Risco: dependência de revisão humana obrigatória limita o ganho de velocidade se o time não incorporar o agente ao fluxo de refinamento.
