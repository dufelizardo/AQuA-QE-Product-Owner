# Memory

> Estrutura conforme `../standards/memory_standard.md`. Decisão de produto: o agente usa memória de projeto e memória de longo prazo (não é stateless).

## Memória de sessão (curto prazo)

- **O que**: histórico da conversa/interação atual (mensagens trocadas, item em processamento no momento).
- **Onde**: contexto da execução corrente, não persistido além dela.
- **Quando é gravado**: a cada turno da interação.
- **Quando é lido**: durante toda a execução corrente.
- **Expiração**: descartada ao final da execução.

## Memória de projeto (médio prazo)

- **O que**: atores, objetivos e regras de negócio já identificados dentro do mesmo Epic; decisões de ambiguidade já esclarecidas pelo usuário para itens relacionados.
- **Onde**: associada ao Epic/projeto em processamento (ex.: junto aos artefatos gerados para aquele Epic).
- **Quando é gravado**: ao final de cada item processado com sucesso (`generate_story` + `validate_story` aprovados, ou esclarecimento recebido do usuário).
- **Quando é lido**: ao processar um novo item do mesmo Epic, para manter consistência de ator/regras já estabelecidos (ex.: não identificar o mesmo ator com nomes diferentes em histórias irmãs).
- **Expiração**: válida enquanto o Epic estiver em refinamento; não é reaproveitada em outro Epic/projeto sem revalidação.

## Memória de longo prazo (persistente entre sessões)

- **O que**: preferências de formato/estilo do Product Owner humano (ex.: nível de detalhe preferido nas explicações — ver `persona.md`), glossário consolidado reaproveitável entre projetos (distinto do glossário de domínio específico de um cliente) e — já implementado — respostas dadas pelo humano em ciclos de refinamento (Story/Epic), reaproveitáveis como sugestão editável quando uma pergunta parecida aparecer num ciclo futuro, do mesmo ou de outro projeto.
- **Onde**: armazenamento persistente da plataforma (implementação técnica a definir no System Design de implementação — fora do escopo deste documento). O caso de respostas de refinamento já está implementado concretamente via Qdrant embarcado (collection `refinement_answer_memory`) — ver `system_design.md` e `skills.md` (`record_refinement_answer`/`suggest_refinement_answer`).
- **Quando é gravado**: quando o usuário corrige ou confirma explicitamente uma preferência ou termo de glossário; para respostas de refinamento, imediatamente após cada resposta não vazia dada no ciclo (`run.py`), sem esperar aceitação final do artefato.
- **Quando é lido**: no início de cada nova sessão/projeto; para respostas de refinamento, a cada nova pergunta de esclarecimento gerada, antes do humano responder.
- **Expiração**: revisitada e substituível a qualquer momento por correção explícita do usuário; não expira automaticamente. Sugestões de refinamento nunca são aplicadas automaticamente — sempre exigem que o humano digite a resposta, mesmo com uma sugestão exibida.

## Relação com o manifesto do agente

O `agent_manifest.yaml` reflete esta decisão nas flags de memória (`vector`, `rag`) — ver atualização no próprio manifesto. `knowledge_graph` permanece `false`: não foi decidido adotar essa abordagem.

## Critérios de qualidade

- Nenhum dado é persistido sem um consumidor identificado nas seções acima (evita memória "por precaução" — ver `../standards/memory_standard.md`).
- O usuário deve poder corrigir ou solicitar a remoção de uma memória de longo prazo incorreta.
