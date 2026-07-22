# AQuA-QE Product Owner — Whitepaper

> Also available in [English](WHITEPAPER.en.md).

> Agente de engenharia de requisitos que gera PRDs (a partir de uma ideia), User Stories, Épicos e Critérios de Aceitação a partir de PRDs, documentos de requisitos, tickets Jira e páginas Confluence — com rastreabilidade obrigatória à fonte, validação automática e revisão humana no centro do ciclo.

Repositório: [github.com/dufelizardo/AQuA-QE-Product-Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner)

---

## 1. Resumo executivo

O refinamento manual de requisitos em User Stories, Épicos e Critérios de Aceitação é lento, inconsistente entre autores e propenso a lacunas: regras de negócio implícitas que se perdem, critérios de aceitação vagos, histórias grandes demais para caber em uma Sprint. Product Owners, Analistas de Negócio/QA e Desenvolvedores gastam tempo desproporcional estruturando informação que já existe — de forma dispersa — em PRDs, documentos de requisitos e tickets.

O AQuA-QE Product Owner é um agente que automatiza essa estruturação sem remover a decisão humana do processo. A partir de uma ideia informal, ele pode gerar o próprio PRD; a partir de uma fonte de requisitos (o PRD gerado, um arquivo `.txt`/Markdown, texto de chat, ticket Jira ou página Confluence), extrai requisitos candidatos, identifica ator/objetivo/regras de negócio, gera o artefato (PRD, User Story ou Épico completo) no formato ágil padrão, valida automaticamente contra INVEST/DoR, submete a um segundo LLM como revisor independente e só então apresenta o resultado para aprovação humana explícita. Nenhuma saída é aprovada pelo próprio agente.

O diferencial do projeto não é gerar texto plausível — qualquer LLM faz isso. É o **ciclo de refinamento interativo**: quando a revisão aponta um problema, o agente não tenta se autocorrigir adivinhando a resposta certa. Ele transforma o apontamento em uma pergunta objetiva, entrega essa pergunta a um humano, usa a resposta real como contexto adicional para reescrever a história, e só então repete a revisão. O ganho de qualidade vem da resposta humana, não da segunda tentativa do modelo.

## 2. Fundamentação metodológica

Nenhum critério de qualidade usado pelo agente foi inventado. Cada um está documentado em `knowledge/methodology/` e é referenciado diretamente pelas regras e guardrails do agente:

| Framework | Papel no agente |
|---|---|
| **Scrum Guide** (`scrum_guide.md`) | Delimita o que é papel do agente (estruturar o artefato) vs. papel do Scrum Team (priorizar backlog, conduzir cerimônias — fora de escopo). |
| **BABOK** (`babok.md`) | Fundamenta a elicitação e estruturação de requisitos em artefatos formais. |
| **ISO/IEC/IEEE 29148** (`iso29148.md`) | Referência para qualidade e completude de requisitos de software. |
| **INVEST** (`invest.md`) | Checklist de qualidade de toda User Story gerada — Independent, Negotiable, Valuable, Estimable, Small, Testable. |
| **DoR / DoD** (`dor.md`, `dod.md`) | Definição de Pronto/Feito usada como referência de completude antes da revisão humana. |
| **BDD / Gherkin** (`bdd.md`, `gherkin.md`) | Formato obrigatório dos Critérios de Aceitação — Given/When/Then verificável, nunca texto livre. |

Esses documentos não são decoração: `validate_story` e `validate_epic` implementam checklists derivados diretamente de INVEST/DoR, e o formato Given-When-Then é reforçado explicitamente no prompt de `generate_story`/`generate_epic_metadata`.

## 3. Princípios de design (guardrails)

Três guardrails de prioridade igual — nenhum subordinado aos outros — governam todo o comportamento do agente (`docs/agent/guardrails.md`):

