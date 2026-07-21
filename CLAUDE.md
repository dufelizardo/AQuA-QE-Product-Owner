# CLAUDE.md

Este arquivo orienta o Claude Code ao trabalhar neste repositório.

## O que é este projeto

Agente que gera User Stories, Épicos e Critérios de Aceitação a partir de PRDs, documentos de requisitos, tickets Jira e páginas Confluence — com rastreabilidade obrigatória à fonte, validação automática e revisão humana no centro do ciclo. Ver `WHITEPAPER.md` (também em inglês: `WHITEPAPER.en.md`) para a visão completa, e `docs/architecture/` para os diagramas (draw.io + SVG).

Este é um **repositório standalone**, próprio, independente de qualquer monorepo — não assuma dependências herdadas de um workspace pai.

## Comandos essenciais

```bash
# Instalar/sincronizar dependências
uv sync

# Rodar toda a suíte de testes (mockada, sem chamadas reais a Ollama/Jira/Confluence)
uv run pytest

# Rodar um teste único
uv run pytest tests/test_generate_story.py::test_nome_do_teste

# Gerar uma única User Story a partir de um arquivo
uv run python run.py --modo unitario --arquivo requisito.txt --saida story.md

# Gerar um Epic completo (lote) a partir de uma fonte maior
uv run python run.py --modo lote --arquivo prd.txt --saida saida_epic/

# Ver todas as opções (--jira, --confluence, --refinar, --criar-jira, etc.)
uv run python run.py --help
```

Não há configuração própria de lint/type-check (`ruff`/`basedpyright`) neste `pyproject.toml` — isso existe apenas na raiz do monorepo que originou este projeto, não neste repositório standalone.

## Setup local

Ver a seção "Setup"/"Configuração" em `README.md`/`README.pt.md`: requer Python 3.12+, `uv`, Ollama instalado com os modelos `mistral`, `phi4` e `bge-m3` baixados, e um `.env` preenchido a partir de `.env.example`.

## Arquitetura (resumo — detalhe completo em `docs/agent/system_design.md` e `WHITEPAPER.md`)

```
Entrada (.txt/Markdown/chat/Jira/Confluence)
  → CLI (run.py) → orchestrator/product_owner.py → workflow/* → skills/* → models/* → services/*
```

- `src/aqua_qe_product_owner/models/` — `UserStory`, `Epic`, `AcceptanceCriteria`, `BusinessRule`, `Actor`, `Requirement`, enum `StoryStatus`.
- `src/aqua_qe_product_owner/skills/` — 22 funções de responsabilidade única (ver `docs/agent/skills.md`).
- `src/aqua_qe_product_owner/workflow/` — orquestra a sequência de skills por caso de uso (`generate_user_story`, `generate_epic`, `generate_acceptance`, `refine_story`).
- `src/aqua_qe_product_owner/orchestrator/product_owner.py` — ponto de entrada único, `handle_request(entrada, modo)`.
- `src/aqua_qe_product_owner/services/` — integrações externas: `llm_service`/`embedding_service` (Ollama), `rag_service` (Qdrant embarcado), `jira_service`/`confluence_service` (REST API + httpx).

## Convenções críticas

- **Nunca inventar** (GR-1, `docs/agent/guardrails.md`): ator, objetivo, regra de negócio ou critério de aceitação só existem se rastreáveis à fonte de entrada. Quando não identificáveis, `identify_actor`/`identify_goal` retornam string vazia (`""`), o que aciona `PENDING_CLARIFICATION` — nunca preencha esses campos com suposição.
- **Sem aprovação automática** (RULE-005): nenhuma skill/workflow define `StoryStatus.ACCEPTED`. Esse status só é atribuído pelo CLI (`run.py`), após confirmação humana explícita no terminal.
- **Toda saída de LLM gerador/revisor é sempre em português**, por design, independentemente do idioma da fonte de entrada — instrução explícita e hardcoded no prompt de `generate_story.py`, `generate_epic_metadata.py` e `refine_story.py` ("Responda sempre em português, mesmo que o texto de origem contenha trechos em outro idioma"). Não é um comportamento adaptativo por idioma da entrada.
- **Dois LLMs sempre diferentes**: `OLLAMA_MODEL` (padrão `mistral`) gera; `OLLAMA_REVIEW_MODEL` (padrão `phi4`) revisa. É deliberado — mitiga *self-preference bias* de um modelo aprovar a própria saída.
- **Escritas externas nunca são automáticas**: `update_jira_issue`, `create_jira_epic`, `create_jira_story` só são chamadas pelo CLI após aceitação humana explícita.
- **Testes sempre mockam** Ollama/Jira/Confluence — nenhum teste em `tests/` faz chamada real de rede. Ao adicionar um teste para uma skill/service novo, siga esse padrão.
- **Camada `Feature`** (entre Epic e User Story) foi avaliada e deliberadamente adiada — existe só como template em `knowledge/templates/feature.md`, sem model/skill/workflow. Não implementar especulativamente; ver seção 4 e 11 do `WHITEPAPER.md` para o raciocínio completo.
- **`knowledge/domain/`** está vazio de propósito (aguardando um cliente/projeto real) — não confundir com pasta incompleta.

## Onde procurar mais detalhe

- `docs/agent/` — PRD, System Design, Agent Design, Rules, Guardrails, Persona, Objectives, Skills, Evaluation (a spec formal completa do agente).
- `knowledge/methodology/` — os frameworks reais que fundamentam os critérios de qualidade (INVEST, DoR/DoD, BDD/Gherkin, BABOK, ISO 29148, Scrum Guide) — nenhum critério do agente foi inventado à parte desses documentos.
- `WHITEPAPER.md` / `WHITEPAPER.en.md` — visão consolidada, inclui o ciclo de refinamento humano-no-loop (o diferencial do projeto).
- `docs/architecture/` — diagramas visuais (draw.io + SVG) dos mesmos fluxos.
