# AQuA-QE Product Owner

> Também disponível em [English](README.md).

Agente que gera User Stories, Épicos e Critérios de Aceitação a partir de PRDs, documentos de requisitos e outras fontes de entrada — seguindo o fluxo de engenharia de agentes:

```
PRD → System Design → Agent Design → AI Specs/Rules/Skills → Context Engineering → Memory/MCP → Agents → Outputs
```

## Estrutura

- **`docs/standards/`** — padrões da plataforma (como escrever um AI Spec, uma Rule, um PRD, etc.). Mudam pouco.
- **`docs/agent/`** — especificação completa deste agente: PRD, System Design, Agent Design, AI Spec, Rules, Persona, Objectives, Output Schema, Guardrails, Evaluation, Prompt e o `agent_manifest.yaml` (manifesto do agente — inputs, outputs, skills, memory, rules).
- **`knowledge/domain/`** — conhecimento específico do domínio/cliente (requisitos, regras de negócio, processos, telas, API, banco, glossário).
- **`knowledge/methodology/`** — material metodológico que orienta o agente (Scrum Guide, BABOK, ISO 29148, INVEST, DoR, DoD, BDD, Gherkin).
- **`knowledge/templates/`** — estrutura pura, sem conhecimento (templates de User Story, Epic, Feature, Acceptance Criteria, Business Rule, Task).
- **`knowledge/examples/`** — exemplos para few-shot (bons e maus exemplos, por categoria).
- **`knowledge/glossary/`** e **`knowledge/regulations/`** — glossário geral e regulações aplicáveis à plataforma.
- **`src/aqua_qe_product_owner/skills/`** — skills do agente em Python (ler arquivo de texto, ler ticket Jira, recuperar chunks, extrair requisitos, identificar ator/objetivo/regras, gerar/validar/revisar/refinar a story, gerar metadados do Épico, comparar versões, exportar em Markdown, atualizar/criar tickets no Jira).
- **`src/aqua_qe_product_owner/models/`** — estruturas de dados do agente (User Story, Epic, Acceptance Criteria, Business Rule, Actor, Requirement).
- **`src/aqua_qe_product_owner/workflow/`** — orquestração da sequência de skills por caso de uso (gerar User Story unitária, gerar Epic em lote, gerar/complementar critérios de aceitação).
- **`src/aqua_qe_product_owner/orchestrator/`** — ponto de entrada único que decide qual workflow executar.
- **`src/aqua_qe_product_owner/services/`** — integrações externas: `llm_service` (Ollama local, geração), `embedding_service` (Ollama local, `bge-m3`), `rag_service` (Qdrant embutido/local, sem servidor) e `jira_service` (API REST do Jira Cloud).

## Configuração

Este é um repositório independente (não faz parte de nenhum monorepo) — o `uv sync` aqui resolve e instala suas próprias dependências.

