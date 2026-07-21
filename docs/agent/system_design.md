# System Design

> Estrutura conforme `../standards/system_design_standard.md`.

## Visão geral da arquitetura

O agente é um pipeline de skills orquestrado sequencialmente, com dois pontos de checagem antes de qualquer saída ser considerada válida: validação automática (INVEST/DoR) e revisão humana obrigatória. Não há aprovação automática — ver `guardrails.md`.

```
Entrada (.txt/Markdown/chat/Jira)
   → read_text_file (se entrada for arquivo .txt/.md; chat e Jira entram como texto direto)
   → extract_requirements
   → retrieve_chunks (conhecimento de apoio: metodologia + domínio, quando existir)
   → identify_actor / identify_goal / identify_business_rules
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

## Modos de operação

- **Unitário** — uma User Story por vez, com possibilidade de interação próxima do usuário a cada etapa.
- **Lote (Epic)** — processa a fonte inteira e gera um conjunto de User Stories de uma vez; ambíguidades pontuais em itens individuais não interrompem o lote inteiro, mas são sinalizadas item a item.

## Restrições técnicas

- Modelo(s) de LLM e limites de contexto/custo a definir na implementação (fora do escopo deste documento de design).
- Uma camada `services/` (abstração sobre providers externos — LLM, embeddings, vector store, Jira) será introduzida incrementalmente, um serviço por vez, junto com a skill que primeiro precisar dele — não construída antecipadamente sem consumidor.

## Observabilidade

- Cada execução deve registrar: fonte de entrada, requisitos extraídos, decisões de ator/objetivo/regra, resultado do checklist automático e se houve interrupção por ambiguidade — necessário para auditar rastreabilidade (ver `guardrails.md`) e para os casos de teste de `evaluation.md`.
