# Context Engineering

> Estrutura conforme `../standards/context_engineering_standard.md`.

## Fontes de contexto

- **`knowledge/methodology/`** — sempre disponível; base para os critérios de qualidade (INVEST, DoR, DoD, Gherkin/BDD, ISO 29148) e para a estrutura Scrum.
- **`knowledge/domain/`** — quando o projeto/cliente já tiver conhecimento cadastrado (requisitos, regras de negócio, telas, glossário próprio); ausência não é erro, apenas contexto reduzido.
- **`knowledge/templates/`** — estrutura de saída (User Story, Epic, Feature, Acceptance Criteria, Business Rule, Task).
- **Memória de projeto e de longo prazo** (ver `memory.md`) — decisões e preferências acumuladas.
- **Saída de skills anteriores na mesma execução** — ex.: `extract_requirements` alimenta `identify_actor`/`identify_goal`/`identify_business_rules`, que alimentam `generate_story`.
- **`retrieve_chunks`** — mecanismo de busca sobre as fontes acima quando o volume de conhecimento exceder o que cabe diretamente no prompt.

## Critério de seleção

- Conhecimento de metodologia relevante à etapa atual é incluído por tipo de tarefa (ex.: INVEST e Gherkin sempre presentes ao gerar/validar uma história; DoR/DoD apenas quando relevante ao status do item).
- Conhecimento de domínio é selecionado por relevância à consulta (`retrieve_chunks`), não incluído por inteiro.
- Memória de projeto tem prioridade sobre memória de longo prazo quando ambas competem por espaço, por ser mais específica à tarefa atual.

## Orçamento de tokens

- Prioridade de alocação: (1) instruções fixas de persona/regras (`prompt.md`), (2) entrada do usuário/fonte sendo processada, (3) conhecimento recuperado (metodologia + domínio), (4) memória, (5) exemplos few-shot (`knowledge/examples/`, quando existirem).
- Em modo lote (Epic), o orçamento é gerenciado por item processado, não pela fonte inteira de uma vez, para evitar que um único documento grande estoure o contexto disponível.

## Ordenação no prompt final

1. Persona e objetivos.
2. Regras/guardrails.
3. Conhecimento de metodologia relevante.
4. Conhecimento de domínio recuperado (se houver).
5. Memória relevante.
6. Entrada do usuário/fonte a processar.
7. Formato de saída esperado.

## Atualização/invalidação

- Conhecimento de `knowledge/` é reconsultado a cada execução (não cacheado entre sessões diferentes).
- Memória de projeto é revalidada a cada novo item processado dentro do mesmo Epic; memória de longo prazo é revisitada no início de cada sessão.
