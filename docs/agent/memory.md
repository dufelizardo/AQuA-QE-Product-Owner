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

- **O que**: preferências de formato/estilo do Product Owner humano (ex.: nível de detalhe preferido nas explicações — ver `persona.md`) e glossário consolidado reaproveitável entre projetos (distinto do glossário de domínio específico de um cliente).
- **Onde**: armazenamento persistente da plataforma (implementação técnica a definir no System Design de implementação — fora do escopo deste documento).
- **Quando é gravado**: quando o usuário corrige ou confirma explicitamente uma preferência ou termo de glossário.
- **Quando é lido**: no início de cada nova sessão/projeto.
- **Expiração**: revisitada e substituível a qualquer momento por correção explícita do usuário; não expira automaticamente.

## Relação com o manifesto do agente

O `agent_manifest.yaml` reflete esta decisão nas flags de memória (`vector`, `rag`) — ver atualização no próprio manifesto. `knowledge_graph` permanece `false`: não foi decidido adotar essa abordagem.

## Critérios de qualidade

- Nenhum dado é persistido sem um consumidor identificado nas seções acima (evita memória "por precaução" — ver `../standards/memory_standard.md`).
- O usuário deve poder corrigir ou solicitar a remoção de uma memória de longo prazo incorreta.
