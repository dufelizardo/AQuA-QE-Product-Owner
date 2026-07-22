# AQuA-QE Product Owner

> Also available in [Portuguese](README.pt.md).

Agent that generates User Stories, Epics and Acceptance Criteria from PRDs, requirement documents and other input sources — following the agent engineering flow:

```
PRD → System Design → Agent Design → AI Specs/Rules/Skills → Context Engineering → Memory/MCP → Agents → Outputs
```

## Structure

- **`docs/standards/`** — platform standards (how to write an AI Spec, a Rule, a PRD, etc.). Change rarely.
- **`docs/agent/`** — this agent's full specification: PRD, System Design, Agent Design, AI Spec, Rules, Persona, Objectives, Output Schema, Guardrails, Evaluation, Prompt, and `agent_manifest.yaml` (the agent manifest — inputs, outputs, skills, memory, rules).
- **`knowledge/domain/`** — domain/client-specific knowledge (requirements, business rules, processes, screens, API, database, glossary).
- **`knowledge/methodology/`** — methodological material that guides the agent (Scrum Guide, BABOK, ISO 29148, INVEST, DoR, DoD, BDD, Gherkin).
- **`knowledge/templates/`** — pure structure, no knowledge (templates for User Story, Epic, Feature, Acceptance Criteria, Business Rule, Task).
- **`knowledge/examples/`** — few-shot examples (good and bad examples, by category).
- **`knowledge/glossary/`** and **`knowledge/regulations/`** — general glossary and regulations applicable to the platform.
- **`src/aqua_qe_product_owner/skills/`** — the agent's skills in Python (generate/validate/review/refine a PRD from an idea, read text file, parse/format a chat transcript, read a Jira issue, retrieve chunks, extract requirements, extract PRD context, identify actor/goal/rules, generate/validate/review/refine the story, generate Epic metadata, diff story versions, export to Markdown, update/create Jira issues, create a Confluence page).
- **`src/aqua_qe_product_owner/models/`** — the agent's data structures (User Story, Epic, Acceptance Criteria, Business Rule, Actor, Requirement, PRDContext, PRDDraft).
- **`src/aqua_qe_product_owner/workflow/`** — orchestration of the skill sequence per use case (generate a single User Story, generate a batch Epic, generate/complement acceptance criteria).
- **`src/aqua_qe_product_owner/orchestrator/`** — single entry point that decides which workflow to run.
- **`src/aqua_qe_product_owner/services/`** — external integrations: `llm_service` (local Ollama, generation), `embedding_service` (local Ollama, `bge-m3`), `rag_service` (embedded/local Qdrant, no server) and `jira_service` (Jira Cloud REST API).

## Setup

This is a standalone repository (not part of any monorepo) — `uv sync` here resolves and installs its own dependencies.

