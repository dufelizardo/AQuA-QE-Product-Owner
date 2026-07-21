# Padrão de Prompt

> Estrutura padrão para o(s) prompt(s) de sistema de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/prompt.md`.

## Propósito

O prompt é onde a AI Spec, as Rules e a persona se materializam em texto efetivamente enviado ao LLM. É a camada de implementação mais próxima do modelo — deve ser derivada dos demais documentos, não a fonte original de decisões de comportamento.

## Seções recomendadas de um prompt de sistema

1. **Papel/persona** — quem o agente é (ver `../agent/persona.md`).
2. **Objetivo da tarefa** — o que o agente deve produzir nesta interação.
3. **Instruções de comportamento** — derivadas da AI Spec e das Rules (ver `ai_spec_standard.md`, `rules_standard.md`); evitar duplicar texto, preferir referenciar a fonte.
4. **Formato de saída** — estrutura esperada da resposta (ver `../agent/output_schema.md`).
5. **Exemplos (few-shot)** — quando necessário, extraídos de `knowledge/examples/`.
6. **Restrições/guardrails** — o que nunca deve ser feito, reforçado explicitamente no prompt.

## Convenções

- Cada versão do prompt deve ser identificável (ex.: comentário de versão no topo do arquivo), para permitir comparar comportamento entre versões durante avaliação.
- Instruções devem ser objetivas e testáveis — evitar linguagem vaga ("seja proativo", "use bom senso") sem critério de verificação associado.
- Alterações no prompt que mudem comportamento observável devem ser acompanhadas de atualização nos casos de avaliação (ver `evaluation_standard.md`).

## Critérios de qualidade

- Nenhuma instrução no prompt deve contradizer a AI Spec ou as Rules — o prompt é a implementação, não a fonte da verdade.
- O prompt deve ser o mais curto possível para cumprir seu objetivo (cada instrução extra consome orçamento de contexto, ver `context_engineering_standard.md`).