1. Instale [Python 3.12+](https://www.python.org/) e [uv](https://docs.astral.sh/uv/).
2. Instale o [Ollama](https://ollama.com) e baixe os três modelos locais usados por este agente:
   ```bash
   ollama pull mistral   # geração
   ollama pull phi4      # revisor independente
   ollama pull bge-m3    # embeddings
   ```
3. Clone este repositório e instale as dependências:
   ```bash
   git clone https://github.com/dufelizardo/AQuA-QE-Product-Owner.git
   cd AQuA-QE-Product-Owner
   uv sync
   ```
4. Copie `.env.example` para `.env` e preencha os valores necessários (o Ollama funciona com os padrões; as credenciais de Jira/Confluence só são necessárias para `--jira`, `--confluence` e `--criar-jira`):
   ```bash
   cp .env.example .env
   ```
5. Rode a suíte de testes (totalmente mockada, sem chamadas reais a Ollama/Jira/Confluence) para confirmar a configuração:
   ```bash
   uv run pytest
   ```

## Uso

```bash
# Uma User Story a partir de um arquivo .txt/.md
uv run python run.py --modo unitario --arquivo requisito.txt --saida story.md

# Uma User Story a partir de texto direto (chat)
uv run python run.py --modo unitario --texto "Como cliente, quero..." --saida story.md

# Uma User Story a partir de um ticket do Jira Cloud
uv run python run.py --modo unitario --jira PROJ-123 --saida story.md

# Um Epic (lote) a partir de uma fonte maior, exportando cada história
uv run python run.py --modo lote --arquivo prd.txt --saida saida_epic/

# Com ciclo interativo de refinamento (perguntas, aceite final, changelog, write-back no Jira)
uv run python run.py --modo unitario --jira PROJ-123 --saida story.md --refinar

# Gerar um Epic completo e criá-lo no Jira (com as stories como tickets filhos)
uv run python run.py --modo lote --arquivo prd.txt --saida saida_epic/ --criar-jira

# Um Epic a partir de uma página do Confluence Cloud (PRD)
uv run python run.py --modo lote --confluence "https://seu-site.atlassian.net/wiki/.../pages/163841/..." --criar-jira
```

`--saida` é opcional em ambos os modos (sem ela, o resultado só é impresso no terminal). Para usar `--jira`, preencha `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` no `.env` (o token é gerado em `id.atlassian.com/manage-profile/security/api-tokens`).

`--refinar` ativa o ciclo interativo: se a história não sair aprovada, o agente gera perguntas de esclarecimento a partir dos apontamentos da revisão, você responde no terminal, e as respostas viram contexto real para reescrever a história (em vez do LLM adivinhar sozinho). Ao final, um prompt pergunta se você aceita a história; se sim, é gerado um changelog (regras/critérios novos vs. descontinuados, no terminal e em `<saida>.changelog.md`) e, se a entrada veio de `--jira`, é perguntado se deve persistir a versão final de volta no ticket.

`--criar-jira` (só no modo lote) gera o Épico completo — título, objetivo, escopo, valor e critérios de aceitação, não só as User Stories — e, após um prompt de aceitação explícito, cria o ticket do Épico no Jira (`JIRA_PROJECT_KEY`, `JIRA_EPIC_ISSUE_TYPE_ID`) e cada User Story como ticket filho (`JIRA_STORY_ISSUE_TYPE_ID`, vínculo `parent` — assume projeto *team-managed*), retornando as chaves criadas. Ver `run.py --help` para todas as opções.

## Status

`docs/agent/`, `docs/standards/` e `knowledge/` (exceto `domain/`, `regulations/` e `examples/`, que dependem de um cliente/projeto real) estão com conteúdo real preenchido.

Em `src/`, todas as 10 skills e os três workflows estão implementados e funcionam de ponta a ponta com modelos locais via Ollama:

- **Modo unitário** (`workflow/generate_user_story.py`) — `read_text_file` → `extract_requirements` → `identify_actor`/`identify_goal`/`identify_business_rules` → `generate_story` (LLM `mistral`) → `validate_story` (checklist Python puro) → `review_story` (LLM revisor `phi4`, independente do gerador) → status final.
- **Modo lote** (`workflow/generate_epic.py`) — mesma sequência aplicada a cada requisito extraído da fonte; itens ambíguos (ator/objetivo não identificado) viram `unresolved_items` sem travar o restante do lote. `generate_epic_metadata` completa o Épico com título, objetivo, escopo, valor e critérios de aceitação de alto nível (antes ficavam vazios), e o Épico passa pelo mesmo ciclo de qualidade da Story: `validate_epic` (checklist Python puro) → `review_epic` (LLM revisor `phi4`). Antes do refinamento por story, `validate_traceability` verifica duplicidade entre stories, stories sem valor de negócio e requisitos órfãos.
- **Complemento de critérios** (`workflow/generate_acceptance.py`) — gera critérios de aceitação adicionais para uma User Story já existente e reaplica `validate_story`/`review_story`.
- **Refinamento interativo** (`workflow/refine_story.py`, via `run.py --refinar`) — `generate_clarifying_questions` transforma os apontamentos da revisão em perguntas ao usuário; `refine_story` reescreve a história com as respostas; `diff_story_versions` compara a versão final com a original (regras/critérios novos vs. descontinuados); `update_jira_issue` persiste a versão aceita de volta no ticket, sob confirmação explícita.
- **Criação de Épico no Jira** (via `run.py --criar-jira`) — `create_jira_epic` cria o ticket do Épico; `create_jira_story` cria cada User Story como ticket filho — ambas só rodam após aceitação humana explícita.
- `orchestrator/product_owner.py` (`handle_request(entrada, modo)`) trata `"unitario"` e `"lote"`.
- `retrieve_chunks` indexa e busca em `knowledge/methodology/` via embedding local (`bge-m3`) e Qdrant local; `read_jira_issue` busca um ticket do Jira Cloud via API REST; `read_confluence_page` busca uma página do Confluence Cloud (mesmas credenciais do Jira); `export_markdown` formata a saída final.

Ainda faltam: uma camada de `Feature` entre Epic e User Story (hoje só existe como template em `knowledge/templates/feature.md`, sem skill/workflow — avaliado e adiado deliberadamente até haver um PRD grande o suficiente para precisar de agrupamento), indexação de `knowledge/domain/` (vazio, aguardando cliente real) e memória de projeto/longo prazo (`memory.md` — distinta do RAG sobre `knowledge/`, ainda não implementada). `tests/` cobre todos os módulos implementados (68 testes, mocks de LLM/HTTP — rápidos e determinísticos, não chamam Ollama nem Jira/Confluence de verdade).

Este projeto tem repositório git próprio, independente do monorepo raiz (conforme a convenção "todo projeto novo recebe repositório separado" — ver `CLAUDE.md` raiz): [github.com/dufelizardo/AQuA-QE-Product-Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner).
