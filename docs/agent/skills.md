# Skills

> Documentação das skills implementadas em `../../src/aqua_qe_product_owner/skills/`, no formato definido em `../standards/skill_standard.md`. Ordem conforme `agent_manifest.yaml`. Tipos de entrada/saída referem-se às estruturas de `../../src/aqua_qe_product_owner/models/`.
>
> `extract_requirements`, `extract_prd_context`, `identify_epic_groups`, `identify_actor`, `identify_goal`, `identify_business_rules`, `identify_dependencies`, `generate_story`, `generate_clarifying_questions`, `refine_story`, `generate_epic_metadata`, `generate_epic_clarifying_questions` e `refine_epic_metadata` usam o LLM gerador ativo (`../../src/aqua_qe_product_owner/services/llm_service.py::generator_model()`; Ollama local por padrão, modelo configurável por `OLLAMA_MODEL`/padrão `mistral`, ou o piloto opcional NVIDIA NIM/Cerebras Inference/Google AI Studio via `LLM_PROVIDER=nvidia|cerebras|google`, ver `system_design.md`). `validate_story`, `validate_epic` e `diff_story_versions`/`diff_epic_versions`/`validate_traceability`/`generate_traceability_matrix`/`format_epic_markdown`/`parse_epic_markdown`/`parse_story_markdown` são Python puro, sem LLM (ver `evaluation.md`). `review_story` e `review_epic` usam o LLM revisor ativo (`llm_service.py::reviewer_model()`; Ollama `OLLAMA_REVIEW_MODEL`/padrão `phi4`, ou NVIDIA `NVIDIA_REVIEW_MODEL`/Cerebras `CEREBRAS_REVIEW_MODEL`/Google `GOOGLE_REVIEW_MODEL` sob o piloto), sempre diferente do gerador, como revisor independente (LLM-como-juiz). `retrieve_chunks`, `record_refinement_answer` e `suggest_refinement_answer` usam embedding local (`services/embedding_service.py`, modelo `bge-m3`) e um Qdrant embutido/local (`services/rag_service.py`, sem servidor externo) — `retrieve_chunks` sobre a collection `knowledge_methodology` (conteúdo estático), as outras duas sobre a collection separada `refinement_answer_memory` (memória institucional de respostas humanas de refinamento, ver `system_design.md`). `read_jira_issue`, `update_jira_issue`, `create_jira_epic`, `update_jira_epic` e `create_jira_story` usam a API REST do Jira Cloud (`services/jira_service.py`) — todas exceto `read_jira_issue` só são chamadas após aceitação humana explícita no CLI (`run.py`), nunca automaticamente. `read_confluence_page` usa a API REST do Confluence Cloud (`services/confluence_service.py`), reaproveitando as mesmas credenciais do Jira (mesma conta Atlassian) — leitura apenas; geração/edição/publicação de PRD (incluindo escrita no Confluence) passou a ser responsabilidade exclusiva do agente irmão AQuA-QE Product Manager.

## read_text_file

- **Descrição**: lê um arquivo de texto (`.txt` ou `.md`) e retorna seu conteúdo. Entrada via chat não passa por esta skill — passa por `parse_chat_transcript`/`format_chat_transcript` (ver abaixo).
- **Entrada**: `caminho: str` — caminho do arquivo `.txt` ou `.md`.
- **Saída**: `str` — conteúdo do arquivo.
- **Efeitos colaterais**: leitura de arquivo em disco.
- **Erros esperados**: arquivo inexistente, ilegível ou com encoding inválido.
- **Dependências**: nenhuma outra skill.

## parse_chat_transcript

- **Descrição**: separa uma transcrição de chat em mensagens por remetente (ex.: `"PO: ..."`, `"Dev: ..."`) — fecha a lacuna do tipo de entrada `chat`, que antes não tinha nenhuma skill própria (`run.py::_ler_entrada` só repassava o texto). O remetente é limitado a 1-3 palavras alfabéticas, para não confundir uma frase como `"O sistema deve responder em: 2 segundos"` com um remetente real. Linhas sem remetente reconhecível viram continuação da mensagem anterior. Se nenhuma linha tiver remetente identificável, retorna o texto inteiro como uma única mensagem sem remetente — comportamento idêntico ao de antes desta skill existir.
- **Entrada**: `texto: str` — texto bruto vindo de `--texto` (chat).
- **Saída**: `list[ChatMessage]` — uma ou mais mensagens, cada uma com `speaker`/`text`.
- **Efeitos colaterais**: nenhum — Python puro (regex), sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: nenhuma outra skill; usada por `run.py::_ler_entrada` só no caminho `--texto`, nunca em `--arquivo`/`--jira`/`--confluence`.

## format_chat_transcript

