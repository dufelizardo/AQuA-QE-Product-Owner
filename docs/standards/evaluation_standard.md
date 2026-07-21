# Padrão de Evaluation

> Estrutura padrão para a Evaluation (avaliação de qualidade) de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/evaluation.md`.

## Propósito

Evaluation define **como se mede se o agente está fazendo o que deveria** — fecha o ciclo com o PRD (métricas de sucesso) e com a AI Spec/Rules (comportamentos esperados), tornando-os verificáveis na prática, não apenas na especificação.

## Seções recomendadas

1. **Métricas** — o que é medido (ex.: aderência a INVEST, cobertura de critérios de aceitação gerados, taxa de alucinação de requisitos não presentes na fonte).
2. **Casos de teste** — conjunto de entradas representativas (caminho feliz, casos de borda, entradas ambíguas ou incompletas) com saída esperada ou critério de aceitação.
3. **Método de avaliação** — automático (assertions, comparação estruturada), por LLM-como-juiz, ou revisão humana — e quando cada um se aplica.
4. **Frequência** — quando a avaliação roda (a cada mudança de prompt/regra, periodicamente, antes de release).
5. **Critério de aprovação** — limiar mínimo para considerar uma versão do agente apta a substituir a anterior.
6. **Registro de regressões** — como falhas encontradas viram novos casos de teste permanentes.

## Critérios de qualidade

- Toda regra (`rules_standard.md`) e todo comportamento da AI Spec (`ai_spec_standard.md`) deveriam ter pelo menos um caso de avaliação associado — comportamento sem forma de verificação é, na prática, não especificado.
- Casos de teste devem ser determinísticos o suficiente para permitir comparação entre versões do agente ao longo do tempo.
- A avaliação deve refletir as métricas de sucesso definidas no PRD (`prd_standard.md`), não apenas aspectos fáceis de medir.
