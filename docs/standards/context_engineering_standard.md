# Padrão de Context Engineering

> Estrutura padrão para as decisões de Context Engineering de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/context_engineering.md`.

## Propósito

Context Engineering define **o que entra na janela de contexto do LLM em cada chamada**, de onde vem, em que ordem e com que prioridade — a diferença entre o agente "saber" algo (existir em `knowledge/`) e o agente efetivamente "ver" algo no momento da decisão.

## Seções recomendadas

1. **Fontes de contexto** — de onde vêm as informações candidatas a entrar no prompt: `knowledge/methodology/`, `knowledge/domain/`, `knowledge/templates/`, memória (ver `memory_standard.md`), saída de skills anteriores (ex.: `retrieve_chunks`).
2. **Critério de seleção** — como decidir o que é relevante para a tarefa atual (busca semântica, filtragem por tipo de documento, sempre incluir vs. incluir sob demanda).
3. **Orçamento de tokens** — limite de contexto disponível e como ele é distribuído entre instruções fixas, conhecimento recuperado e histórico da conversa.
4. **Ordenação** — em que posição cada tipo de conteúdo aparece no prompt final (instruções, persona, conhecimento, exemplos, entrada do usuário).
5. **Formatação** — como cada fonte é serializada para o prompt (Markdown bruto, resumo, tabela, JSON).
6. **Atualização/invalidação** — quando o contexto recuperado precisa ser reconsultado (ex.: nova versão de um documento de `knowledge/`).

## Critérios de qualidade

- Toda informação incluída no contexto deve ter uma razão rastreável (nenhuma inclusão "por via das dúvidas" sem custo/benefício avaliado).
- O orçamento de tokens deve ser respeitado de forma previsível, não estourado silenciosamente.
- A estratégia de seleção deve ser testável — dado um input, deve ser possível prever (ou verificar) o que entrará no contexto.
