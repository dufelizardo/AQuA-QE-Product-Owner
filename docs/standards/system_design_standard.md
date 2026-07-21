# Padrão de System Design

> Estrutura padrão para o System Design de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/system_design.md`.

## Propósito

Traduz o PRD (o quê e por quê) em uma visão técnica de alto nível (como): componentes do sistema, fluxo de dados e pontos de integração — antes de detalhar o comportamento do agente propriamente dito (Agent Design).

## Seções recomendadas

1. **Visão geral da arquitetura** — diagrama ou descrição textual dos componentes principais (orquestrador/agente, skills, memória, fontes de conhecimento, LLM).
2. **Componentes**
   - **Orquestrador/Agente** — quem decide qual skill chamar e quando.
   - **Skills** — funções que o agente pode executar (ver `skill_standard.md`).
   - **Fontes de conhecimento** — `knowledge/` (metodologia, templates, domínio) consumido via Context Engineering (ver `context_engineering_standard.md`).
   - **Memória** — estado persistido entre execuções (ver `memory_standard.md`).
   - **Interfaces externas** — entradas (ex.: arquivo de texto de requisitos) e saídas (ex.: User Stories em Markdown).
3. **Fluxo de dados** — sequência de passos desde a entrada até a saída, indicando onde cada skill atua.
4. **Pontos de integração** — sistemas externos (ex.: Jira, Confluence, repositórios de arquivos) e o contrato de cada integração.
5. **Restrições técnicas** — modelo(s) de LLM usado(s), limites de contexto, custo/latência esperados.
6. **Observabilidade** — o que é logado/monitorado para diagnosticar falhas do agente.

## Critérios de qualidade

- Cada componente deve mapear para pelo menos um requisito do PRD (ver `prd_standard.md`); nenhum componente deve existir sem justificativa.
- O fluxo de dados deve ser rastreável ponta a ponta, desde a entrada do usuário até a saída final.
- Decisões de arquitetura relevantes devem registrar a alternativa considerada e o motivo da escolha (mesmo que resumido).
