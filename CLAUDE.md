# CLAUDE.md — SocraticLLM

This file is read by Claude Code at session start. It is the source of truth for project state, decisions, and next steps. Update it after each meaningful session.

---

## What This Project Is

SocraticLLM is a Socratic tutor: a dialogue system that teaches recognition and transfer, not answers. It never tells the student what to do — only asks the next question — and builds a persistent, longitudinal model of how a specific student thinks. A teacher-side flow turns an uploaded textbook into the concept graph the dialogue runs against, for whatever subject that textbook covers.

Full vision: `VISION.md`

**2026-07-12 pivot:** this project previously pursued a different concept — a from-scratch, self-narrating transformer that taught CS-curious people how LLMs work internally (tokenizer → embeddings → attention → feedforward → softmax, each instrumented to narrate itself). That vision is superseded. The code from that effort has been extracted with full git history into a standalone repo at `~/Projects/didactic-transformer` (local only, no remote yet) and removed from this repo entirely. `socraticllm/` and `tests/` exist again as of this session, but freshly — they hold only new-vision code (the concept graph so far), not any of the extracted legacy code. `examples/` does not exist here anymore.

---

## Core Design Decisions (do not relitigate without flagging)

**1. The hard constraint: the system never gives the answer, only the next question.**
This is architectural, not a prompt-level suggestion — a guardrail layer validates every dialogue turn and rejects/retries anything that leaks an answer. This is what makes the product different from an AI tutor that happens to be phrased as questions.

**2. Persistent student model is the primary product.**
The model's own weights don't change through interaction — the student does. That change is tracked explicitly: a structured student profile records recognition patterns, stall points, and friction per concept, scoped per curriculum (a student may work through more than one). It should be surfaced to the student so they can watch their own growth, and to the teacher so they can see where a class is actually stuck. Schema below; lives at `learner/state.json` (path/name likely to change — see Open Design Questions).

**3. Curriculum is whatever textbook the teacher uploads — not a fixed domain list.**
STEM and the Trivium are the initial focus because they're recognition-heavy, not a hard boundary. If a teacher uploads a book on LLMs, "LLMs" is the curriculum. The system extracts the concept graph (concepts, prerequisites, sequencing) from the source text; the teacher doesn't hand-build it.

**4. The dialogue engine calls an existing LLM API — it does not run a self-hosted model.**
Confirmed 2026-07-12. The engineering effort goes into the concept graph, the guardrail that enforces the questions-only constraint, and the student model — not into model internals. This also means the from-scratch transformer code from the prior vision is not a dependency of this product.

**5. Two surfaces, one engine; student side ships first.**
Student-side dialogue is v1. Teacher-side curriculum upload and dashboard follow once the dialogue loop is proven — per `VISION.md`'s own "First Version" scoping (no teacher dashboard yet, no longitudinal tracking yet).

---

## Pedagogy

These are design principles for the dialogue engine's behavior, not just the hard constraint in Core Design Decision #1. They govern *how* a question is chosen, not just that a question (rather than an answer) is delivered.

**Don't resolve understanding prematurely.** When the student asks a question, the system should first assess whether answering directly would short-circuit their own reasoning. If so, the response is a question, a reframe, or a partial answer that creates productive tension rather than closure — not a stall tactic, but a deliberate refusal to hand over the resolution the student hasn't earned yet. A complete, direct answer is only warranted once the student has demonstrated they've done the conceptual work, or when they explicitly ask for the direct answer outright. The goal is arrived-at understanding, not received information.

**Notice when the student accepts too easily.** If the student takes the system's first response at face value without interrogating it, that's a signal to gently resist, not to move on. Surface the assumption underneath the answer and ask whether it holds. Passive acceptance is the failure mode this product exists to break.

**Name understanding when it arrives.** When the student reaches a correct understanding on their own, say so explicitly. The reward signal for productive struggle needs to come from the system, not only from the satisfaction of the correct answer appearing — otherwise there's nothing distinguishing earned recognition from a lucky guess in the student's own experience of the moment.

**The tension this creates is intentional, and belongs in the product framing, not just the architecture.** Models default to answering fully because that's what they're rewarded for. SocraticLLM is deliberately less immediately helpful in service of being more genuinely useful. That trade-off should be named clearly wherever the product explains itself — not hidden as an implementation detail — because a student (or teacher) who doesn't understand why the system is withholding answers will just experience it as unhelpful.