- **GR-1 — Nunca inventar.** Nenhum ator, objetivo, regra de negócio ou critério de aceitação é gerado sem origem rastreável na fonte de entrada. Quando a fonte não contém informação suficiente, o agente **interrompe e solicita esclarecimento** — nunca preenche a lacuna com uma suposição não sinalizada. Na implementação, isso é literal: `identify_actor`/`identify_goal` retornam string vazia quando não conseguem identificar o campo com confiança, o que aciona o status `PENDING_CLARIFICATION`.
- **GR-2 — Nunca entregar história vaga ou não testável.** Toda saída passa por `validate_story`/`validate_epic` (checklist INVEST, Python puro, sem LLM) antes de ser apresentada.
- **GR-3 — Nunca omitir regra de negócio identificável.** Regras identificadas — explícitas ou implícitas — aparecem listadas na história mesmo quando não viram, isoladamente, um critério de aceitação.
- **Guardrail transversal — Sem aprovação automática.** Independentemente dos três guardrails acima serem satisfeitos, o agente nunca marca um artefato como "aprovado" — apenas como **rascunho validado** (`draft_validated`). A aprovação final é sempre um ato humano, nunca delegado ao LLM revisor nem ao checklist automático.

Esses guardrails viram regras formais e verificáveis (`RULE-001` a `RULE-006` em `docs/agent/rules.md`), com resolução de conflito explícita: regras bloqueantes (rastreabilidade, validação, regra de negócio, sem auto-aprovação) têm prioridade sobre a regra de formatação, que é apenas recomendação.

## 4. Arquitetura

```
Entrada (.txt/Markdown/chat/Jira/Confluence)
   → read_text_file / parse_chat_transcript+format_chat_transcript (só chat) / read_jira_issue / read_confluence_page
   → extract_requirements
   → retrieve_chunks (RAG sobre knowledge/methodology/, quando relevante)
   → identify_actor / identify_goal / identify_business_rules
   → generate_story  (LLM gerador — mistral)
   → validate_story  (checklist INVEST, Python puro)
   → review_story    (LLM revisor independente — phi4)
   → [se reprovado] generate_clarifying_questions → resposta humana → refine_story → revalidar
   → aceite humano explícito
   → export_markdown / update_jira_issue
```

Em modo lote, o mesmo padrão se repete em nível de Épico, mas em **duas fases**, não uma só — decisão de arquitetura que evita gastar o processamento caro (identificação de ator/objetivo/regras + geração + validação + revisão de cada User Story) antes de o Épico em si estar definido:

```
Entrada completa (.txt/Markdown/Confluence/Jira)
   → extract_requirements
   → extract_prd_context (visão, requisitos não funcionais, riscos, critérios de sucesso, restrições, dependências)
   → identify_epic_groups (agrupa os requisitos por coerência temática — 1 grupo se o PRD for coeso, N se cobrir frentes distintas)
   → por grupo: generate_epic_metadata (a partir do texto + requisitos do grupo, SEM nenhuma story ainda)
   → validate_epic
   → por Épico: recepção (menu) — gerar as User Stories agora / refinar o Épico / não continuar com este Épico
        → [refinar] generate_epic_clarifying_questions → resposta humana → refine_epic_metadata → validate_epic/review_epic (repete até aprovar ou o usuário desistir)
   → por Épico selecionado: generate_epic_stories: para cada requisito → generate_story → validate_story → review_story
   → validate_traceability (stories duplicadas, sem valor, requisitos órfãos)
   → review_epic (agora com as stories existentes, avalia coerência real com o Épico)
   → refinamento humano-no-loop por story reprovada
   → diff_epic_versions (changelog, se o Épico foi refinado) +, se a origem era 1 único ticket Jira, oferece persistir de volta nele (update_jira_epic)
   → aceite humano final
```

`generate_epic_metadata` depende apenas do texto de origem e dos requisitos extraídos — nunca das stories, que ainda não existem nesse ponto. Isso permite ao humano rejeitar, refinar ou pedir ajuste no Épico (título/objetivo/escopo/valor) **antes** de qualquer User Story ser gerada, evitando o desperdício de gerar um lote inteiro de stories sob um Épico com o escopo errado. A recepção é decidida **por Épico, individualmente** (não uma pergunta única para o lote inteiro) — cada Épico de `identify_epic_groups` tem seu próprio menu. Ao escolher "refinar", `review_epic` roda pela primeira vez (sob demanda, só para aquele Épico — não para todos os impressos na recepção, para não pagar esse custo de LLM sem necessidade), julgando clareza/coerência de título/objetivo/escopo/valor (ainda sem o eixo "coerência com as stories", que só existe depois). Só depois que as stories existem é que `review_epic` roda de novo com esse eixo completo — por isso a revisão do Épico acontece potencialmente em até três momentos: `validate_epic` (checklist automático, sempre), `review_epic` sob demanda na recepção (só se o usuário refinar) e `review_epic` de novo após as stories (sempre, dentro de `finalize_epic`). Write-back no Jira (`update_jira_epic`) só é oferecido quando o lote inteiro se resolveu em **um único** Épico — evita sobrescrever o mesmo ticket com o conteúdo de Épicos diferentes quando o PRD se divide em N grupos.

