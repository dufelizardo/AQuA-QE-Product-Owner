# Skills

> Documentação das skills implementadas em `../../src/aqua_qe_product_owner/skills/`, no formato definido em `../standards/skill_standard.md`. Ordem conforme `agent_manifest.yaml`. Tipos de entrada/saída referem-se às estruturas de `../../src/aqua_qe_product_owner/models/`.
>
> `extract_requirements`, `extract_prd_context`, `identify_actor`, `identify_goal`, `identify_business_rules`, `generate_story`, `generate_clarifying_questions`, `refine_story`, `generate_epic_metadata`, `generate_prd`, `generate_prd_clarifying_questions` e `refine_prd` usam um LLM local via Ollama (`../../src/aqua_qe_product_owner/services/llm_service.py`, modelo configurável por `OLLAMA_MODEL`, padrão `mistral`). `validate_story`, `validate_epic`, `validate_prd`, `format_prd_markdown` e `diff_story_versions`/`validate_traceability` são Python puro, sem LLM (ver `evaluation.md`). `review_story`, `review_epic` e `review_prd` usam um segundo LLM, diferente do gerador (`OLLAMA_REVIEW_MODEL`, padrão `phi4`), como revisor independente (LLM-como-juiz). `retrieve_chunks` usa embedding local (`services/embedding_service.py`, modelo `bge-m3`) e um Qdrant embutido/local (`services/rag_service.py`, sem servidor externo). `read_jira_issue`, `update_jira_issue`, `create_jira_epic` e `create_jira_story` usam a API REST do Jira Cloud (`services/jira_service.py`) — as três últimas só são chamadas após aceitação humana explícita no CLI (`run.py`), nunca automaticamente. `read_confluence_page` e `create_confluence_page` usam a API REST do Confluence Cloud (`services/confluence_service.py`), reaproveitando as mesmas credenciais do Jira (mesma conta Atlassian) — `create_confluence_page` também só é chamada após aceitação humana explícita.

## read_text_file

- **Descrição**: lê um arquivo de texto (`.txt` ou `.md`) e retorna seu conteúdo. Entrada via chat não passa por esta skill — chega como texto direto.
- **Entrada**: `caminho: str` — caminho do arquivo `.txt` ou `.md`.
- **Saída**: `str` — conteúdo do arquivo.
- **Efeitos colaterais**: leitura de arquivo em disco.
- **Erros esperados**: arquivo inexistente, ilegível ou com encoding inválido.
- **Dependências**: nenhuma outra skill.

## read_jira_issue

- **Descrição**: busca um ticket no Jira Cloud (resumo + descrição) e retorna como texto simples, convertendo o corpo do formato Atlassian Document Format (ADF) para texto puro.
- **Entrada**: `issue_key: str` — chave do ticket (ex.: `PROJ-123`).
- **Saída**: `str` — resumo e descrição concatenados.
- **Efeitos colaterais**: chamada HTTP à API REST do Jira Cloud (`services/jira_service.py`); requer `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` no `.env`.
- **Erros esperados**: credenciais ausentes (`KeyError`); ticket inexistente ou sem permissão (erro HTTP via `httpx`).
- **Dependências**: nenhuma outra skill.

## read_confluence_page

- **Descrição**: busca uma página do Confluence Cloud (título + corpo) e retorna como texto simples, convertendo o storage format (XHTML) para texto puro. Aceita a URL completa da página ou apenas o ID numérico.
- **Entrada**: `pagina: str` — URL completa (ex.: `https://site.atlassian.net/wiki/spaces/.../pages/163841/...`) ou apenas o ID (ex.: `163841`).
- **Saída**: `str` — título e corpo concatenados.
- **Efeitos colaterais**: chamada HTTP à API REST do Confluence Cloud (`services/confluence_service.py`); requer `JIRA_BASE_URL`, `JIRA_EMAIL` e `JIRA_API_TOKEN` no `.env` (mesmas credenciais do Jira — mesma conta Atlassian).
- **Erros esperados**: credenciais ausentes (`KeyError`); página inexistente ou sem permissão (erro HTTP via `httpx`).
- **Dependências**: nenhuma outra skill.

