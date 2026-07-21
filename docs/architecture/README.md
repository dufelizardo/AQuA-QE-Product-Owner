# Diagramas de arquitetura

Representação visual da arquitetura e dos fluxos do agente, complementando a documentação em prosa de `../agent/system_design.md`, `../agent/agent_design.md`, `../agent/skills.md` e `../../WHITEPAPER.md`.

- **Fonte editável**: [`architecture.drawio`](architecture.drawio) — arquivo único, 6 páginas, abra em [app.diagrams.net](https://app.diagrams.net) ou na extensão "Draw.io Integration" do VS Code.
- **Espelho estático**: `svg/*.svg` — mesmo conteúdo de cada página, visível diretamente aqui no GitHub/VS Code, sem precisar abrir o draw.io.

## 1 — Arquitetura em camadas

![Arquitetura em camadas](svg/01-arquitetura-camadas.svg)

Da entrada (`.txt`/Markdown/chat/Jira/Confluence) até os sistemas externos, passando por CLI, orquestrador, workflows, skills, models e services. Detalhe textual em `../agent/system_design.md`.

## 2 — Fluxo modo unitário

![Fluxo modo unitário](svg/02-fluxo-modo-unitario.svg)

Pipeline de uma única User Story: `Generate → Validate → Review → Refine → Approve`, com os dois pontos de checagem (checklist automático e revisor independente) antes de qualquer aceite humano. Detalhe textual em `../agent/system_design.md` e `../agent/rules.md`.

## 3 — Fluxo modo lote (Épico)

![Fluxo modo lote (Épico)](svg/03-fluxo-modo-lote-epico.svg)

Em duas fases: primeiro `extract_prd_context` (visão, requisitos não funcionais, riscos, critérios de sucesso, restrições, dependências) + `identify_epic_groups` (agrupa os requisitos por coerência temática — um PRD coeso vira um único Épico, um PRD com frentes distintas pode virar vários) + `generate_epic_metadata`/`validate_epic` por grupo definem cada Épico candidato só a partir do texto e dos requisitos do seu grupo — **sem nenhuma story ainda** — e o usuário decide se quer continuar (uma pergunta cobrindo todos os Épicos identificados); só depois o mesmo pipeline do Diagrama 2 é aplicado a cada requisito de cada Épico, seguido de `validate_traceability` e `review_epic` (agora com as stories existentes, para avaliar coerência real), um Épico de cada vez.

## 4 — Ciclo de refinamento humano-no-loop

![Ciclo de refinamento humano-no-loop](svg/04-ciclo-refinamento-humano.svg)

O diferencial do projeto: quando a revisão reprova, o agente gera perguntas objetivas para um humano responder — não tenta se autocorrigir sozinho. Ver seção 6 do `../../WHITEPAPER.md`.

## 5 — Integrações externas

![Integrações externas](svg/05-integracoes-externas.svg)

Ollama local (`mistral`/`phi4`/`bge-m3`), Qdrant embarcado, Jira Cloud e Confluence Cloud, e qual módulo de `services/` fala com cada um.

## 6 — Ideia para PRD e Confluence

![Ideia para PRD e Confluence](svg/06-ideia-para-prd-confluence.svg)

O passo "Ideia → PRD" que faltava: `generate_prd` → `validate_prd` → `review_prd`, com o mesmo ciclo de refinamento humano-no-loop do Diagrama 4 (`generate_prd_clarifying_questions`/`refine_prd`). Uma vez aceito, `format_prd_markdown` produz o texto final, que pode ser exportado, publicado como página no Confluence (`create_confluence_page`) e/ou virar a entrada do Diagrama 3 (gerar o Épico a partir do PRD recém-criado).

## Mantendo `.drawio` e `.svg` sincronizados

`architecture.drawio` é a fonte editável; os `.svg` em `svg/` foram gerados como um espelho fiel de cada página, para renderizar direto no GitHub sem exigir o app do draw.io (não há CLI/app do draw.io instalado na máquina onde este diretório foi criado). Se você editar o `.drawio` no app.diagrams.net, reexporte os SVGs por lá (`File → Export as → SVG`, uma página por vez) e substitua os arquivos correspondentes em `svg/` para manter os dois em sincronia.