`identify_epic_groups` fecha a lacuna PRD→Épico(s): antes, um PRD com frentes temáticas distintas (ex.: "Agendamento" + "Notificações" + "Pagamento") sempre virava um único Épico artificialmente amplo, misturando tudo. Agora o agrupamento decide quantos Épicos fazem sentido — podendo ser um só, quando o PRD for coeso (comportamento padrão, sem mudança visível). Se a resposta do LLM não cobrir todos os requisitos exatamente uma vez, a skill cai no fallback seguro de um único grupo, nunca perdendo rastreabilidade nem inventando uma divisão inconsistente (GR-1). A relação é sempre unidirecional — um PRD gera um ou mais Épicos, nunca o contrário.

`extract_prd_context` fecha uma lacuna de rastreabilidade real: um PRD típico (`docs/standards/prd_standard.md`) contém muito mais do que requisitos funcionais — visão, público-alvo, requisitos não funcionais, restrições, critérios de sucesso, riscos, dependências. Antes, só o texto bruto e a lista de requisitos funcionais sobreviviam ao processamento; todo esse outro conteúdo era lido pelo LLM mas nunca estruturado nem preservado. `epic.prd_context` guarda essa informação vinculada ao Épico, sem introduzir nenhuma camada nova de processo — apenas preserva o que já era lido.

Camadas do código (`src/aqua_qe_product_owner/`):

