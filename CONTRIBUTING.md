# Guia de Contribuição

Obrigado por considerar contribuir com o **AQuA-QE Product Owner**! Antes de mais nada, vale a pena ler o `WHITEPAPER.md` (ou `WHITEPAPER.en.md`) e `docs/agent/` para entender o que o agente faz e por quê.

## Relatando problemas

- Confira as [issues existentes](https://github.com/dufelizardo/AQuA-QE-Product-Owner/issues) antes de abrir uma nova.
- Se for algo que parece uma lacuna conhecida, veja primeiro o [Project "Backlog"](https://github.com/users/dufelizardo/projects/3) — pode já estar lá, deliberadamente adiado até haver um consumidor real.
- Ao relatar um bug, inclua: passos para reproduzir, comportamento esperado vs. observado, modo usado (`--modo unitario/lote`), e o provedor de LLM ativo (`LLM_PROVIDER`, se diferente do padrão `ollama`).

## Propondo mudanças (Pull Requests)

- Para uma mudança grande, abra uma issue primeiro descrevendo o que pretende fazer.
- Prefira PRs pequenos e focados — evite misturar correção de bug com feature nova.
- **Este repositório não tem lint/type-check próprio** (`ruff`/`basedpyright` só existem na raiz do monorepo que originou este projeto) — não é preciso rodar nada disso aqui.
- Rode `uv sync` e depois `uv run pytest` antes de abrir o PR. A suíte inteira é mockada — nenhum teste faz chamada real a Ollama/Jira/Confluence/Qdrant; um PR que precise de rede real para passar não será aceito.
- Qualquer mudança numa skill geradora/revisora precisa preservar o ciclo `gerar → validar (checklist Python) → revisar (segundo LLM independente) → [refinar, humano-no-loop] → aceite humano explícito`. Nenhuma skill ou workflow pode setar `ArtifactStatus.ACCEPTED` sozinha — isso é sempre um ato humano no `run.py`.
- Mudanças que permitam a uma skill inventar dado fora da fonte de entrada, ou que contornem a revisão humana, são rejeitadas. O guardrail mais crítico deste agente é **GR-1** (nunca inventar) — ver `docs/agent/guardrails.md` para o conjunto completo (GR-1/GR-2/GR-3 cobrem invenção, histórias vagas/não testáveis, e regras de negócio omitidas).
- Se a mudança afeta comportamento observável, atualize também a documentação relevante: `docs/agent/*`, `README.md`/`README.pt.md`, `WHITEPAPER.md`/`WHITEPAPER.en.md`, e os diagramas em `docs/architecture/` (draw.io + SVG) se o fluxo mudou.

## Ambiente de desenvolvimento

```bash
# Python 3.12+ e uv já instalados
ollama pull mistral   # geração
ollama pull phi4      # revisor independente
ollama pull bge-m3    # embeddings (memória institucional de refinamento)

uv sync
cp .env.example .env  # preencha se for usar --jira/--confluence

uv run pytest
```

## Processo de Pull Request

1. Fork do repositório, branch a partir de `main`.
2. Faça a mudança, com testes cobrindo o novo comportamento.
3. `uv run pytest` localmente antes de abrir o PR.
4. Descreva a mudança no PR, referenciando a issue relacionada (ex. "Closes #12").
5. Aguarde a revisão — esteja aberto a ajustes, especialmente em torno dos guardrails.

## Onde encontrar mais

- [Wiki](https://github.com/dufelizardo/AQuA-QE-Product-Owner/wiki) — visão geral com links para tudo.
- [Discussions](https://github.com/dufelizardo/AQuA-QE-Product-Owner/discussions) — comece pelo post "Welcome"/mais recente.
- [Backlog project](https://github.com/users/dufelizardo/projects/3) — o que está deliberadamente fora desta fase.
