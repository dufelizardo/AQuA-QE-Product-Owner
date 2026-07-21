# AQuA-QE Product Owner — Whitepaper

> Também disponível em [Português](WHITEPAPER.md).

> A requirements-engineering agent that generates PRDs (from an idea), User Stories, Epics, and Acceptance Criteria from PRDs, requirement documents, Jira tickets, and Confluence pages — with mandatory traceability to source, automatic validation, and human review at the center of the cycle.

Repository: [github.com/dufelizardo/AQuA-QE-Product-Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner)

---

## 1. Executive summary

Manually refining requirements into User Stories, Epics, and Acceptance Criteria is slow, inconsistent across authors, and prone to gaps: implicit business rules that get lost, vague acceptance criteria, stories too large to fit in a Sprint. Product Owners, Business/QA Analysts, and Developers spend disproportionate time structuring information that already exists — scattered across PRDs, requirement documents, and tickets.

AQuA-QE Product Owner is an agent that automates this structuring without removing the human decision from the process. Starting from an informal idea, it can generate the PRD itself; from a requirements source (the generated PRD, a `.txt`/Markdown file, chat text, Jira ticket, or Confluence page), it extracts candidate requirements, identifies actor/goal/business rules, generates the artifact (a PRD, a User Story, or a full Epic) in the standard agile format, automatically validates it against INVEST/DoR, submits it to a second LLM acting as an independent reviewer, and only then presents the result for explicit human approval. No output is ever approved by the agent itself.

The project's differentiator is not generating plausible text — any LLM does that. It's the **interactive refinement cycle**: when review flags a problem, the agent does not try to self-correct by guessing the right answer. It turns the finding into an objective question, hands that question to a human, uses the real answer as additional context to rewrite the story, and only then re-runs review. The quality gain comes from the human's answer, not from the model's second attempt.

## 2. Methodological foundation

None of the quality criteria the agent uses were invented. Each one is documented in `knowledge/methodology/` and referenced directly by the agent's rules and guardrails:

| Framework | Role in the agent |
|---|---|
| **Scrum Guide** (`scrum_guide.md`) | Delimits what is the agent's role (structuring the artifact) vs. the Scrum Team's role (backlog prioritization, ceremonies — out of scope). |
| **BABOK** (`babok.md`) | Grounds requirement elicitation and structuring into formal artifacts. |
| **ISO/IEC/IEEE 29148** (`iso29148.md`) | Reference for software requirement quality and completeness. |
| **INVEST** (`invest.md`) | Quality checklist for every generated User Story — Independent, Negotiable, Valuable, Estimable, Small, Testable. |
| **DoR / DoD** (`dor.md`, `dod.md`) | Definition of Ready/Done used as a completeness reference before human review. |
| **BDD / Gherkin** (`bdd.md`, `gherkin.md`) | Mandatory format for Acceptance Criteria — verifiable Given/When/Then, never free text. |

These documents aren't decoration: `validate_story` and `validate_epic` implement checklists derived directly from INVEST/DoR, and the Given-When-Then format is explicitly enforced in the `generate_story`/`generate_epic_metadata` prompts.

## 3. Design principles (guardrails)

Three guardrails of equal priority — none subordinate to the others — govern the agent's entire behavior (`docs/agent/guardrails.md`):

- **GR-1 — Never invent.** No actor, goal, business rule, or acceptance criterion is generated without a traceable origin in the input source. When the source doesn't contain enough information, the agent **stops and asks for clarification** — it never fills the gap with an unflagged assumption. In the implementation this is literal: `identify_actor`/`identify_goal` return an empty string when they can't identify the field with confidence, which triggers the `PENDING_CLARIFICATION` status.
- **GR-2 — Never deliver a vague or untestable story.** Every output goes through `validate_story`/`validate_epic` (INVEST checklist, pure Python, no LLM) before being presented.
- **GR-3 — Never omit an identifiable business rule.** Rules identified — explicit or implicit — are listed in the story even when they don't individually become an acceptance criterion.
- **Cross-cutting guardrail — No automatic approval.** Regardless of the three guardrails above being satisfied, the agent never marks an artifact as "approved" — only as a **validated draft** (`draft_validated`). Final approval is always a human act, never delegated to the reviewer LLM or the automatic checklist.

These guardrails become formal, verifiable rules (`RULE-001` through `RULE-006` in `docs/agent/rules.md`), with explicit conflict resolution: blocking rules (traceability, validation, business rules, no self-approval) take priority over the formatting rule, which is only a recommendation.

## 4. Architecture