1. Install [Python 3.12+](https://www.python.org/) and [uv](https://docs.astral.sh/uv/).
2. Install [Ollama](https://ollama.com) and pull the three local models this agent uses:
   ```bash
   ollama pull mistral   # generation
   ollama pull phi4      # independent reviewer
   ollama pull bge-m3    # embeddings
   ```
3. Clone this repo and install dependencies:
   ```bash
   git clone https://github.com/dufelizardo/AQuA-QE-Product-Owner.git
   cd AQuA-QE-Product-Owner
   uv sync
   ```
4. Copy `.env.example` to `.env` and fill in the values you need (Ollama works with the defaults; Jira/Confluence credentials are only required for `--jira`, `--confluence` and `--criar-jira`):
   ```bash
   cp .env.example .env
   ```
5. Run the test suite (fully mocked, no live Ollama/Jira/Confluence calls) to confirm the setup:
   ```bash
   uv run pytest
   ```

## Usage

```bash
# Generate a PRD from an informal idea, with the interactive refinement loop
uv run python run.py --modo prd --texto "Customers should be able to open a CDB from the app" --refinar --saida prd.md

# Generate a PRD and publish it as a new Confluence page
uv run python run.py --modo prd --arquivo idea.txt --refinar --publicar-confluence

# A single User Story from a .txt/.md file
uv run python run.py --modo unitario --arquivo requirement.txt --saida story.md

# A single User Story from raw text (chat)
uv run python run.py --modo unitario --texto "As a customer, I want..." --saida story.md

# A single User Story from a Jira Cloud issue
uv run python run.py --modo unitario --jira PROJ-123 --saida story.md

# An Epic (batch) from a larger source, exporting each story
uv run python run.py --modo lote --arquivo prd.txt --saida epic_output/

# With the interactive refinement loop (questions, final acceptance, changelog, Jira write-back)
uv run python run.py --modo unitario --jira PROJ-123 --saida story.md --refinar

# Generate a full Epic and create it in Jira (with the stories as child tickets)
uv run python run.py --modo lote --arquivo prd.txt --saida epic_output/ --criar-jira

# An Epic from a Confluence Cloud page (PRD)
uv run python run.py --modo lote --confluence "https://your-site.atlassian.net/wiki/.../pages/163841/..." --criar-jira
```

`--saida` is optional in both modes (without it, the result is only printed to the terminal). To use `--jira`, fill in `JIRA_BASE_URL`, `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.env` (the token is generated at `id.atlassian.com/manage-profile/security/api-tokens`).

`--refinar` turns on the interactive loop: if the story isn't approved, the agent turns the review's concerns into clarifying questions, you answer them in the terminal, and those answers become real grounding to rewrite the story (instead of the LLM guessing the fix on its own). At the end, a prompt asks whether you accept the story; if so, a changelog is generated (new vs. discontinued rules/criteria, printed and saved to `<saida>.changelog.md`) and, if the input came from `--jira`, you're asked whether to persist the final version back to the ticket.

Batch mode (`--modo lote`) always stops right after defining the Epic (title, objective, scope, value, acceptance criteria) to ask whether to continue — before generating any User Story, so a wrong-scoped Epic doesn't cost a full batch of story generation.

`--criar-jira` (batch mode only), after the Epic and its User Stories are generated and an explicit acceptance prompt, creates the Epic ticket in Jira (`JIRA_PROJECT_KEY`, `JIRA_EPIC_ISSUE_TYPE_ID`) and each User Story as a child ticket (`JIRA_STORY_ISSUE_TYPE_ID`, simple `parent` link — assumes a *team-managed* project), returning the created keys.

`--modo prd` generates a full PRD from an informal idea (`--arquivo`/`--texto`), goes through the same INVEST/DoR-equivalent validation, independent review and interactive refinement loop as a User Story, and — once explicitly accepted — can be exported (`--saida`), published as a new Confluence page (`--publicar-confluence`, requires `CONFLUENCE_SPACE_KEY`), and/or become the input for batch mode (the CLI asks whether to continue and generate the Epic from it). See `run.py --help` for all options.

## Status

`docs/agent/`, `docs/standards/` and `knowledge/` (except `domain/`, `regulations/` and `examples/`, which depend on a real client/project) are filled in with real content.

In `src/`, all 33 skills and the four workflows are implemented and work end to end with local models via Ollama:

- **PRD mode** (`workflow/generate_prd.py`, via `run.py --modo prd`) — the "Idea → PRD" step: `generate_prd` (LLM `mistral`) writes a full PRD from an informal idea (context/problem, objective, target audience, scope, out-of-scope, functional/non-functional requirements, success criteria, risks — per `docs/standards/prd_standard.md`), `validate_prd` (pure Python checklist) → `review_prd` (reviewer LLM `phi4`) → the same interactive refinement loop as User Story (`generate_prd_clarifying_questions` + `refine_prd`) → explicit human acceptance. Once accepted, `format_prd_markdown` produces the final text, which can be exported, published to Confluence (`create_confluence_page`, via `--publicar-confluence`), and/or feed directly into batch mode.
- **Single-story mode** (`workflow/generate_user_story.py`) — `read_text_file` → `extract_requirements` → `identify_actor`/`identify_goal`/`identify_business_rules` → `generate_story` (LLM `mistral`) → `validate_story` (pure Python checklist) → `review_story` (reviewer LLM `phi4`, independent from the generator) → final status. For `chat` input specifically, `parse_chat_transcript`/`format_chat_transcript` (pure Python, no LLM) normalize a multi-speaker transcript (`"PO: ...\nDev: ..."`) into `"Speaker: message"` paragraphs before any of this runs; plain-text input with no identifiable speaker passes through unchanged.
- **Batch mode** (`workflow/generate_epic.py`) — in two phases: `generate_epics_shape` extracts the requirements, extracts the PRD's non-functional context (`extract_prd_context` — vision, non-functional requirements, constraints, success criteria, risks, dependencies, kept in `epic.prd_context`), groups the requirements by thematic coherence (`identify_epic_groups` — a cohesive PRD stays a single group; a PRD covering distinct fronts can split into several, with a safe single-group fallback if the LLM's grouping is inconsistent), and defines each candidate Epic's title, objective, scope, value and high-level acceptance criteria from the source text alone (no story generated yet), then `validate_epic` runs the automatic checklist for each — this is the point where `run.py --modo lote` asks whether to continue (one combined question covering every Epic identified), before paying the cost of generating any story. Only after confirmation does `generate_epics_stories` apply the single-story pipeline to each extracted requirement, per Epic (ambiguous items become `unresolved_items` without blocking the rest of the batch), then run `validate_traceability` (duplicated stories, stories with no business value, orphan requirements) and `review_epic` (reviewer LLM `phi4`, now able to judge coherence against the stories it groups) for each Epic in turn.
- **Acceptance criteria complement** (`workflow/generate_acceptance.py`) — generates additional acceptance criteria for an existing User Story and reapplies `validate_story`/`review_story`.
- **Interactive refinement** (`workflow/refine_story.py`, via `run.py --refinar`) — `generate_clarifying_questions` turns the reviewer's concerns into questions for the user; `refine_story` rewrites the story using the answers; `diff_story_versions` compares the final version against the original (new vs. discontinued rules/criteria); `update_jira_issue` persists the accepted version back to the ticket, under explicit confirmation.
- **Epic creation in Jira** (via `run.py --criar-jira`) — `create_jira_epic` creates the Epic ticket; `create_jira_story` creates each User Story as a child ticket — both only run after explicit human acceptance.
- `orchestrator/product_owner.py` (`handle_request(entrada, modo)`) handles `"unitario"` (single) and `"lote"` (batch).
- `retrieve_chunks` indexes and searches `knowledge/methodology/` via local embedding (`bge-m3`) and a local Qdrant instance; `read_jira_issue` fetches a Jira Cloud issue via REST API; `read_confluence_page` fetches a Confluence Cloud page (same credentials as Jira); `export_markdown` formats the final output.

Still missing: a `Feature` layer between Epic and User Story (today it only exists as a template in `knowledge/templates/feature.md`, no skill/workflow — evaluated and deliberately deferred until a PRD is large enough to actually need grouping), indexing of `knowledge/domain/` (empty, waiting on a real client), and project/long-term memory (`memory.md` — distinct from the RAG built over `knowledge/`, not yet implemented). `tests/` covers every implemented module (117 tests, LLM/HTTP calls mocked — fast and deterministic, no real calls to Ollama, Jira, or Confluence).

This project has its own git repository, independent from the parent monorepo (per the "every new project gets a separate repository" convention — see the root `CLAUDE.md`): [github.com/dufelizardo/AQuA-QE-Product-Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner).

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