- **Descrição**: reconstrói uma transcrição normalizada (`"Remetente: mensagem"` por parágrafo) a partir das mensagens de `parse_chat_transcript`. Para o caso de uma única mensagem sem remetente (fallback de `parse_chat_transcript`, quando a entrada não é uma transcrição de verdade), retorna o texto original sem nenhuma alteração.
- **Entrada**: `mensagens: list[ChatMessage]`.
- **Saída**: `str` — transcrição normalizada (ou o texto original inalterado, no caso de mensagem única sem remetente).
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `parse_chat_transcript`; o texto resultante alimenta o resto do pipeline normalmente (`extract_requirements`, `identify_actor`, etc.), como qualquer outra fonte de entrada.

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

## record_refinement_answer

- **Descrição**: grava uma resposta que o humano deu a uma pergunta de esclarecimento num ciclo de refinamento (Story ou Epic), na collection `refinement_answer_memory` — memória institucional distinta de `knowledge_methodology`, para reaproveitamento futuro como sugestão (nunca aplicação automática) em ciclos de refinamento posteriores, do mesmo ou de outro artefato/projeto.
- **Entrada**: `pergunta: str`, `resposta: str`, `tipo_artefato: str` (`"story"` ou `"epic"`, gravado como metadado, não usado como filtro de busca).
- **Saída**: nenhuma (`None`).
- **Efeitos colaterais**: chamada ao serviço de embedding (`bge-m3`) e gravação no Qdrant local (`.data/qdrant/`); cria a collection `refinement_answer_memory` na primeira chamada, se ainda não existir.
- **Erros esperados**: nenhum — sempre grava; sem dedup (respostas repetidas geram pontos novos, mesmo padrão já aceito em `retrieve_chunks`/`index_knowledge`).
- **Dependências**: nenhuma outra skill. Chamada por `run.py` logo após cada `input()` de resposta nos dois ciclos de refinamento, só se a resposta não for vazia.

## suggest_refinement_answer

- **Descrição**: sugere a resposta de refinamento mais parecida já dada antes para uma pergunta de esclarecimento, buscando por similaridade semântica na collection `refinement_answer_memory`. Sugestão sempre editável — nunca aplicada automaticamente no artefato; o humano continua respondendo livremente no `input()`.
- **Entrada**: `pergunta: str`.
- **Saída**: `dict | None` — `{"pergunta": str, "resposta": str, "tipo_artefato": str, "score": float}` do resultado mais similar, ou `None` se a collection ainda não tiver nenhuma resposta registrada.
- **Efeitos colaterais**: chamada ao serviço de embedding (`bge-m3`) e consulta ao Qdrant local — nunca cria a collection nem indexa nada (diferente de `retrieve_chunks`, que indexa `knowledge/methodology/` sob demanda quando a collection não existe).
- **Erros esperados**: nenhum resultado disponível ainda (retorna `None`, não é um erro).
- **Dependências**: nenhuma outra skill. Sem gate de score mínimo — sempre retorna o top-1 se a collection tiver algum ponto, exibindo o score para o humano julgar a relevância.

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

## identify_dependencies

- **Descrição**: identifica dependências — outras histórias, sistemas ou decisões — mencionadas implícita ou explicitamente no texto. Fecha o gap entre o campo `UserStory.dependencies` (já declarado no schema, ver `output_schema.md`) e a implementação: antes desta skill, o campo nunca era preenchido por nenhuma skill.
- **Entrada**: `texto: str`.
- **Saída**: `list[str]` — dependências identificadas; lista vazia quando nenhuma é identificável no texto (mesmo tipo já usado por `PRDContext.dependencies` em `extract_prd_context`, sem `source_reference` individual por item).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: nenhuma dependência identificável no texto (retorna lista vazia); resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma outra skill (opera sobre o texto completo de entrada, mesmo padrão de `identify_business_rules`); ver `../../knowledge/templates/user_story.md`.

## generate_story

- **Descrição**: gera uma User Story a partir do ator, objetivo e contexto informados.
- **Entrada**: `ator: str`, `objetivo: str`, `contexto: dict` (chaves usadas: `business_rules: list[BusinessRule]`, `dependencies: list[str]`, `texto_fonte: str`, `id: str` opcional).
- **Saída**: `UserStory` — sempre criada com `status = PENDING_CLARIFICATION`; o status final é decidido pelo workflow após `validate_story` (ver `../../knowledge/templates/user_story.md`).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome as saídas de `identify_business_rules` e `identify_dependencies` e, opcionalmente, `retrieve_chunks`; `ator`/`objetivo` vêm de `identify_actor`/`identify_goal`.

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

## identify_epic_groups