```
Input (.txt/Markdown/chat/Jira/Confluence)
   → read_text_file / read_jira_issue / read_confluence_page
   → extract_requirements
   → retrieve_chunks (RAG over knowledge/methodology/, when relevant)
   → identify_actor / identify_goal / identify_business_rules
   → generate_story  (generator LLM — mistral)
   → validate_story  (INVEST checklist, pure Python)
   → review_story    (independent reviewer LLM — phi4)
   → [if rejected] generate_clarifying_questions → human answer → refine_story → re-validate
   → explicit human acceptance
   → export_markdown / update_jira_issue
```

In batch mode, the same pattern repeats at the Epic level, but in **two phases**, not one — an architectural decision that avoids spending the expensive processing (identifying actor/goal/rules + generating + validating + reviewing each User Story) before the Epic itself is defined:

```
Full input (.txt/Markdown/Confluence)
   → extract_requirements
   → extract_prd_context (vision, non-functional requirements, risks, success criteria, constraints, dependencies)
   → identify_epic_groups (groups the requirements by thematic coherence — 1 group if the PRD is cohesive, N if it covers distinct fronts)
   → per group: generate_epic_metadata (from the text + the group's requirements, with NO story yet)
   → validate_epic
   → [human checkpoint] "Continue and generate the User Stories for {these N Epics / this Epic}?"
   → per Epic: generate_epic_stories: for each requirement → generate_story → validate_story → review_story
   → validate_traceability (duplicated stories, missing value, orphan requirements)
   → review_epic (now with the stories in place, evaluates real coherence with the Epic)
   → interactive human refinement for each rejected story
   → final human acceptance
```

`generate_epic_metadata` depends only on the source text and the extracted requirements — never on the stories, which don't exist yet at that point. This lets the human reject or request changes to the Epic (title/objective/scope/value) **before** any User Story is generated, avoiding the waste of generating a whole batch of stories under an Epic with the wrong scope. Only once the stories exist can `review_epic` meaningfully evaluate coherence between the Epic's objective and what the stories actually deliver — which is why the Epic review happens in two steps: `validate_epic` (automatic checklist, runs right after the Epic is defined) and `review_epic` (reviewer LLM, runs only after the stories are generated).

`extract_prd_context` closes a real traceability gap: a typical PRD (`docs/standards/prd_standard.md`) contains much more than functional requirements — vision, target audience, non-functional requirements, constraints, success criteria, risks, dependencies. Before, only the raw text and the flat list of functional requirements survived processing; all that other content was read by the LLM but never structured or preserved. `epic.prd_context` keeps that information tied to the Epic, without introducing any new process layer — it just preserves what was already being read.

`identify_epic_groups` closes the PRD→Epic(s) gap: before, a PRD covering distinct thematic fronts (e.g., "Scheduling" + "Notifications" + "Payment") always became a single, artificially broad Epic, mixing everything together. Now the grouping step decides how many Epics make sense — which can be just one, when the PRD is cohesive (default behavior, no visible change). If the LLM's response doesn't cover every requirement exactly once, the skill falls back to the safe single-group behavior, never losing traceability or inventing an inconsistent split (GR-1). The relationship is always one-directional — a PRD generates one or more Epics, never the reverse.

Code layers (`src/aqua_qe_product_owner/`):