## retrieve_chunks

- **Descrição**: recupera os trechos de `knowledge/methodology/` mais relevantes para uma consulta. Indexa sob demanda (na primeira busca) se a coleção ainda não existir.
- **Entrada**: `consulta: str`, `k: int = 5` — número de trechos a retornar.
- **Saída**: `list[str]` — trechos recuperados, ordenados por relevância.
- **Efeitos colaterais**: chamada ao serviço de embedding (`bge-m3`) e consulta/gravação no Qdrant local (`.data/qdrant/`, arquivo, sem servidor).
- **Erros esperados**: nenhum trecho relevante encontrado para a consulta (retorna lista vazia).
- **Dependências**: nenhuma outra skill. Cobre hoje apenas `knowledge/methodology/` — não indexa `knowledge/domain/` (ainda vazio).

## extract_requirements

- **Descrição**: extrai os requisitos candidatos presentes no texto de entrada.
- **Entrada**: `texto: str` — texto bruto (ex.: saída de `read_text_file` ou texto de chat).
- **Saída**: `list[Requirement]` — requisitos candidatos, cada um com `source_reference` rastreável (GR-1).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: texto sem requisitos identificáveis (retorna lista vazia); resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: geralmente consome a saída de `read_text_file` (ou o texto de chat, recebido diretamente).

## extract_prd_context

- **Descrição**: extrai o conteúdo do PRD além dos requisitos funcionais — visão, problema, objetivos, público-alvo, requisitos não funcionais, restrições, critérios de sucesso, riscos e dependências (ver `../standards/prd_standard.md`) — para que essa informação não seja descartada após `extract_requirements` (fecha uma lacuna de rastreabilidade: hoje só os requisitos funcionais sobrevivem ao Épico gerado).
- **Entrada**: `texto: str` — fonte completa.
- **Saída**: `PRDContext` — todos os campos opcionais (string/lista vazia quando não identificável, GR-1).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill; chamada por `workflow/generate_epic.py::generate_epic_shape`, junto de `extract_requirements`, antes de qualquer User Story ser gerada.

## identify_actor

- **Descrição**: identifica o ator (persona) principal descrito no texto.
- **Entrada**: `texto: str`.
- **Saída**: `str` — nome/descrição do ator identificado; string vazia (`""`) quando não identificável com confiança (aciona RULE-004 no workflow).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill (opera sobre o texto completo de entrada).

## identify_goal

- **Descrição**: identifica o objetivo (goal) descrito no texto.
- **Entrada**: `texto: str`.
- **Saída**: `str` — objetivo identificado; string vazia (`""`) quando não identificável com confiança (aciona RULE-004 no workflow).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill (opera sobre o texto completo de entrada).

## identify_business_rules

- **Descrição**: identifica as regras de negócio implícitas ou explícitas no texto.
- **Entrada**: `texto: str`.
- **Saída**: `list[BusinessRule]` — regras de negócio identificadas, cada uma com `source_reference` rastreável (GR-3).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: nenhuma regra identificável no texto (retorna lista vazia); resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill (opera sobre o texto completo de entrada); ver `../../knowledge/templates/business_rule.md`.

## generate_story

- **Descrição**: gera uma User Story a partir do ator, objetivo e contexto informados.
- **Entrada**: `ator: str`, `objetivo: str`, `contexto: dict` (chaves usadas: `business_rules: list[BusinessRule]`, `texto_fonte: str`, `id: str` opcional).
- **Saída**: `UserStory` — sempre criada com `status = PENDING_CLARIFICATION`; o status final é decidido pelo workflow após `validate_story` (ver `../../knowledge/templates/user_story.md`).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome as saídas de `identify_business_rules` e, opcionalmente, `retrieve_chunks`; `ator`/`objetivo` vêm de `identify_actor`/`identify_goal`.

