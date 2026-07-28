# System Design

> Estrutura conforme `../standards/system_design_standard.md`.

## Visão geral da arquitetura

O agente é um pipeline de skills orquestrado sequencialmente, com dois pontos de checagem antes de qualquer saída ser considerada válida: validação automática (INVEST/DoR) e revisão humana obrigatória. Não há aprovação automática — ver `guardrails.md`.

```
Entrada (.txt/Markdown/chat/Jira)
   → read_text_file (se entrada for arquivo .txt/.md; chat e Jira entram como texto direto)
   → extract_requirements
   → retrieve_chunks (conhecimento de apoio: metodologia + domínio, quando existir)
   → identify_actor / identify_goal / identify_business_rules / identify_dependencies
   → generate_story
   → validate_story (checklist automático)
   → [ambíguo/incompleto?] → parar e solicitar esclarecimento ao usuário
   → export_markdown
   → revisão humana obrigatória (fora do agente, pelo PO)
```

## Componentes

- **Orquestrador/Agente** — decide a sequência de skills a chamar (ordem fixa do `agent_manifest.yaml`) e decide quando interromper o fluxo por ambiguidade (ver `agent_design.md`). Implementado em `../../src/aqua_qe_product_owner/orchestrator/product_owner.py`.
- **Workflows** — orquestração da sequência de skills por caso de uso (User Story unitária, Epic em lote, geração/complemento de critérios de aceitação), implementados em `../../src/aqua_qe_product_owner/workflow/`.
- **Skills** — funções descritas em `skills.md`, implementadas em `../../src/aqua_qe_product_owner/skills/`.
- **Modelos de dados** — estruturas (`UserStory`, `Epic`, `AcceptanceCriteria`, `BusinessRule`, `Actor`, `Requirement`) implementadas em `../../src/aqua_qe_product_owner/models/`, conforme `output_schema.md`.
- **Fontes de conhecimento** — `knowledge/methodology/` (sempre disponível) e `knowledge/domain/` (quando o projeto/cliente tiver conhecimento próprio cadastrado), consumidas via `retrieve_chunks` e Context Engineering (ver `context_engineering.md`).
- **Memória** — camada de projeto (decisões dentro do Epic atual) e de longo prazo (preferências e glossário consolidado entre sessões) — ver `memory.md`.
- **Interfaces externas** — entrada: arquivo `.txt`/Markdown, texto de chat ou ticket Jira; saída: arquivo Markdown exportado (`export_markdown`), consumível pelo Product Backlog/Jira.

## Fluxo de dados

1. A entrada é normalizada em texto (`read_text_file` quando for arquivo `.txt`/Markdown; passagem direta quando for chat ou Jira).
2. Requisitos candidatos são extraídos (`extract_requirements`).
3. Para cada requisito (ou lote, em modo Epic), o agente identifica ator, objetivo e regras de negócio.
4. `generate_story` produz a User Story estruturada (ver `output_schema.md`), usando também contexto recuperado por `retrieve_chunks` quando relevante.
5. `validate_story` aplica o checklist automático (`validation_checklist.md`); se reprovar por informação faltante/ambígua, o agente interrompe e solicita esclarecimento em vez de prosseguir.
6. Se aprovada no checklist automático, a história é exportada (`export_markdown`) em estado de **rascunho validado** — não aprovado.
7. A aprovação final é um passo humano, fora da responsabilidade do agente.
8. Opcionalmente, após o aceite (`--priorizar`), o usuário é perguntado a prioridade de cada história (Alta/Média/Baixa) — decisão sempre humana, nunca sugerida pelo agente (ver `dor.md`/`scrum_guide.md`, que atribuem ordenação do backlog ao PO e estimativa ao time). Em modo lote, opcionalmente (`--saida-rtm`) a Matriz de Rastreabilidade do Épico (`generate_traceability_matrix`) é exportada junto das User Stories.

## Modos de operação

