# Agent Design

> Ponte entre o System Design (arquitetura técnica) e a AI Spec/Rules (comportamento). Descreve como o agente decide, não apenas por onde os dados fluem.

## Pontos de decisão do agente

1. **Unitário vs. lote** — determinado pelo tipo de entrada/solicitação do usuário: uma pergunta pontual (ou requisito único) aciona o modo unitário; uma fonte completa (PRD inteiro, documento de requisitos) aciona o modo lote (Epic).
2. **Prosseguir vs. interromper por ambiguidade** — após `identify_actor`/`identify_goal`/`identify_business_rules`, o agente avalia se há informação suficiente para gerar uma história rastreável e testável. Se não houver, **interrompe e solicita esclarecimento** (não gera suposição silenciosa) — esta é a decisão de design mais importante do agente, derivada diretamente da guardrail nº 1 (ver `guardrails.md`).
3. **Aprovar automaticamente vs. exigir revisão humana** — o agente **nunca** decide aprovação final. `validate_story` decide apenas se a história passa no checklist automático (nível "rascunho validado"); a aprovação de negócio permanece sempre humana.
4. **Quando consultar `retrieve_chunks`** — sempre que a geração da história (`generate_story`) puder se beneficiar de conhecimento de domínio já registrado em `knowledge/domain/` ou de metodologia em `knowledge/methodology/`; não é uma etapa opcional ignorável, mas seu resultado pode vir vazio (fonte de domínio ainda não populada).

## Papel de cada camada nas decisões

- **AI Spec** (`ai_spec.md`) — descreve o comportamento esperado em cada ponto de decisão acima.
- **Rules** (`rules.md`) — tornam esses comportamentos verificáveis e aplicáveis (o "código de conduta" formal).
- **Skills** (`skills.md`) — implementam a capacidade técnica que cada decisão utiliza.

## Modelo de interação com o usuário

O agente é **colaborativo e consultivo**, não uma caixa-preta: ao interromper por ambiguidade, explica qual informação está faltando e por quê; ao entregar uma história, explica as decisões tomadas (ator/objetivo/regras identificados) para que o revisor humano valide rapidamente (ver `persona.md`).

## Fora do escopo do agente

Decisão de priorização do Product Backlog, condução de cerimônias Scrum e aprovação final de qualquer artefato — essas decisões permanecem com o Scrum Team humano (ver `../../knowledge/methodology/scrum_guide.md`).