## validate_story

- **Descrição**: valida se a User Story atende aos critérios INVEST e ao checklist do agente.
- **Entrada**: `story: UserStory`.
- **Saída**: `bool` — indica se a história passa no checklist automático (não decide aprovação humana, ver `guardrails.md`).
- **Efeitos colaterais**: nenhum — checklist em Python puro, sem chamada a LLM (distinção de `evaluation.md`).
- **Erros esperados**: nenhum (checagens sobre campos ausentes/vazios retornam `False`, não lançam exceção).
- **Dependências**: consome a saída de `generate_story`; critérios definidos em `../../knowledge/methodology/invest.md` e `../agent/validation_checklist.md`.

## review_story

- **Descrição**: revisa a User Story com um segundo LLM, diferente do usado em `generate_story`, contra os critérios INVEST — mitiga o viés de um modelo aprovar a própria saída (self-preference bias).
- **Entrada**: `story: UserStory`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão (`OLLAMA_REVIEW_MODEL`, padrão `phi4`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_story`, após `validate_story` aprovar o checklist automático (ver `workflow/generate_user_story.py`).

## generate_clarifying_questions

- **Descrição**: transforma os `review_notes` de uma User Story em perguntas diretas e acionáveis para o Product Owner responder (fecha o ciclo entre `review_story` apontar um problema e o usuário resolvê-lo).
- **Entrada**: `story: UserStory`.
- **Saída**: `list[str]` — lista de perguntas; vazia se a história não tiver `review_notes`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `review_notes`, preenchido por `review_story`.

## refine_story

- **Descrição**: reescreve `description`, `business_rules` e `acceptance_criteria` de uma User Story usando as respostas do usuário às perguntas de esclarecimento — não o LLM adivinhando sozinho a correção.
- **Entrada**: `story: UserStory`, `respostas: list[dict]` (cada item: `{"pergunta": str, "resposta": str}`).
- **Saída**: `UserStory` — mesma história, campos atualizados; `status`/`review_notes` só são recalculados pelo workflow (`workflow/refine_story.py`), que reaplica `validate_story`/`review_story`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome as perguntas de `generate_clarifying_questions` e as respostas do usuário (coletadas no CLI, `run.py`).

## diff_story_versions

- **Descrição**: compara duas versões de uma User Story (antes/depois de um refinamento) e identifica regras de negócio e critérios de aceitação novos vs. descontinuados — changelog de rastreabilidade entre versões.
- **Entrada**: `antes: UserStory`, `depois: UserStory`.
- **Saída**: `dict` com `regras_novas`, `regras_descontinuadas`, `criterios_novos`, `criterios_descontinuados`.
- **Efeitos colaterais**: nenhum — comparação pura em Python (diferença de conjuntos), sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: nenhuma outra skill; usada pelo CLI (`run.py`) após a aceitação final da história.

## generate_epic_metadata

- **Descrição**: define título, objetivo, escopo, valor de negócio e critérios de aceitação de alto nível de um Épico, a partir da fonte completa e dos requisitos candidatos extraídos dela — roda **antes** de qualquer User Story ser gerada (ver `workflow/generate_epic.py::generate_epic_shape`), para que o Épico possa ser validado com o humano sem pagar o custo de gerar todas as stories primeiro.
- **Entrada**: `texto: str` (fonte completa), `requisitos: list[Requirement]` (já extraídos por `extract_requirements`).
- **Saída**: `dict` no formato `{"titulo", "objetivo", "escopo", "valor", "criterios_aceitacao": [...]}`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome os requisitos extraídos por `extract_requirements` — não depende de nenhuma User Story já gerada.

## validate_epic

- **Descrição**: valida se o Epic tem título, objetivo, escopo, valor e ao menos um critério de aceitação completo (equivalente de `validate_story`, em nível de Épico).
- **Entrada**: `epic: Epic`.
- **Saída**: `bool` — indica se o Épico passa no checklist automático (não decide aceitação humana).
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_epic_metadata`.

## review_epic

- **Descrição**: revisa o Epic com um segundo LLM, diferente do gerador, avaliando se objetivo/escopo/valor são claros e coerentes com as User Stories que ele agrupa — equivalente de `review_story` em nível de Épico.
- **Entrada**: `epic: Epic`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão (`OLLAMA_REVIEW_MODEL`, padrão `phi4`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_epic_metadata`, após `validate_epic` aprovar o checklist automático (ver `workflow/generate_epic.py:finalize_epic`).

## validate_traceability

- **Descrição**: verifica consistência entre os artefatos de um Epic — stories com objetivo duplicado, stories sem `benefit` (valor de negócio) associado, e requisitos extraídos que não viraram nenhuma story nem `unresolved_item` (órfãos).
- **Entrada**: `epic: Epic`.
- **Saída**: `dict` com `stories_duplicadas`, `stories_sem_valor`, `requisitos_orfaos`.
- **Efeitos colaterais**: nenhum — Python puro (comparação de texto/conjuntos), sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome `epic.requirements` (preenchido por `workflow/generate_epic.py`); usada pelo CLI (`run.py`) logo após a geração do Épico, antes do refinamento por story.

## export_markdown

- **Descrição**: exporta a User Story validada em formato Markdown para o caminho informado.
- **Entrada**: `story: UserStory`, `caminho: str`.
- **Saída**: `None`.
- **Efeitos colaterais**: escrita de arquivo em disco.
- **Erros esperados**: caminho inválido ou sem permissão de escrita; `story` não validada previamente.
- **Dependências**: consome a saída de `generate_story`/`validate_story`/`review_story`.

## update_jira_issue

- **Descrição**: persiste a versão final (aceita pelo usuário) de uma User Story de volta na descrição do ticket Jira de origem.
- **Entrada**: `issue_key: str`, `story: UserStory`.
- **Saída**: `None`.
- **Efeitos colaterais**: chamada HTTP `PUT` à API REST do Jira Cloud (`services/jira_service.py`, convertendo texto simples para ADF).
- **Erros esperados**: credenciais ausentes (`KeyError`); ticket inexistente ou sem permissão de escrita (erro HTTP via `httpx`).
- **Dependências**: chamada apenas após aceitação explícita do usuário no CLI (`run.py`), nunca automaticamente.

## create_jira_epic

- **Descrição**: cria um novo ticket do tipo Épico no Jira Cloud a partir de um `Epic` gerado e aceito pelo usuário, retornando a chave criada.
- **Entrada**: `epic: Epic`.
- **Saída**: `str` — chave do ticket criado (ex.: `AQUAQE-42`).
- **Efeitos colaterais**: chamada HTTP `POST` à API REST do Jira Cloud; requer `JIRA_PROJECT_KEY` e `JIRA_EPIC_ISSUE_TYPE_ID` no `.env` (específicos do projeto/instância — ver `create_jira_story`).
- **Erros esperados**: credenciais/config ausentes (`KeyError`); erro HTTP via `httpx` (ex.: tipo de issue inválido para o projeto).
- **Dependências**: chamada apenas após aceitação explícita do usuário no CLI (`run.py --criar-jira`), nunca automaticamente.

## create_jira_story

- **Descrição**: cria uma User Story como ticket filho (`parent`) de um Épico já criado no Jira Cloud, retornando a chave criada.
- **Entrada**: `story: UserStory`, `epic_key: str`.
- **Saída**: `str` — chave do ticket criado (ex.: `AQUAQE-43`).
- **Efeitos colaterais**: chamada HTTP `POST` à API REST do Jira Cloud; requer `JIRA_PROJECT_KEY` e `JIRA_STORY_ISSUE_TYPE_ID` no `.env`. Usa vínculo `parent` simples — assume projeto *team-managed* (não usa o campo "Epic Link" de projetos clássicos/*company-managed*).
- **Erros esperados**: credenciais/config ausentes (`KeyError`); erro HTTP via `httpx`.
- **Dependências**: chamada apenas após `create_jira_epic` retornar a chave do Épico pai; nunca automaticamente.

## generate_prd

- **Descrição**: gera um PRD completo (contexto/problema, objetivo, público-alvo, escopo, fora de escopo, requisitos funcionais e não funcionais, critérios de sucesso, riscos e premissas) a partir de uma ideia informal, conforme `../standards/prd_standard.md` — fecha o passo "Ideia → PRD" que antes não existia no agente (só se consumia um PRD já pronto).
- **Entrada**: `ideia: str` — descrição informal/crua da ideia.
- **Saída**: `PRDDraft` — sempre criado com `status = PENDING_CLARIFICATION`; o status final é decidido pelo workflow após `validate_prd`/`review_prd`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill; primeira etapa de `workflow/generate_prd.py::generate_prd_draft`.

## validate_prd

- **Descrição**: valida se o PRD tem contexto/problema, objetivo e escopo preenchidos, e ao menos um requisito funcional e um critério de sucesso.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `bool` — indica se o PRD passa no checklist automático (não decide aceitação humana).
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_prd`/`refine_prd`.

## review_prd

- **Descrição**: revisa o PRD com um segundo LLM, diferente do gerador, avaliando clareza e coerência entre objetivo, escopo e requisitos — equivalente de `review_story`/`review_epic` em nível de PRD.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão (`OLLAMA_REVIEW_MODEL`, padrão `phi4`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_prd`/`refine_prd`, após `validate_prd` aprovar o checklist automático (ver `workflow/generate_prd.py::finalize_prd`).

## generate_prd_clarifying_questions

- **Descrição**: transforma os `review_notes` de um PRD em perguntas diretas e acionáveis para quem propôs a ideia responder — mesmo papel de `generate_clarifying_questions`, em nível de PRD.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `list[str]` — lista de perguntas; vazia se o PRD não tiver `review_notes`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `review_notes`, preenchido por `review_prd`.

## refine_prd

- **Descrição**: reescreve os campos do PRD usando as respostas do usuário às perguntas de esclarecimento — não o LLM adivinhando sozinho a correção.
- **Entrada**: `draft: PRDDraft`, `respostas: list[dict]` (cada item: `{"pergunta": str, "resposta": str}`).
- **Saída**: `PRDDraft` — mesmo PRD, campos atualizados; `status`/`review_notes` só são recalculados pelo workflow (`workflow/generate_prd.py::refine_prd_draft`), que reaplica `validate_prd`/`review_prd`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome as perguntas de `generate_prd_clarifying_questions` e as respostas do usuário (coletadas no CLI, `run.py`).

## format_prd_markdown

- **Descrição**: formata o PRD em Markdown, seções conforme `../standards/prd_standard.md`. Usado tanto para exportação local (`--saida`) quanto como corpo da página do Confluence (`create_confluence_page`) — o texto resultante pode alimentar `extract_requirements`/`extract_prd_context`/`generate_epic_shape` normalmente, como qualquer outra fonte de entrada.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `str` — PRD formatado em Markdown.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_prd`/`refine_prd`, tipicamente após aceitação humana.

## create_confluence_page

- **Descrição**: publica o PRD aceito como uma nova página no Confluence Cloud, retornando a URL da página criada.
- **Entrada**: `draft: PRDDraft`, `titulo: str`.
- **Saída**: `str` — URL da página criada.
- **Efeitos colaterais**: chamada HTTP `POST` à API REST do Confluence Cloud (`services/confluence_service.py::create_page`); requer `CONFLUENCE_SPACE_KEY` no `.env` (além das credenciais do Jira, reaproveitadas).
- **Erros esperados**: credenciais/config ausentes (`KeyError`); erro HTTP via `httpx` (ex.: espaço inexistente ou sem permissão).
- **Dependências**: chamada apenas após aceitação explícita do usuário no CLI (`run.py --modo prd --publicar-confluence`), nunca automaticamente.