---

## Repo Structure (target)

Partially scaffolded — `socraticllm/curriculum/concept_graph.py`, `pyproject.toml`, and `tests/`
exist; the rest doesn't yet. Proposed shape, reflecting "two surfaces, one engine":

```
SocraticLLM/
├── CLAUDE.md
├── VISION.md
├── README.md
├── TODO.md
├── LICENSE
├── pyproject.toml
├── socraticllm/
│   ├── engine/
│   │   ├── llm_client.py       # wraps the LLM API call used for dialogue
│   │   ├── dialogue.py         # the Socratic dialogue loop
│   │   ├── guardrail.py        # enforces the hard constraint: no answer ever leaves this layer
│   │   └── metacognition.py    # engineers self-discovery moments (e.g. resurfacing a past problem)
│   ├── curriculum/
│   │   ├── ingest.py           # accepts an uploaded textbook, extracts raw text
│   │   ├── concept_graph.py    # schema (Concept, Prerequisite, Domain) + LLM-driven extraction
│   │   └── store.py            # persistence — one concept graph per uploaded curriculum
│   ├── student/
│   │   ├── model.py            # persistent per-student state: recognition patterns, friction, readiness
│   │   └── session.py          # one problem -> dialogue -> session lifecycle
│   ├── teacher/
│   │   └── dashboard.py        # deferred past v1
│   └── interface/
│       └── repl.py             # v1 driver, student side only
├── curricula/                   # gitignored: uploaded source docs + generated concept graphs, one dir per curriculum
├── student/                     # student-state persistence (data, not code — see socraticllm/student/ above)
│   ├── state.json
│   └── history/
└── tests/
```

---

## Student State Schema

`student/state.json` (moved from `learner/state.json` — see Current State) is injected into each session, and is loaded/saved via `socraticllm/student/model.py` (`StudentState`, `CurriculumProgress`, `ConceptProgress`, `load()`, `save()`). The prior schema hardcoded a 5-item concept map (tokenization/embeddings/attention/feedforward/softmax) tied to the old vision. Since curriculum is now pluggable, the concept map is keyed dynamically off whatever `ConceptGraph` is active (`StudentState.ensure_curriculum(graph)` populates a curriculum's concept map from the graph's concept ids without disturbing existing progress), and scoped per curriculum since a student may work through more than one.

Shape (implemented, `tests/test_student_model.py` passing):

```json
{
  "student_state": {
    "version": "0.2",
    "student_id": "",
    "last_updated": "",
    "session_count": 0,

    "curricula": {
      "<curriculum_id>": {
        "concept_map": {
          "<concept_id>": {
            "status": "not_yet",
            "confidence": null,
            "notes": null,
            "last_seen": null
          }
        },
        "friction_log": [],
        "open_questions": []
      }
    },

    "preferred_explanation_style": {
      "analogies": null,
      "math": null,
      "code": null
    }
  }
}
```