- **`models/`** — estruturas de dados: `UserStory`, `Epic` (com `UnresolvedItem`), `AcceptanceCriteria`, `BusinessRule`, `Actor`, `Requirement`, `PRDContext`, `PRDDraft`, e o enum `StoryStatus` (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — 38 funções, cada uma com um único efeito colateral e uma única responsabilidade (ver seção 5).
- **`workflow/`** — orquestração da sequência de skills por caso de uso: `generate_prd.py` (`generate_prd_draft` → gera o PRD a partir de uma ideia; `refine_prd_draft` → refina com respostas humanas), `generate_user_story.py` (`finalize_story`), `generate_epic.py` (`generate_epic_shape` → define o Épico; `generate_epic_stories` → divide em User Stories e finaliza; `generate_epic` → wrapper de conveniência que encadeia as duas, sem checkpoint humano), `generate_acceptance.py`, `refine_story.py`.
- **`orchestrator/product_owner.py`** — ponto de entrada único (`handle_request(entrada, modo)`), decide entre modo `"unitario"` e `"lote"`.
- **`services/`** — integrações externas, introduzidas incrementalmente, uma por consumidor real: `llm_service` (Ollama), `embedding_service` (Ollama), `rag_service` (Qdrant embarcado), `jira_service` e `confluence_service` (REST API + httpx).

Deliberadamente **não existe** uma camada de `Feature` entre Épico e User Story no código (só como template em `knowledge/templates/feature.md`). A avaliação registrada no projeto concluiu que essa camada tem valor real, mas custo desproporcional para o volume de PRDs testados até agora — fica para quando um PRD grande o suficiente justificar o agrupamento, em vez de ser construída especulativamente.

## 5. As 38 skills

Skills sem LLM (Python puro, determinísticas):

- `validate_story`, `validate_epic`, `validate_prd` — checklist INVEST/DoR.
- `format_prd_markdown` — formata o PRD em Markdown (exportação local e corpo da página do Confluence).
- `diff_story_versions`/`diff_epic_versions` — changelog entre versões (regras/critérios novos vs. descontinuados; para Épico, também objetivo/escopo/valor antes-depois).
- `validate_traceability` — duplicidade, ausência de valor de negócio, requisitos órfãos.
- `parse_chat_transcript`/`format_chat_transcript` — reconhecem e normalizam transcrições de chat multi-remetente na entrada `--texto`, sem alterar texto corrido sem remetente identificável.

Skills com LLM gerador (`OLLAMA_MODEL`, padrão `mistral`):

- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd`, `extract_requirements`, `extract_prd_context`, `identify_epic_groups`, `identify_actor`, `identify_goal`, `identify_business_rules`, `generate_story`, `generate_clarifying_questions`, `refine_story`, `generate_epic_metadata`, `generate_epic_clarifying_questions`, `refine_epic_metadata`.

Skills com LLM revisor independente (`OLLAMA_REVIEW_MODEL`, padrão `phi4` — deliberadamente um modelo diferente do gerador, para mitigar *self-preference bias*):

- `review_story`, `review_epic`, `review_prd`.

Skills de embedding/RAG (Ollama `bge-m3` + Qdrant embarcado, sem servidor externo):

- `retrieve_chunks` — indexa e busca em `knowledge/methodology/` sob demanda.

Skills de I/O externo:

- `read_text_file` (disco), `read_jira_issue`/`read_confluence_page` (leitura, Jira/Confluence Cloud REST API), `export_markdown` (disco), `update_jira_issue`/`create_jira_epic`/`update_jira_epic`/`create_jira_story`/`create_confluence_page`/`update_confluence_page` (escrita, Jira/Confluence Cloud REST API — **só executadas após aceitação humana explícita no CLI, nunca automaticamente**; `update_confluence_page` ainda não está conectada a nenhum fluxo do CLI, só chamável diretamente como skill).

Detalhamento completo de entrada/saída/erros de cada skill em `docs/agent/skills.md`.

## 6. O ciclo de refinamento interativo (diferencial do projeto)

A maior parte dos agentes de geração de conteúdo trata "revisão reprovada" como um sinal para o próprio LLM tentar de novo. Esse projeto trata isso como um sinal para **envolver um humano com uma pergunta específica**:

1. `review_story`/`review_epic` reprova e produz `review_notes` — apontamentos concretos (ex.: "critério de aceitação não cobre o caso de erro X", "benefício não é mensurável").
2. `generate_clarifying_questions` transforma cada apontamento em uma pergunta objetiva e acionável.
3. O CLI (`run.py --refinar`) apresenta as perguntas no terminal; **um humano real responde** — não o mesmo LLM se autocorrigindo.
4. `refine_story` reescreve `description`, `business_rules` e `acceptance_criteria` usando as respostas como contexto real, não como uma nova tentativa às cegas.
5. O ciclo revalida (`validate_story`/`review_story`) e repete se necessário.
6. Ao final, um prompt pergunta explicitamente se o usuário **aceita** a história. Só esse aceite explícito muda o status para `accepted` — nunca o LLM, nunca o checklist automático (RULE-005).
7. `diff_story_versions` gera um changelog entre a versão original e a aceita (regras/critérios novos vs. descontinuados) — apoia a gestão do ciclo de vida da história no backlog.
8. Se a origem era um ticket Jira, o usuário é perguntado se deseja persistir a versão final de volta no ticket (`update_jira_issue`) — write-back nunca automático.

Esse desenho foi validado ao vivo em dois testes reais: um PRD informal sobre "Sistema de Agendamento de Consultas" (Épico completo com 6 User Stories, refinamento interativo ponta a ponta, criação real no Jira) e um PRD formal em uma página real do Confluence Cloud do usuário.

Importante: esse ciclo não é só um portão de aprovação. A resposta humana a cada pergunta gerada é uma **oportunidade real de trabalho conjunto** — o humano não está apenas corrigindo um erro apontado, está melhorando a escrita da história com contexto que só ele tem (regras de negócio implícitas, decisões de escopo, casos de borda que o texto de origem não deixava claro). O LLM estrutura a pergunta certa; quem melhora a história é a resposta humana.

## 7. Modos de operação

- **PRD** (`--modo prd`) — o passo "Ideia → PRD" que faltava: `generate_prd` gera um PRD completo (contexto/problema, objetivo, público-alvo, escopo, fora de escopo, requisitos funcionais/não funcionais, critérios de sucesso, riscos e premissas — conforme `docs/standards/prd_standard.md`) a partir de uma ideia informal, passa pelo mesmo padrão `validate_prd` → `review_prd` → `generate_prd_clarifying_questions`/`refine_prd` (ciclo de refinamento humano-no-loop completo, seção 6) → aceite humano explícito. Uma vez aceito, `format_prd_markdown` produz o texto final, que pode ser exportado (`--saida`), publicado no Confluence (`--publicar-confluence`) e/ou virar a entrada do modo lote (o CLI pergunta se deve continuar e gerar o Épico a partir dele). Entrada via `--arquivo` ou `--texto`.
- **Unitário** (`--modo unitario`) — uma única User Story por execução; `validate_story`/`review_story` já rodam de imediato (não há custo de "revisar N candidatos" a evitar, como no Épico) e o CLI sempre pergunta "Aceitar esta história?" antes de exportar, com ou sem `--refinar` — só recusar o aceite impede a exportação. `--refinar` liga o ciclo de perguntas/refinamento **antes** desse aceite, quando a história não sai aprovada. Entrada via `--arquivo`, `--texto` ou `--jira`.
- **Lote/Épico(s)** (`--modo lote`) — em duas fases: primeiro `extract_prd_context` + `identify_epic_groups` (agrupa os requisitos extraídos por coerência temática — um PRD coeso vira um único Épico; um PRD com frentes distintas pode virar vários) + `generate_epic_metadata` por grupo definem título/objetivo/escopo/valor/critérios de cada Épico candidato a partir do texto de origem — **sem gerar nenhuma User Story ainda** — e `validate_epic` confere o checklist automático de cada um; o CLI então apresenta, **por Épico, individualmente**, um menu de recepção (gerar as User Stories agora / refinar o Épico / não continuar com este Épico) — escolher refinar entra no ciclo `generate_epic_clarifying_questions` → resposta humana → `refine_epic_metadata` → `validate_epic`/`review_epic`, repetido até aprovar ou o usuário desistir. Só os Épicos confirmados (opção 1, com ou sem refinamento prévio) são divididos em User Stories (uma por requisito do seu grupo), cada uma passando pelo pipeline completo do modo unitário; itens ambíguos viram `unresolved_items` sem travar o restante do lote; `validate_traceability`, `review_epic` (agora com as stories existentes) e `diff_epic_versions` (changelog do Épico, se refinado) rodam antes do refinamento por story, um Épico de cada vez. Entrada via `--arquivo`, `--jira` ou `--confluence`.
- **`--criar-jira`** (modo lote) — após aceitação humana explícita **de cada Épico** (pergunta individual, um Épico de cada vez), cria o ticket de Épico e cada User Story como ticket filho no Jira Cloud (vínculo `parent` simples, assume projeto *team-managed*). Se o Épico veio de `--jira` e o lote resultou em um único Épico, também é oferecido persistir a versão refinada de volta no mesmo ticket (`update_jira_epic`), em vez de só criar tickets novos.
- **`--publicar-confluence`** (modo prd) — após aceitação humana explícita do PRD, pergunta o título e publica a página no Confluence Cloud (`create_confluence_page`), retornando a URL criada.

## 8. Integrações reais

- **Jira Cloud** (REST API v3) — leitura (`read_jira_issue`, convertendo Atlassian Document Format para texto puro), escrita (`update_jira_issue`/`update_jira_epic`, convertendo de volta para ADF) e criação (`create_jira_epic`/`create_jira_story`). Autenticação via Basic Auth (e-mail + API token gerado em `id.atlassian.com/manage-profile/security/api-tokens`).
- **Confluence Cloud** (REST API v1) — leitura de página (`read_confluence_page`), convertendo o storage format (XHTML) para texto puro via `html.parser.HTMLParser` da stdlib (sem dependência nova); **criação de página** (`create_confluence_page`/`create_page`), convertendo o Markdown do PRD de volta para o storage format (`#`/`##`/`###` viram `h1`/`h2`/`h3`, linhas `- item` consecutivas viram lista, o resto vira parágrafo, tudo HTML-escapado) — requer `CONFLUENCE_SPACE_KEY` além das credenciais do Jira, reaproveitadas (mesma conta Atlassian); e **atualização de página existente** (`update_confluence_page`/`update_page`, mesmo id/título, versão incrementada) — paridade com `update_jira_issue`, mas ainda não conectada a nenhum fluxo do CLI (chamável só diretamente como skill).

Todas as operações de **escrita** exigem aceitação humana explícita antes de disparar — não há nenhum caminho no código em que o agente escreve em um sistema externo sem confirmação do usuário.

## 9. Stack técnico

- **LLM local via Ollama** — `mistral` para geração, `phi4` como revisor independente, `bge-m3` para embeddings (1024 dimensões, bom desempenho em português). Escolha deliberada por modelos locais em vez de APIs de nuvem, configurável via `OLLAMA_MODEL`/`OLLAMA_REVIEW_MODEL`/`OLLAMA_EMBEDDING_MODEL`/`OLLAMA_BASE_URL`.
- **Qdrant embarcado** (`QdrantClient(path=...)`, sem servidor) para RAG sobre `knowledge/methodology/`.
- **`uv`** para dependências — projeto standalone (repositório próprio, fora do monorepo que o originou), com `httpx` e `python-dotenv` declarados explicitamente em `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Qualidade e cobertura de testes

133 testes automatizados cobrem todos os módulos implementados (91% de cobertura de linha), todos com chamadas a Ollama/Jira/Confluence mockadas — rápidos, determinísticos, sem dependência de infraestrutura externa para rodar em CI. A avaliação do agente em produção combina três camadas que nunca se substituem (`docs/agent/evaluation.md`):

1. Checklist automático (`validate_story`/`validate_epic`) — sem LLM.
2. LLM-como-juiz (`review_story`/`review_epic`) — modelo diferente do gerador.
3. Revisão humana obrigatória — único ato que efetivamente aprova um artefato.

Métricas de sucesso definidas no PRD: redução do tempo de refinamento, taxa de aceitação sem retrabalho, cobertura de requisitos (% dos requisitos da fonte que efetivamente viraram User Story rastreável).

## 11. O que ainda falta (deliberadamente adiado, não esquecido)

- **Camada `Feature`** entre Épico e User Story — avaliada e adiada até um PRD grande o suficiente justificar o agrupamento (ver seção 4).
- **Indexação de `knowledge/domain/`** — estrutura de pastas pronta (requisitos, regras de negócio, processos, telas, API, banco, glossário), vazia até haver um cliente/projeto real para popular.
- **Memória de projeto/longo prazo** (`memory.md`) — distinta do RAG sobre `knowledge/methodology/`, ainda não implementada.
- **Resiliência a falhas de infraestrutura do Ollama local** — instabilidade observada em execuções longas com troca de modelo (gerador ↔ revisor); decisão consciente de reexecutar manualmente em vez de adicionar retry automático, até haver evidência de que o custo de complexidade compensa.
- **`update_confluence_page` sem fluxo de CLI** — a skill existe (paridade com `create_confluence_page`), mas nenhum comando do `run.py` a aciona hoje; chamável só diretamente.

## 12. Como executar

Ver `README.md`/`README.pt.md` para o passo a passo completo de instalação (Python 3.12+, `uv`, Ollama + modelos, `.env.example` → `.env`) e todos os exemplos de uso do `run.py` (`--modo prd`/`unitario`/`lote`, `--arquivo`/`--texto`/`--jira`/`--confluence`, `--refinar`, `--criar-jira`, `--publicar-confluence`).

## 13. Conclusão

O AQuA-QE Product Owner não busca substituir o Product Owner — busca eliminar o trabalho mecânico de estruturação que precede a decisão dele. Cada guardrail do projeto (nunca inventar, nunca entregar história vaga, nunca omitir regra de negócio, nunca aprovar sozinho) existe para que a saída do agente seja sempre um ponto de partida confiável para revisão humana, nunca um substituto dela. O ciclo de refinamento interativo — perguntas geradas pelo LLM, respondidas por um humano real, incorporadas de volta à história — é a peça central que diferencia este agente de um simples gerador de texto plausível.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
