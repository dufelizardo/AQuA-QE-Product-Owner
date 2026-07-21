# Padrão de AI Spec

> Estrutura padrão para a AI Spec (especificação de comportamento) de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/ai_spec.md`.

## Propósito

Enquanto o System Design descreve a arquitetura técnica, a AI Spec descreve **como o agente deve se comportar**: sua persona, seus objetivos, o que ele deve e não deve fazer diante de cada tipo de entrada. É a ponte entre o design do agente e as regras/prompt/skills que o implementam.

## Seções recomendadas

1. **Persona** — tom de voz, nível de formalidade, papel que o agente assume (ver `../agent/persona.md`).
2. **Objetivos** — o que o agente deve maximizar/entregar em cada interação (ver `../agent/objectives.md`).
3. **Entradas esperadas** — tipos e formatos de entrada que o agente deve saber tratar.
4. **Saídas esperadas** — formato e estrutura da saída (ver `../agent/output_schema.md`).
5. **Comportamentos esperados** — o que o agente deve fazer em cenários comuns (caminho feliz) e em cenários de exceção (entrada incompleta, ambígua, fora de escopo).
6. **Limites de conhecimento** — o que o agente pode assumir que sabe (via `knowledge/`) versus o que deve perguntar/sinalizar como desconhecido.
7. **Guardrails** — o que o agente nunca deve fazer, independentemente da entrada (ver `../agent/guardrails.md` e `rules_standard.md`).
8. **Padrões de aceitação** — exemplos de saída aceitável vs. inaceitável (ver `../agent/acceptance_patterns.md`).

## Critérios de qualidade

- Todo comportamento descrito deve ser **verificável** — deve existir uma forma de testar se o agente o segue (ver `evaluation_standard.md`).
- Ambiguidades de escopo devem ser resolvidas aqui, não deixadas para o prompt improvisar em produção.
- A AI Spec não descreve *implementação* (isso é papel de `rules_standard.md`, `skill_standard.md` e `prompt_standard.md`) — descreve *comportamento esperado observável*, no espírito do BDD (ver `../../knowledge/methodology/bdd.md`).
