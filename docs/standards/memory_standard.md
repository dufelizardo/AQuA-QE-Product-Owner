# Padrão de Memory

> Estrutura padrão para as decisões de Memory de um agente desta plataforma. Define o formato; o conteúdo deste agente fica em `../agent/memory.md`.

## Propósito

Memory define **o que persiste entre execuções do agente** (diferente de Context Engineering, que trata do que entra em uma única chamada). Sem memória, cada execução do agente começa do zero; com memória mal definida, o agente acumula estado desatualizado ou irrelevante.

## Tipos de memória a considerar

- **Memória de sessão (curto prazo)** — estado válido apenas durante uma interação/tarefa (ex.: histórico de mensagens da conversa atual).
- **Memória de projeto (médio prazo)** — decisões e contexto válidos enquanto se trabalha em um mesmo Epic/Feature (ex.: atores e regras de negócio já identificados).
- **Memória de longo prazo (persistente)** — conhecimento acumulado entre sessões (ex.: preferências de formato do Product Owner humano, glossário de domínio consolidado).

## Campos por tipo de memória

- **O que é armazenado** — estrutura e conteúdo do dado.
- **Onde é armazenado** — arquivo, banco vetorial, banco relacional, etc.
- **Quando é gravado** — evento que dispara a escrita.
- **Quando é lido** — em que ponto do fluxo a memória é consultada.
- **Política de expiração/invalidação** — quando o dado deixa de ser confiável e deve ser descartado ou revalidado.

## Critérios de qualidade

- Nenhum dado deve ser persistido sem um consumidor identificado (evitar memória "por precaução").
- Memória de longo prazo não deve conter informação que já é derivável de `knowledge/` ou do código — apenas o que foi efetivamente aprendido/decidido ao longo do uso.
- Deve haver uma forma explícita de o usuário corrigir ou apagar uma memória incorreta.