- **`models/`** — data structures: `UserStory`, `Epic` (with `UnresolvedItem`), `AcceptanceCriteria`, `BusinessRule`, `Actor`, `Requirement`, `PRDContext`, `PRDDraft`, and the `StoryStatus` enum (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — 31 functions, each with a single side effect and a single responsibility (see section 5).
- **`workflow/`** — orchestration of the skill sequence per use case: `generate_prd.py` (`generate_prd_draft` → generates the PRD from an idea; `refine_prd_draft` → refines it with human answers), `generate_user_story.py` (`finalize_story`), `generate_epic.py` (`generate_epic_shape` → defines the Epic; `generate_epic_stories` → splits it into User Stories and finalizes it; `generate_epic` → convenience wrapper chaining both, with no human checkpoint), `generate_acceptance.py`, `refine_story.py`.
- **`orchestrator/product_owner.py`** — single entry point (`handle_request(entrada, modo)`), decides between `"unitario"` (single) and `"lote"` (batch) mode.
- **`services/`** — external integrations, introduced incrementally, one per real consumer: `llm_service` (Ollama), `embedding_service` (Ollama), `rag_service` (embedded Qdrant), `jira_service` and `confluence_service` (REST API + httpx).

There is deliberately **no** `Feature` layer between Epic and User Story in the code (it only exists as a template in `knowledge/templates/feature.md`). The evaluation recorded in the project concluded that this layer has real value, but a disproportionate cost for the volume of PRDs tested so far — it's deferred until a PRD large enough justifies the grouping, instead of being built speculatively.

## 5. The 31 skills

Skills with no LLM (pure Python, deterministic):

- `validate_story`, `validate_epic`, `validate_prd` — INVEST/DoR checklist.
- `format_prd_markdown` — formats the PRD as Markdown (local export and Confluence page body).
- `diff_story_versions` — changelog between versions (new vs. discontinued rules/criteria).
- `validate_traceability` — duplication, missing business value, orphan requirements.

Skills using the generator LLM (`OLLAMA_MODEL`, default `mistral`):

- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd`, `extract_requirements`, `extract_prd_context`, `identify_epic_groups`, `identify_actor`, `identify_goal`, `identify_business_rules`, `generate_story`, `generate_clarifying_questions`, `refine_story`, `generate_epic_metadata`.

Skills using an independent reviewer LLM (`OLLAMA_REVIEW_MODEL`, default `phi4` — deliberately a different model from the generator, to mitigate self-preference bias):

- `review_story`, `review_epic`, `review_prd`.

Embedding/RAG skills (Ollama `bge-m3` + embedded Qdrant, no external server):

- `retrieve_chunks` — indexes and searches `knowledge/methodology/` on demand.

External I/O skills:

- `read_text_file` (disk), `read_jira_issue`/`read_confluence_page` (read, Jira/Confluence Cloud REST API), `export_markdown` (disk), `update_jira_issue`/`create_jira_epic`/`create_jira_story`/`create_confluence_page` (write, Jira/Confluence Cloud REST API — **only executed after explicit human acceptance in the CLI, never automatically**).

Full input/output/error detail for every skill is in `docs/agent/skills.md`.

## 6. The interactive refinement cycle (the project's differentiator)

Most content-generation agents treat a "review rejected" signal as a cue for the same LLM to try again. This project treats it as a cue to **bring in a human with a specific question**:

1. `review_story`/`review_epic` rejects and produces `review_notes` — concrete findings (e.g., "acceptance criterion doesn't cover error case X," "benefit isn't measurable").
2. `generate_clarifying_questions` turns each finding into an objective, actionable question.
3. The CLI (`run.py --refinar`) presents the questions in the terminal; **a real human answers them** — not the same LLM self-correcting.
4. `refine_story` rewrites `description`, `business_rules`, and `acceptance_criteria` using the answers as real context, not as a new blind attempt.
5. The cycle re-validates (`validate_story`/`review_story`) and repeats if needed.
6. At the end, a prompt explicitly asks whether the user **accepts** the story. Only that explicit acceptance changes the status to `accepted` — never the LLM, never the automatic checklist (RULE-005).
7. `diff_story_versions` produces a changelog between the original and accepted versions (new vs. discontinued rules/criteria) — supports managing the story's lifecycle in the backlog.
8. If the source was a Jira ticket, the user is asked whether to persist the final version back to the ticket (`update_jira_issue`) — write-back is never automatic.

This design was validated live in two real tests: an informal PRD about a "Medical Appointment Scheduling System" (a full Epic with 6 User Stories, end-to-end interactive refinement, real Jira ticket creation) and a formal PRD on a real page of the user's Confluence Cloud.

Importantly, this cycle isn't just an approval gate. The human's answer to each generated question is a genuine **opportunity for joint work** — the human isn't just fixing a flagged error, they're improving the story's writing with context only they have (implicit business rules, scope decisions, edge cases the source text left unclear). The LLM structures the right question; the human's answer is what actually improves the story.

## 7. Operating modes

- **PRD** (`--modo prd`) — the missing "Idea → PRD" step: `generate_prd` produces a full PRD (context/problem, objective, target audience, scope, out-of-scope, functional/non-functional requirements, success criteria, risks and assumptions — per `docs/standards/prd_standard.md`) from an informal idea, goes through the same `validate_prd` → `review_prd` → `generate_prd_clarifying_questions`/`refine_prd` pattern (full interactive human-in-the-loop refinement, section 6) → explicit human acceptance. Once accepted, `format_prd_markdown` produces the final text, which can be exported (`--saida`), published to Confluence (`--publicar-confluence`), and/or become the batch mode's input (the CLI asks whether to continue and generate the Epic from it). Input via `--arquivo` or `--texto`.
- **Single** (`--modo unitario`) — one User Story per run, with the possibility of close interaction at each step. Input via `--arquivo`, `--texto`, or `--jira`.
- **Batch/Epic(s)** (`--modo lote`) — in two phases: first `extract_prd_context` + `identify_epic_groups` (groups the extracted requirements by thematic coherence — a cohesive PRD becomes a single Epic; a PRD covering distinct fronts can become several) + `generate_epic_metadata` per group define each candidate Epic's title/objective/scope/value/criteria from the source text — **without generating any User Story yet** — and `validate_epic` checks each one's automatic checklist; the CLI then asks the user whether to continue (a single combined question covering every Epic identified). Only after confirmation is each Epic split into User Stories (one per requirement in its group), each going through the full single-mode pipeline; ambiguous items become `unresolved_items` without blocking the rest of the batch; `validate_traceability` and `review_epic` (now with the stories in place) run before per-story refinement, one Epic at a time. Input via `--arquivo` or `--confluence`.
- **`--criar-jira`** (batch mode) — after explicit human acceptance **of each Epic** (individual prompt, one Epic at a time), creates the Epic ticket and each User Story as a child ticket in Jira Cloud (simple `parent` link, assumes a *team-managed* project).
- **`--publicar-confluence`** (PRD mode) — after explicit human acceptance of the PRD, asks for a title and publishes the page to Confluence Cloud (`create_confluence_page`), returning the created URL.

## 8. Real integrations

- **Jira Cloud** (REST API v3) — read (`read_jira_issue`, converting Atlassian Document Format to plain text), write (`update_jira_issue`, converting back to ADF), and creation (`create_jira_epic`/`create_jira_story`). Authentication via Basic Auth (email + API token generated at `id.atlassian.com/manage-profile/security/api-tokens`).
- **Confluence Cloud** (REST API v1) — page read (`read_confluence_page`), converting the storage format (XHTML) to plain text via the stdlib's `html.parser.HTMLParser` (no new dependency); and **page creation** (`create_confluence_page`/`create_page`), converting plain text back to storage format (one `<p>` per line, HTML-escaped) — requires `CONFLUENCE_SPACE_KEY` in addition to the reused Jira credentials (same Atlassian account).

All **write** operations require explicit human acceptance before firing — there is no code path where the agent writes to an external system without user confirmation.

## 9. Technical stack

- **Local LLM via Ollama** — `mistral` for generation, `phi4` as an independent reviewer, `bge-m3` for embeddings (1024 dimensions, strong performance in Portuguese). A deliberate choice of local models over cloud APIs, configurable via `OLLAMA_MODEL`/`OLLAMA_REVIEW_MODEL`/`OLLAMA_EMBEDDING_MODEL`/`OLLAMA_BASE_URL`.
- **Embedded Qdrant** (`QdrantClient(path=...)`, no server) for RAG over `knowledge/methodology/`.
- **`uv`** for dependency management — a standalone project (its own repository, outside the monorepo that originated it), with `httpx` and `python-dotenv` declared explicitly in `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Quality and test coverage

103 automated tests cover every implemented module (90% line coverage), all with Ollama/Jira/Confluence calls mocked — fast, deterministic, no dependency on external infrastructure to run in CI. Evaluating the agent in production combines three layers that never substitute for one another (`docs/agent/evaluation.md`):

1. Automatic checklist (`validate_story`/`validate_epic`) — no LLM.
2. LLM-as-judge (`review_story`/`review_epic`) — a different model from the generator.
3. Mandatory human review — the only act that actually approves an artifact.

Success metrics defined in the PRD: reduction in refinement time, acceptance rate without rework, requirement coverage (% of the source's requirements that actually became a traceable User Story).

## 11. What's still missing (deliberately deferred, not forgotten)

- **`Feature` layer** between Epic and User Story — evaluated and deferred until a PRD large enough justifies the grouping (see section 4).
- **Indexing of `knowledge/domain/`** — folder structure ready (requirements, business rules, processes, screens, API, database, glossary), empty until a real client/project exists to populate it.
- **Project/long-term memory** (`memory.md`) — distinct from the RAG over `knowledge/methodology/`, not yet implemented.
- **Resilience to local Ollama infrastructure failures** — instability observed during long runs that swap models (generator ↔ reviewer); a conscious decision to re-run manually rather than add automatic retries, until there's evidence the added complexity pays off.

## 12. How to run it

See `README.md`/`README.pt.md` for the full setup walkthrough (Python 3.12+, `uv`, Ollama + models, `.env.example` → `.env`) and every `run.py` usage example (`--modo prd`/`unitario`/`lote`, `--arquivo`/`--texto`/`--jira`/`--confluence`, `--refinar`, `--criar-jira`, `--publicar-confluence`).

## 13. Conclusion

AQuA-QE Product Owner doesn't aim to replace the Product Owner — it aims to eliminate the mechanical structuring work that precedes their decision. Every guardrail in the project (never invent, never deliver a vague story, never omit a business rule, never self-approve) exists so the agent's output is always a reliable starting point for human review, never a substitute for it. The interactive refinement cycle — questions generated by the LLM, answered by a real human, folded back into the story — is the centerpiece that sets this agent apart from a simple plausible-text generator.
