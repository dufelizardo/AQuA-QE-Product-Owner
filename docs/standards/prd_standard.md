# Padrão de PRD

> Estrutura padrão para o PRD (Product Requirements Document) de um agente desta plataforma. Define o formato; o conteúdo de cada agente fica em `../agent/prd.md`.

## Propósito

O PRD responde **por que o agente deve existir** e **o que ele precisa entregar**, antes de qualquer decisão de arquitetura ou implementação. É o documento de mais alto nível na cadeia `PRD → System Design → Agent Design → AI Spec/Rules/Skills`.

## Seções recomendadas

1. **Contexto e problema** — qual necessidade de negócio motiva o agente (ver conceito de *Need* no BACCM, `../../knowledge/methodology/babok.md`).
2. **Objetivo do produto** — resultado que o agente deve produzir, em uma frase.
3. **Público-alvo / personas** — quem usa o agente e quem consome seus outputs.
4. **Escopo** — o que o agente faz.
5. **Fora de escopo** — o que o agente explicitamente não faz (evita expansão silenciosa de responsabilidade).
6. **Requisitos funcionais** — capacidades que o agente deve ter, classificadas por prioridade.
7. **Requisitos não funcionais** — desempenho, custo (tokens/latência), segurança, disponibilidade.
8. **Métricas de sucesso** — como medir se o agente está entregando valor (ver `evaluation_standard.md`).
9. **Riscos e premissas** — dependências externas, limitações conhecidas, suposições assumidas.

## Critérios de qualidade

- Cada requisito funcional deve ser rastreável até um objetivo do produto (nenhum requisito "solto").
- Usar a mesma disciplina de escrita de requisitos individuais da ISO/IEC/IEEE 29148 (não ambíguo, verificável, singular) — ver `../../knowledge/methodology/iso29148.md`.
- Escopo e fora de escopo devem ser mutuamente exclusivos e, juntos, exaustivos o suficiente para não deixar zona cinzenta.