- **Descrição**: agrupa os requisitos extraídos de um PRD em Épicos candidatos, por coerência temática — permite que um PRD com frentes distintas (ex.: "Agendamento" + "Notificações" + "Pagamento") vire múltiplos Épicos em vez de um só. Se os requisitos formarem um único produto coeso, retorna **um grupo só** — nunca força divisão que não exista no texto (GR-1). Usada por `workflow/generate_epic.py::generate_epics_shape`.
- **Entrada**: `texto: str` (fonte completa), `requisitos: list[Requirement]` (já extraídos por `extract_requirements`).
- **Saída**: `list[list[Requirement]]` — um ou mais grupos, cada um com os `Requirement` originais (não strings/IDs soltos).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: nenhum lançado — se a resposta do LLM não cobrir todos os requisitos exatamente uma vez (ID duplicado, ID inexistente, requisito faltando) ou vier malformada, a skill cai no fallback seguro de um único grupo com todos os requisitos, em vez de falhar ou perder rastreabilidade.
- **Dependências**: consome os requisitos extraídos por `extract_requirements`.

## generate_epic_metadata

- **Descrição**: define título, objetivo, escopo, valor de negócio e critérios de aceitação de alto nível de um Épico, a partir da fonte completa e dos requisitos candidatos de **um grupo** (ver `identify_epic_groups`) — roda **antes** de qualquer User Story ser gerada (ver `workflow/generate_epic.py::generate_epics_shape`), para que cada Épico candidato possa ser validado com o humano sem pagar o custo de gerar todas as stories primeiro.
- **Entrada**: `texto: str` (fonte completa), `requisitos: list[Requirement]` (um grupo de `identify_epic_groups`, ou todos os requisitos quando há um único Épico).
- **Saída**: `dict` no formato `{"titulo", "objetivo", "escopo", "valor", "criterios_aceitacao": [...]}`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome um grupo de requisitos de `identify_epic_groups` (ou a lista completa de `extract_requirements`, no caminho de um único Épico) — não depende de nenhuma User Story já gerada.

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

## generate_epic_clarifying_questions

- **Descrição**: gera perguntas de esclarecimento a partir dos apontamentos da revisão do Épico — mesmo papel de `generate_clarifying_questions`, em nível de Épico. Retorna lista vazia se `epic.review_notes` estiver vazio.
- **Entrada**: `epic: Epic`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `epic.review_notes`, produzido por `review_epic` (via `workflow/generate_epic.py:finalize_epic`).

## refine_epic_metadata

- **Descrição**: reescreve título, objetivo, escopo, valor e critérios de aceitação do Épico usando as respostas do usuário às perguntas de esclarecimento — mesmo papel de `refine_story`, em nível de Épico. Normaliza campos que o LLM às vezes devolve como lista em vez de string.
- **Entrada**: `epic: Epic`, `respostas: list[dict]` (cada item com `pergunta`/`resposta`).
- **Saída**: `Epic` — o mesmo objeto, com os campos reescritos.
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: chamada pelo ciclo de refinamento do CLI (`run.py::_ciclo_de_refinamento_epic`), reaplicando `validate_epic`/`review_epic` em seguida via `workflow/generate_epic.py:refine_epic_shape`.

## diff_epic_versions

- **Descrição**: compara duas versões de um Épico (antes/depois do refinamento) — critérios de aceitação novos/descontinuados (diff de conjunto, como `diff_story_versions`), e se objetivo/escopo/valor mudaram (comparação direta de texto, já que são campos escalares, não listas).
- **Entrada**: `antes: Epic`, `depois: Epic`.
- **Saída**: `dict` com `criterios_novos`, `criterios_descontinuados`, `objetivo_antes`/`objetivo_depois`, `escopo_antes`/`escopo_depois`, `valor_antes`/`valor_depois`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: usada pelo CLI (`run.py`) para gerar o changelog do Épico após um ciclo de refinamento.

## validate_traceability

- **Descrição**: verifica consistência entre os artefatos de um Epic — stories com objetivo duplicado, stories sem `benefit` (valor de negócio) associado, e requisitos extraídos que não viraram nenhuma story nem `unresolved_item` (órfãos).
- **Entrada**: `epic: Epic`.
- **Saída**: `dict` com `stories_duplicadas`, `stories_sem_valor`, `requisitos_orfaos`.
- **Efeitos colaterais**: nenhum — Python puro (comparação de texto/conjuntos), sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome `epic.requirements` (preenchido por `workflow/generate_epic.py`); usada pelo CLI (`run.py`) logo após a geração do Épico, antes do refinamento por story.

## generate_traceability_matrix