`status` values: `not_yet` | `encountered` | `recognized` (renamed from `working` — VISION.md's language is specifically about *recognition*, not proficiency)
`confidence` values: `low` | `medium` | `high` | `null`

Dropped from the old schema: `disclosure_level`. That was specific to the old vision's progressive-disclosure-of-internals feature and has no equivalent here.

---

## Current State

- [x] VISION.md rewritten for the Socratic-tutor product (consolidated from the now-removed `SOCRATICLLM.md`)
- [x] CLAUDE.md updated to match (this session)
- [x] TODO.md updated to match (this session, see below)
- [x] Legacy transformer code extracted with history to `~/Projects/didactic-transformer` and removed from this repo
- [x] `learner/` vs `student/` naming resolved — renamed to `student/` (see Open Design Questions)
- [ ] Repo restructured to target shape (`engine/`, `curriculum/`, `student/`, `teacher/`, `interface/`) — `curriculum/` and `student/` started, rest not yet
- [x] Concept graph schema defined (`socraticllm/curriculum/concept_graph.py` — `Concept`, `ConceptGraph`; add/get, prerequisite lookup, cycle + dangling-reference validation, topological ordering; tests passing)
- [x] Student state schema redesigned and implemented (`socraticllm/student/model.py`); `learner/state.json` renamed to `student/state.json` and rewritten to the new schema (no real data existed to migrate)
- [x] LLM client wrapper implemented (`socraticllm/engine/llm_client.py`, `LLMClient`; calls the Claude API — `anthropic` added as a dependency)
- [x] Guardrail (the hard constraint) implemented — first pass, structural/heuristic only (`socraticllm/engine/guardrail.py`); semantic follow-up noted in Open Design Questions
- [x] Dialogue engine implemented (`socraticllm/engine/dialogue.py`, `DialogueEngine`; wires `LLMClient` + guardrail into a turn loop with retry-then-fallback on guardrail rejection)
- [ ] First-version curriculum chosen and its concept graph created
- [ ] Student-side REPL wired end to end
- [ ] Metacognition layer implemented
- [ ] Curriculum ingestion pipeline (textbook upload -> concept graph extraction) implemented
- [ ] Teacher dashboard — explicitly deferred past v1
- [x] `REFERENCES.md` created (external articles supporting the problem statement); `VISION.md` points to it
- [x] References populated — 5 entries, added manually by the user (see Last session)

**Last session:** Reconciled a vision fork: `VISION.md` still described the old from-scratch, self-narrating-transformer product, while a separate `SOCRATICLLM.md` (added in a later commit, "Update vision: Socratic tutor...") described an entirely different product — a Socratic dialogue tutor — but had the old CLAUDE.md content accidentally appended to it rather than replacing the old vision cleanly. Confirmed with the user: the Socratic-tutor vision is authoritative, the domain is not fixed to STEM/Trivium/algebra but whatever textbook a teacher uploads, and the dialogue engine will call an existing LLM API rather than a self-hosted model. Consolidated into `VISION.md`, removed `SOCRATICLLM.md`, and rewrote this file and `TODO.md` to match.

Then resolved the legacy-code question: extracted `socraticllm/tokenizer/`, `socraticllm/model/`, `socraticllm/narration/`, `socraticllm/curriculum/lessons.py`, their tests, `examples/repl.py`, and `pyproject.toml` into a standalone repo at `~/Projects/didactic-transformer`, using `git-filter-repo` (installed via `pip install --user --break-system-packages`) so the extracted repo keeps real history for those paths. Two files (`socraticllm/model/attention.py`, `embeddings.py`) had uncommitted working-tree changes that predated this session — a real, tested `Embeddings.forward`/`MultiHeadAttention.forward` implementation that had never been committed — so those were copied into the new repo and committed there before removal here, rather than being lost. `origin` was auto-stripped from the new repo by `git-filter-repo`; it's local-only per the user's choice. The legacy code removal (`git rm -r socraticllm tests examples pyproject.toml`), the VISION/CLAUDE/TODO rewrites, and `learner/` were committed together and pushed (`90d1a72`).

Then rewrote `README.md` (`9e5cc56`) — the old one was a placeholder line from before either vision existed — to describe the Socratic-tutor product, its two-surface architecture, and honest current status.

Then implemented the concept graph schema: `socraticllm/curriculum/concept_graph.py` (`Concept`
dataclass — id, name, description, an optional `domain` tag for classification, and
`prerequisites` as a list of concept ids for sequencing) and `ConceptGraph` (add/get,
`prerequisites_of`, `validate()` which catches dangling prerequisite references and cycles via a
three-color DFS, and `topological_order()`). Deliberately did not add a separate `Prerequisite`
class — a plain list of ids on `Concept` covers what's needed so far; revisit if prerequisites
need their own metadata (e.g. required vs. helpful) later. Also did not add a separate `Domain`
class — `domain` is a free-text tag on `Concept` for now, not its own graph-level construct;
`curriculum_id` on `ConceptGraph` is what one uploaded textbook maps to. Recreated `pyproject.toml`
(package `socraticllm`, no dependencies yet) since it had been removed along with the rest of the
legacy code. Found a working `.venv` already present with pytest installed — the venv-creation
issue noted in `TODO.md`'s Environment section appears resolved; `tests/test_concept_graph.py`
(9 cases: add/get, duplicate-id error, unknown-id error, prerequisite lookup, valid-graph pass,
dangling-reference error, cycle error, topological order correctness, topological-order-on-cycle
error) all pass via `.venv/bin/python -m pytest`. Committed and pushed (`339915a`).

All work through this session is committed and pushed; working tree is clean.

**Then:** Created `REFERENCES.md` — a running list of external articles that speak to the problem statement in `VISION.md`, formatted as `[Title](url) — why it's relevant`. Added a pointer to it from `VISION.md`'s "The Core Problem" section. Intended workflow: user pastes an article URL, Claude fetches it via WebFetch, pulls the title, and appends a formatted entry. First attempt (NPR article, `https://www.npr.org/2026/01/28/nx-s1-5631779/ai-schools-teachers-students`) hit a WebFetch timeout, so the user populated all 5 references manually instead: coverage of teachers going analog/banning AI in the classroom (NPR, Edutopia), UChicago Law's device ban for 1Ls (two MSN/Fox pieces), and a Brookings policy overview on ban-vs-integrate approaches. Committed together with the `CLAUDE.md`/`VISION.md` updates.

**Then:** Implemented the student state schema redesign. Confirmed with the user that the existing `learner/state.json` had no real data worth migrating (`session_count: 0`, every concept still `not_yet` — just the old template) and that `learner/` should be renamed to `student/` to match the `socraticllm/student/` module name, resolving the naming open question. `git mv learner student`, then added `socraticllm/student/model.py` (`ConceptProgress`, `CurriculumProgress`, `StudentState` dataclasses; `StudentState.ensure_curriculum(graph)` populates a curriculum's `concept_map` from a `ConceptGraph`'s concept ids without clobbering existing progress; `load()`/`save()` for the JSON file) and `socraticllm/student/__init__.py` re-exporting the public names, mirroring the `socraticllm/curriculum/` package's shape. Regenerated `student/state.json` via `save(StudentState())` so the on-disk file matches the loader's expected format exactly, rather than hand-writing it. `tests/test_student_model.py` (4 cases: missing-file load returns defaults, `ensure_curriculum` populates from a graph, `ensure_curriculum` doesn't overwrite existing progress, save/load round-trip) passes alongside the existing concept graph tests (13 total).

**Then:** Implemented the LLM client wrapper. Added `socraticllm/engine/llm_client.py` — `LLMClient`, a thin wrapper around `anthropic.Anthropic().messages.create()` with one method, `complete(system, messages, max_tokens)`, returning the extracted text block. Defaults to `claude-opus-4-8` (per Core Design Decision #4 — an existing LLM API, not a self-hosted model) and requests adaptive thinking (`thinking: {"type": "adaptive"}`) on every call, since dialogue-turn generation under the pedagogy constraints in this file's Pedagogy section is exactly the kind of judgment call adaptive thinking is for. Added `anthropic` as a real dependency in `pyproject.toml` (previously empty) and installed it into the existing `.venv`. `socraticllm/engine/__init__.py` re-exports `LLMClient`, mirroring `curriculum/` and `student/`. The client is injectable (`LLMClient(client=...)`) specifically so tests don't hit the real API — `tests/test_llm_client.py` (2 cases: extracts the `text` block and ignores `thinking` blocks; passes `model`/`system`/`messages`/`max_tokens` through to the underlying call) uses a hand-written fake client rather than a mocking library. All 15 tests pass.

**Then:** Started the guardrail — the hard constraint from Core Design Decision #1. Before writing it, flagged a real gap: there's no `Problem`/expected-answer model anywhere in the codebase yet (no `Problem` class in `curriculum/`, no per-session "current problem" in `student/`), which limits what a guardrail can check. Asked the user how to scope a first pass; agreed on **structural/heuristic**, not semantic — `socraticllm/engine/guardrail.py`'s `check(response)` flags responses *shaped* like a delivered answer (declarative "the answer is X" / "the solution is X" phrasing, "Answer:"/"Final answer:" labels, "so/therefore/thus/hence, the answer..." conclusions, "you should conclude that...", and multi-step "Step 1: ... Step 2: ..." walkthroughs — 2+ step markers), regardless of curriculum content. It does **not** know whether a given response's content is factually the answer to a specific problem — that needs a semantic, LLM-judge-based check once a `Problem`/answer representation exists (see Open Design Questions below, which now also notes this as a follow-up). `GuardrailResult(passed, reason)` is the return type; `socraticllm/engine/__init__.py` re-exports `check` and `GuardrailResult` alongside `LLMClient`. `tests/test_guardrail.py` (11 leaked-answer cases that must be rejected, 6 legitimate Socratic responses — including a bare affirmation with no question mark, per the Pedagogy section's "name understanding when it arrives" — that must pass) all pass; one regex bug found and fixed along the way (the step-marker pattern required whitespace immediately after the step number, which "Step 1:" doesn't have). All 32 tests pass.

**Then:** Implemented the dialogue engine. `socraticllm/engine/dialogue.py`: `DialogueEngine` wraps an `LLMClient` and a `SYSTEM_PROMPT` translating the Pedagogy section's three principles (never resolve prematurely, resist easy acceptance, name understanding when it arrives) into instructions for the model. `ask(student_message)` appends to `self.history`, calls the LLM, and checks the candidate against the guardrail (`check()`); on rejection it retries up to `MAX_GUARDRAIL_RETRIES` (2) with a corrective message appended to a **local** copy of the message list — never to permanent history, so a rejected candidate and the retry-nudge never appear in the record the student or a future session actually sees. After exhausting retries, falls back to a fixed safe question (`FALLBACK_RESPONSE`) rather than ever letting a flagged response through — the hard constraint holds even in the worst case. Returns a `DialogueTurn(response, guardrail_retries)` so callers can observe how often the guardrail fired.

Decided not to give `DialogueEngine` a hard `ConceptGraph` dependency, since there's still no `Problem`/session model to select which concept applies (same gap noted for the guardrail). Instead it takes an optional `curriculum_context: str` that gets folded into the system prompt — a plain-string hook a future `student/session.py` can fill in once it exists, without this module needing to import `ConceptGraph` prematurely. `tests/test_dialogue.py` (5 cases: passing response used directly, reject-then-succeed retry with the rejected candidate confirmed absent from history, fallback after exhausting retries, history accumulates across multiple turns, `curriculum_context` appears in the system prompt sent to the LLM) uses a hand-written scripted fake client, same pattern as `test_llm_client.py`. All 37 tests pass.

**Then:** Ran an 8-angle multi-agent code review (high effort) over the dialogue engine commit, then fixed the 3 CONFIRMED correctness bugs it found (left the 2 PLAUSIBLE findings and the CONFIRMED cleanup/altitude/efficiency findings — retry logic belongs on the guardrail not the engine, no prompt caching, `FALLBACK_RESPONSE` doesn't vary, `llm_client or LLMClient()` discards a falsy-but-valid client, user-role misattribution of the retry correction — untouched, since the user asked specifically for "the confirmed bugs"):

1. **Dangling history entry.** `DialogueEngine.ask()` used to append the student's message to `self.history` *before* calling the LLM; if `complete()` raised, the exception propagated but left an unpaired `user` entry, so the *next* `ask()` call would append a second consecutive `user` message — which the Anthropic Messages API rejects (roles must alternate), meaning one transient API failure broke every subsequent turn in the session. Fixed by building the turn's `user_turn` and `messages` locally and only appending to `self.history` once a final outcome exists (success or fallback) — an exception now leaves `self.history` completely untouched.
2. **Uncaught `StopIteration` in `LLMClient.complete()`.** `next(block.text for block in response.content if block.type == "text")` crashed with a bare `StopIteration` if the model emitted no text block (plausible with `thinking: {"type": "adaptive"}` consuming the whole budget). Replaced with an explicit loop and a new `NoTextResponseError` (re-exported from `socraticllm.engine`) carrying `stop_reason` and the block types actually present, so a caller gets a debuggable error instead of a cryptic crash.
3. **`FALLBACK_RESPONSE` bypassed the guardrail.** `guardrail.py`'s own docstring says "every candidate dialogue turn passes through here before it reaches the student," but the fallback path returned `FALLBACK_RESPONSE` without ever calling `check()` on it — true today only because the constant happens to be guardrail-safe by hand. Now the fallback path calls `check(FALLBACK_RESPONSE)` too; if a future edit to the constant ever made it fail, the code raises `RuntimeError` rather than silently letting it through, so the hard constraint's own stated invariant actually holds for every code path, not just by convention.

Added 5 regression tests (`tests/test_llm_client.py`: `NoTextResponseError` is raised with a clear message; `tests/test_dialogue.py`: history stays empty after a raised exception, a new `FlakyLLMClient` double proves the engine can be asked again cleanly after a failed turn, `FALLBACK_RESPONSE` itself passes the guardrail, and a monkeypatched guardrail proves the `RuntimeError` safety net fires). All 42 tests pass.

**Next task:** First-version curriculum content (`TODO.md` step 6) — hand-author a small concept graph for one subject, the fastest path to proving the dialogue constraint end to end per `VISION.md`'s own framing. Which subject is still open. After that: the student-side REPL (`socraticllm/interface/repl.py`, `TODO.md` step 7) to wire concept graph + student model + dialogue engine + guardrail into one working loop — this is also where the `Problem`/session-model gap flagged above will likely need to get resolved.

---

## Open Design Questions

- **First-version curriculum scope.** `VISION.md`'s "First Version" section names algebra as the example; the user has since clarified the domain is generic (e.g. a book on LLMs would work equally). Still open: whether v1 hand-authors a small concept graph directly (fastest path to proving the dialogue constraint) or builds the ingestion/extraction pipeline first. Leaning toward hand-authoring first, per `VISION.md`'s own "just prove the dialogue works" framing, but not decided.
- **Semantic guardrail follow-up.** `socraticllm/engine/guardrail.py`'s first pass is structural/heuristic (see Current State) — it can't check whether a response's content is factually the answer to the specific problem the student is working, only whether it's *shaped* like a delivered answer. A semantic check needs a `Problem`/expected-answer representation, which doesn't exist yet (no `Problem` class in `curriculum/`, no per-session "current problem" in `student/`). Whether to add an LLM-judge-based semantic layer on top of the heuristic pass, and what that representation looks like, is open — likely to surface again once `student/session.py` ("one problem -> dialogue -> session lifecycle") is built.
- **Unfixed code-review findings on `dialogue.py`.** A code review after the dialogue engine landed found 3 CONFIRMED correctness bugs (fixed, see Current State) plus 6 more findings deliberately left alone since the user asked only for "the confirmed bugs": (1) `self._llm = llm_client or LLMClient()` uses `x or default()`, which would silently discard an injected client that happens to be falsy — PLAUSIBLE, no current caller triggers it; (2) the guardrail-retry correction is injected as a `{"role": "user", ...}` message, misattributing an operator-level correction to the student — PLAUSIBLE, and not a trivial fix since the Claude API's mid-conversation `role: "system"` alternative requires the message to directly follow a `user` turn, which the current retry sequence doesn't; (3) retry-then-fallback orchestration lives in `DialogueEngine.ask()` rather than on `guardrail.py` itself, so a second caller of `check()` would have to reimplement it; (4) the full conversation history is resent on every turn and every retry with no truncation or Anthropic prompt caching; (5) `FALLBACK_RESPONSE` is always the identical string regardless of context or repeat exposure; (6) the retry loop's manual counter/`while True` could be a `for attempt in range(...)` and the success/fallback branches duplicate an append-then-return shape. None of these are blocking; worth revisiting before the `interface/repl.py` step if a real student conversation will actually exercise long sessions.
- **API key management, and whether an admin UI/role is needed.** For v1, the LLM API key is a single environment variable (the `anthropic` SDK resolves `ANTHROPIC_API_KEY` from the environment automatically — no code change needed) — fine for a single-deployment, single-key setup. The user is considering a further-out model: multiple teachers register, an IT-administrator role configures the LLM API key (and presumably approves/manages teachers), which implies multi-tenancy the current design doesn't have — curricula are keyed by `curriculum_id` only, with no owning-teacher or owning-org concept. This is explicitly **not** v1 scope; noted here so it isn't lost, not because it should influence current TODO ordering.
- **Whether students need to register at all.** The user's current thinking: no per-student account/login — instead, a school points internal DNS at the deployment and students just start a conversation. This is in tension with Core Design Decision #2 (persistent per-student model, scoped per curriculum, keyed by `student_id` in the schema) — some identifier still has to tie a conversation back to a specific student's history across sessions, even without a formal registration flow. Candidate approaches (none chosen): a device-local identifier (browser storage/cookie, no login), the school's existing SSO/roster feeding an identifier without SocraticLLM ever handling credentials, or a lightweight name/ID prompt with no password. Affects the `student_id` field in the Student State Schema above and the eventual `interface/repl.py` (or web equivalent) — flagging now, not deciding now.

---

## Working Conventions

- Update the "Current State" checklist and "Last session" note at the end of every session.
- Don't start a new component until the previous one has a passing test.
- When uncertain about a design decision, flag it explicitly rather than picking arbitrarily — add to `## Open Design Questions` above.
