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
- **`src/aqua_qe_product_owner/skills/`** — the agent's skills in Python (read text file, read a Jira issue, retrieve chunks, extract requirements, identify actor/goal/rules, generate/validate/review/refine the story, generate Epic metadata, diff story versions, export to Markdown, update/create Jira issues).
- **`src/aqua_qe_product_owner/models/`** — the agent's data structures (User Story, Epic, Acceptance Criteria, Business Rule, Actor, Requirement).
- **`src/aqua_qe_product_owner/workflow/`** — orchestration of the skill sequence per use case (generate a single User Story, generate a batch Epic, generate/complement acceptance criteria).
- **`src/aqua_qe_product_owner/orchestrator/`** — single entry point that decides which workflow to run.
- **`src/aqua_qe_product_owner/services/`** — external integrations: `llm_service` (local Ollama, generation), `embedding_service` (local Ollama, `bge-m3`), `rag_service` (embedded/local Qdrant, no server) and `jira_service` (Jira Cloud REST API).

## Usage

```bash
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

`--criar-jira` (batch mode only) generates the full Epic — title, objective, scope, value and acceptance criteria, not just the User Stories — and, after an explicit acceptance prompt, creates the Epic ticket in Jira (`JIRA_PROJECT_KEY`, `JIRA_EPIC_ISSUE_TYPE_ID`) and each User Story as a child ticket (`JIRA_STORY_ISSUE_TYPE_ID`, simple `parent` link — assumes a *team-managed* project), returning the created keys. See `run.py --help` for all options.

## Status

`docs/agent/`, `docs/standards/` and `knowledge/` (except `domain/`, `regulations/` and `examples/`, which depend on a real client/project) are filled in with real content.

In `src/`, all 10 skills and the three workflows are implemented and work end to end with local models via Ollama:

- **Single-story mode** (`workflow/generate_user_story.py`) — `read_text_file` → `extract_requirements` → `identify_actor`/`identify_goal`/`identify_business_rules` → `generate_story` (LLM `mistral`) → `validate_story` (pure Python checklist) → `review_story` (reviewer LLM `phi4`, independent from the generator) → final status.
- **Batch mode** (`workflow/generate_epic.py`) — same sequence applied to each requirement extracted from the source; ambiguous items (actor/goal not identified) become `unresolved_items` without blocking the rest of the batch. `generate_epic_metadata` fills in the Epic's title, objective, scope, value and high-level acceptance criteria (previously left blank), and the Epic goes through the same quality cycle as a Story: `validate_epic` (pure Python checklist) → `review_epic` (reviewer LLM `phi4`). Before per-story refinement, `validate_traceability` checks for duplicated stories, stories with no business value, and orphan requirements.
- **Acceptance criteria complement** (`workflow/generate_acceptance.py`) — generates additional acceptance criteria for an existing User Story and reapplies `validate_story`/`review_story`.
- **Interactive refinement** (`workflow/refine_story.py`, via `run.py --refinar`) — `generate_clarifying_questions` turns the reviewer's concerns into questions for the user; `refine_story` rewrites the story using the answers; `diff_story_versions` compares the final version against the original (new vs. discontinued rules/criteria); `update_jira_issue` persists the accepted version back to the ticket, under explicit confirmation.
- **Epic creation in Jira** (via `run.py --criar-jira`) — `create_jira_epic` creates the Epic ticket; `create_jira_story` creates each User Story as a child ticket — both only run after explicit human acceptance.
- `orchestrator/product_owner.py` (`handle_request(entrada, modo)`) handles `"unitario"` (single) and `"lote"` (batch).
- `retrieve_chunks` indexes and searches `knowledge/methodology/` via local embedding (`bge-m3`) and a local Qdrant instance; `read_jira_issue` fetches a Jira Cloud issue via REST API; `read_confluence_page` fetches a Confluence Cloud page (same credentials as Jira); `export_markdown` formats the final output.

Still missing: a `Feature` layer between Epic and User Story (today it only exists as a template in `knowledge/templates/feature.md`, no skill/workflow — evaluated and deliberately deferred until a PRD is large enough to actually need grouping), indexing of `knowledge/domain/` (empty, waiting on a real client), and project/long-term memory (`memory.md` — distinct from the RAG built over `knowledge/`, not yet implemented). `tests/` covers every implemented module (68 tests, LLM/HTTP calls mocked — fast and deterministic, no real calls to Ollama, Jira, or Confluence).

**Infrastructure note**: this project still has no `git init` of its own (it should follow the "every new project gets a separate repository" convention — see the root `CLAUDE.md`, along with future agent projects); the entire history of this implementation exists only on disk in this directory, with no version control.