- **Descrição**: formata a Matriz de Rastreabilidade (RTM) do Epic em Markdown — tabela Requisito → Story → Critérios de Aceitação → Status, seguida da seção de inconsistências (reaproveita `validate_traceability`, não duplica a lógica de comparação). Escopo limitado a PRD-requisito → Épico → Story → Critério de Aceitação — as camadas Task/Código/Testes/Release não existem neste agente.
- **Entrada**: `epic: Epic`.
- **Saída**: `str` — RTM formatada em Markdown; requisitos sem story correspondente aparecem marcados como `(órfão)`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome `epic.requirements`/`epic.stories` e o resultado de `validate_traceability`; usada pelo CLI (`run.py --saida-rtm`, modo lote) após o export das User Stories do Épico.

## format_epic_markdown

- **Descrição**: formata o Epic (estágio *shape*: título/objetivo/escopo/valor/critérios de aceitação/requisitos) em Markdown, invertível por `parse_epic_markdown`. Não inclui `stories`, `prd_context`, `status` nem `review_notes`.
- **Entrada**: `epic: Epic`.
- **Saída**: `str` — Epic formatado em Markdown.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: nenhuma outra skill; usada pelo CLI (`run.py`) para exportar `<EPIC-ID>.md` junto das User Stories, sempre que `--saida` é informado.

## parse_epic_markdown

- **Descrição**: reconstrói um Epic (estágio *shape*) a partir do Markdown produzido por `format_epic_markdown`, preservando a redação original campo a campo — fecha a lacuna de não existir forma de carregar um Épico já pronto (só se gerava do zero a partir de um PRD). IDs de requisito/critério são regenerados sequencialmente, não preservados do arquivo.
- **Entrada**: `texto: str`.
- **Saída**: `Epic` — sem `stories` (o parser cobre só o estágio anterior a elas existirem).
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum (seções ausentes/malformadas resultam em campos vazios, mesmo padrão de robustez do resto do agente).
- **Dependências**: nenhuma outra skill; usada pelo CLI (`run.py --epic-existente`, modo lote) junto de `workflow/generate_epic.py::load_epic_shape`, no lugar de `generate_epics_shape`.

## parse_story_markdown

- **Descrição**: reconstrói uma `UserStory` a partir do Markdown produzido por `export_markdown`, preservando a redação original campo a campo — fecha a mesma lacuna do Épico, mas aqui o exportador (`export_markdown`) já existia, só faltava o parser inverso. `status`/`review_notes` não são restaurados do arquivo (ficam para `finalize_story` recalcular); IDs de critério de aceitação são regenerados sequencialmente; `source_reference` de cada regra de negócio usa o `source_reference` da própria story como fallback, já que `export_markdown` não exporta a origem de cada regra individualmente.
- **Entrada**: `texto: str`.
- **Saída**: `UserStory`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum (seções ausentes/malformadas resultam em campos vazios).
- **Dependências**: nenhuma outra skill; usada pelo CLI (`run.py --story-existente`, modo unitário) junto de `workflow/generate_user_story.py::finalize_story`, no lugar de `generate_user_story`.

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

## update_jira_epic

- **Descrição**: persiste a versão final (aceita pelo usuário) de um Épico de volta na descrição do ticket Jira de origem — equivalente de `update_jira_issue` em nível de Épico. Reaproveita `epic_para_texto` (definida em `create_jira_epic`) para formatar o corpo.
- **Entrada**: `issue_key: str`, `epic: Epic`.
- **Saída**: `None`.
- **Efeitos colaterais**: chamada HTTP `PUT` à API REST do Jira Cloud (`services/jira_service.py`, convertendo texto simples para ADF).
- **Erros esperados**: credenciais ausentes (`KeyError`); ticket inexistente ou sem permissão de escrita (erro HTTP via `httpx`).
- **Dependências**: chamada apenas após aceitação explícita do usuário no CLI (`run.py --modo lote --jira <chave>`, quando o lote gera exatamente 1 Épico — evita sobrescrever o mesmo ticket com o conteúdo de Épicos diferentes quando o PRD se divide em N grupos), nunca automaticamente.

## create_jira_story

- **Descrição**: cria uma User Story como ticket filho (`parent`) de um Épico já criado no Jira Cloud, retornando a chave criada.
- **Entrada**: `story: UserStory`, `epic_key: str`.
- **Saída**: `str` — chave do ticket criado (ex.: `AQUAQE-43`).
- **Efeitos colaterais**: chamada HTTP `POST` à API REST do Jira Cloud; requer `JIRA_PROJECT_KEY` e `JIRA_STORY_ISSUE_TYPE_ID` no `.env`. Usa vínculo `parent` simples — assume projeto *team-managed* (não usa o campo "Epic Link" de projetos clássicos/*company-managed*).
- **Erros esperados**: credenciais/config ausentes (`KeyError`); erro HTTP via `httpx`.
- **Dependências**: chamada apenas após `create_jira_epic` retornar a chave do Épico pai; nunca automaticamente.