- **Unitário** — uma User Story por vez, com possibilidade de interação próxima do usuário a cada etapa. Caso especial (`--story-existente`): `parse_story_markdown` carrega uma User Story `.md` já exportada (`export_markdown`), preservando a redação original campo a campo, e `finalize_story` (já existente, mesmo usado por `generate_user_story`) decide o status — entra direto no ciclo normal de refinamento/aceite, sem nenhuma outra mudança de fluxo.
- **Lote (Epic)** — processa a fonte inteira e gera um conjunto de User Stories de uma vez; ambíguidades pontuais em itens individuais não interrompem o lote inteiro, mas são sinalizadas item a item. Caso especial (`--epic-existente`): em vez de gerar o Épico a partir de um PRD, `parse_epic_markdown` carrega um Épico `.md` já exportado (`format_epic_markdown`), preservando a redação original campo a campo, e `load_epic_shape` aplica o checklist automático — entra direto no mesmo menu de recepção (gerar as stories agora / refinar / descartar), sem nenhuma outra mudança de fluxo.

## Restrições técnicas

- Modelo(s) de LLM e limites de contexto/custo a definir na implementação (fora do escopo deste documento de design).
- Uma camada `services/` (abstração sobre providers externos — LLM, embeddings, vector store, Jira) será introduzida incrementalmente, um serviço por vez, junto com a skill que primeiro precisar dele — não construída antecipadamente sem consumidor.
- Dois LLMs locais via Ollama por padrão (`OLLAMA_MODEL` gerador, `OLLAMA_REVIEW_MODEL` revisor) — mesma convenção de PM/SA.
- **Piloto de provedor alternativo via toggle** (`LLM_PROVIDER=ollama|nvidia|cerebras|google`, padrão `ollama`): `llm_service.py::generator_model()`/`reviewer_model()` resolvem o modelo certo conforme o provedor ativo; `complete`/`complete_json` mantêm assinatura inalterada. Portado dos agentes irmãos AQuA-QE Product Manager/Solution Architect, já validados ao vivo lá antes de chegar aqui — NVIDIA NIM (`deepseek-ai/deepseek-v4-pro` gerador, `meta/llama-3.3-70b-instruct` revisor, mas instável em testes ao vivo: 503 de capacidade, 404 de entitlement), Cerebras Inference (`gpt-oss-120b` gerador, `zai-glm-4.7` revisor, rápido mas testado com erro 402 de billing/quota pendente) e Google AI Studio (`gemini-3.1-flash-lite` gerador, `gemini-2.5-flash-lite` revisor — único provedor validado ao vivo de ponta a ponta com sucesso nos agentes irmãos, adotado aqui como default direto, pulando o `gemini-3.5-flash` inicial que esgotava a quota gratuita de 20 req/dia). Todos os três provedores em nuvem usam o SDK `openai` contra endpoint compatível com OpenAI. Não afeta embeddings — `embedding_service.py`/`bge-m3` continuam sempre Ollama.
- **`rag_service.py` hospeda duas collections Qdrant independentes** no mesmo storage embarcado (`.data/qdrant/`): `knowledge_methodology` (conteúdo estático de `knowledge/methodology/`, indexado sob demanda por `search`/`retrieve_chunks`) e `refinement_answer_memory` (memória institucional de respostas humanas de ciclos de refinamento reais, gravada por `record_refinement_answer` e consultada por `find_similar_refinement_answers`/`suggest_refinement_answer` — issue [#12](https://github.com/dufelizardo/AQuA-QE-Product-Owner/issues/12)). Compartilham o mesmo `_client()`/`embed()`, mas são semanticamente distintas: uma é base de metodologia, a outra é histórico de decisões humanas reutilizável entre projetos. Qdrant embarcado suporta múltiplas collections sob o mesmo path sem conflito de lock, desde que os clients não fiquem abertos simultaneamente (padrão já usado — cada função cria um client novo e descartável por chamada).

## Observabilidade

- Cada execução deve registrar: fonte de entrada, requisitos extraídos, decisões de ator/objetivo/regra, resultado do checklist automático e se houve interrupção por ambiguidade — necessário para auditar rastreabilidade (ver `guardrails.md`) e para os casos de teste de `evaluation.md`.
