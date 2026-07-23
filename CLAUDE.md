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

### The attention loop and question-move palette are proprietary — not in this repo

**2026-07-23:** a dedicated session distilled a specific questioning methodology (a macro-level "what to focus on and when to move on" loop, plus a named set of question-move patterns) that goes beyond the three general principles above. This repo is Apache 2.0 (`LICENSE`, public GitHub remote) — trade secret protection is incompatible with checking proprietary content into a publicly licensed repo, so that methodology is **not written here**. It's kept in a private location and, for the dialogue engine, loaded at runtime as an optional prompt overlay (see `socraticllm/engine/dialogue.py`'s `_load_methodology_overlay()` — reads a gitignored local path, `private/methodology_prompt.txt` by default, or `SOCRATICLLM_METHODOLOGY_PATH` if set). Without that file present, the engine still runs on the generic public `SYSTEM_PROMPT` alone.

The user is planning a separate, private repo for the methodology content itself. Until that exists, `private/` is gitignored here and holds the working copy locally.

**Sequencing decision (2026-07-23, not proprietary — general architecture):** `ConceptGraph`'s prerequisite structure acts as a **readiness gate**, not a fixed walk order. A concept can't be surfaced as the next thing to work on until its prerequisites are `recognized` in the student's state — but among whatever's currently unlocked, focus-selection logic (not `topological_order()`) decides which one to pursue and when. `topological_order()` remains useful for validation and for picking a reasonable *first* problem when there's no dialogue history yet to signal from. (The focus-selection logic itself — how "current signal" is represented and how "addressed" is detected — is the proprietary part above; this bullet is just the public-safe shape of how it plugs into `ConceptGraph`.)

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
- [x] First-version curriculum chosen and its concept graph created (algebra — linear equations, `socraticllm/curriculum/algebra_1.py`, `build_algebra_1()`)
- [ ] Student-side REPL wired end to end
- [ ] Metacognition layer implemented
- [ ] Curriculum ingestion pipeline (textbook upload -> concept graph extraction) implemented
- [ ] Teacher dashboard — explicitly deferred past v1
- [x] `REFERENCES.md` created (external articles supporting the problem statement); `VISION.md` points to it
- [x] References populated — 5 entries, added manually by the user (see session history below)
- [x] Questioning methodology distilled (attention loop + question-move palette) and kept proprietary — split into public generic `SYSTEM_PROMPT` + gitignored private overlay loaded at runtime (this session)
- [x] `ConceptGraph` sequencing decision made: readiness gate, not fixed walk order (this session)
- [ ] `Problem`/session model with focus state (current signal, addressed/slack status) — discussed and scoped this session, not yet built; blocks the REPL

**Last session (2026-07-23):** Picked up after the whole engine stack landed (2026-07-13, summarized below). Two parts: a methodology-architecture discussion, then an IP-protection correction on top of it.

1. **Questioning methodology review.** User distilled a specific epistemology in a separate session — an "attention loop" (find the loudest signal at the current resolution level → follow it down until addressed → introduce slack → let the next problem emerge honestly → never solve multiple threads at once) plus 7 named question-move patterns (principle-before-instance, surface-the-assumption, cross-domain transfer, gestalt-before-detail, stress-test-the-frame, temporal/cyclical awareness, force-naming). Reviewed all existing engine files against it; identified two layers (macro pacing loop vs. micro question-phrasing palette) sitting on top of the existing three Pedagogy principles, and flagged the tension between the loudest-signal method and `ConceptGraph`'s fixed prerequisite order.
2. **Sequencing decision:** `ConceptGraph` prerequisites act as a **readiness gate** (a concept can't be surfaced until its prerequisites are `recognized`), not an authoritative walk order — loudest-signal logic decides which unlocked concept to pursue and when. `topological_order()` still used for validation and picking a first problem with no history to signal from.
3. **Build sequence agreed:** (1) document the decision, (2) fold the methodology into `SYSTEM_PROMPT`, (3) design the `Problem`/session model with real focus state — cheapest/lowest-risk first.
4. **IP correction:** mid-session, user asked how to keep the methodology a business secret. Flagged that this repo is Apache 2.0 with a public GitHub remote (`github.com/otisranson/SocraticLLM`) — trade secret protection is incompatible with checking proprietary content into a publicly licensed repo, and the methodology had just been written into both `CLAUDE.md` and `dialogue.py`'s `SYSTEM_PROMPT`. User said to move it out; a separate private repo is planned eventually.
5. **Fix applied:** reverted `SYSTEM_PROMPT` to a generic, public-safe 3-rule version. Added `_load_methodology_overlay()` to `dialogue.py` — reads proprietary prompt content from a gitignored local path (`private/methodology_prompt.txt` by default, or `SOCRATICLLM_METHODOLOGY_PATH`) and appends it if present; the engine still works standalone with just the generic prompt if the file is absent. Wrote the methodology text to `private/methodology_prompt.txt`, added `/private/` to `.gitignore`, trimmed `CLAUDE.md`'s Pedagogy section to a pointer note (the readiness-gate decision stayed — general architecture, not proprietary content). Confirmed via `git check-ignore` that the private file isn't tracked. Committed (`edc3b79`) and pushed.

Also recorded, from the 2026-07-13 session, two forward-looking product ideas in Open Design Questions during a conversation about API key handling — not scoped for v1, just flagged so they aren't lost: a possible multi-tenant admin UI (teacher registration, IT-admin-configured key), and whether students need accounts at all versus an unauthenticated school-DNS-pointed deployment.

All work is committed and pushed; working tree is clean; 47 tests passing.

**Next task:** Design the `Problem`/session model with real focus state (current signal, addressed/slack status) — scoped in discussion this session (see the attention-loop / readiness-gate notes above) but not built. It unblocks the student-side REPL (`socraticllm/interface/repl.py`, `TODO.md` step 7): wire `build_algebra_1()` + student model + `DialogueEngine` + guardrail into one working loop, with session-end triggered by demonstrated recognition rather than a fixed script. Separately, and not blocking: the user still needs to create the private repo for `private/methodology_prompt.txt` — right now that file only exists on this machine, uncommitted anywhere.

<details>
<summary>Session history prior to 2026-07-23 (click to expand)</summary>

**2026-07-13:** Built out the whole engine stack from scratch, in order, each with passing tests before the next started. Prior sessions had reconciled the Socratic-tutor vision (`VISION.md`, this file, `TODO.md` rewritten to match; see git history around `90d1a72`/`9e5cc56`/`339915a` for that and the legacy-transformer extraction/concept-graph-schema detail) — this session picked up from there:

1. **`REFERENCES.md`** populated with 5 real entries (user did this manually after a `WebFetch` timeout on the first attempt); `VISION.md` points to it.
2. **Student state schema redesign** (`socraticllm/student/model.py`): `StudentState`/`CurriculumProgress`/`ConceptProgress` dataclasses, `concept_map` keyed dynamically off whatever `ConceptGraph` is active via `ensure_curriculum(graph)`, `load()`/`save()`. Renamed `learner/` → `student/` (no real data existed to migrate) resolving that naming question.
3. **LLM client wrapper** (`socraticllm/engine/llm_client.py`): `LLMClient.complete()`, a thin wrapper around `anthropic.Anthropic().messages.create()`, default model `claude-opus-4-8`, adaptive thinking on. Added `anthropic` as a real dependency.
4. **Guardrail** (`socraticllm/engine/guardrail.py`): the hard constraint from Core Design Decision #1. Flagged first that no `Problem`/expected-answer model exists yet to check content against; user agreed to scope this pass as **structural/heuristic** — `check(response)` flags responses *shaped* like a delivered answer (declarative "the answer is X", "Answer:" labels, multi-step walkthroughs), not their curriculum-specific correctness. Semantic follow-up noted in Open Design Questions.
5. **Dialogue engine** (`socraticllm/engine/dialogue.py`): `DialogueEngine.ask()` wires `LLMClient` + the guardrail into a turn loop, with a `SYSTEM_PROMPT` translating the Pedagogy section's three principles into model instructions, and retry-then-fallback on a guardrail rejection.
6. **Code review + fixes:** an 8-angle multi-agent review (high effort) on the dialogue-engine commit found 9 verified findings; fixed the 3 CONFIRMED correctness bugs — a dangling `self.history` entry when the LLM call raised mid-turn (broke the *next* turn's role alternation), an uncaught `StopIteration` in `LLMClient.complete()` when the model emitted no text block (now `NoTextResponseError`), and `FALLBACK_RESPONSE` bypassing the guardrail entirely (now checked too, with a `RuntimeError` safety net). Left 6 lower-priority findings (2 PLAUSIBLE, 4 CONFIRMED cleanup/altitude/efficiency) unfixed per the user's explicit "fix the confirmed bugs" scope — full list in Open Design Questions.
7. **First-version curriculum** (`socraticllm/curriculum/algebra_1.py`): asked the user which subject; chose algebra (linear equations) over "how LLMs work" — matches `VISION.md`'s own example and extends a shape already proven in `tests/test_concept_graph.py`'s fixture. `build_algebra_1()` returns a fresh, validated 8-concept `ConceptGraph` forming the recognition ladder from foundations (`variables`/`equality`/`inverse-operations`/`like-terms`) through `one-step` → `two-step` → `multi-step-equations` → `systems-of-equations`. Not yet wired into `DialogueEngine` at the time.

</details>

---

## Open Design Questions

- **Semantic guardrail follow-up.** `socraticllm/engine/guardrail.py`'s first pass is structural/heuristic (see Current State) — it can't check whether a response's content is factually the answer to the specific problem the student is working, only whether it's *shaped* like a delivered answer. A semantic check needs a `Problem`/expected-answer representation, which doesn't exist yet (no `Problem` class in `curriculum/`, no per-session "current problem" in `student/`). Whether to add an LLM-judge-based semantic layer on top of the heuristic pass, and what that representation looks like, is open — likely to surface again once `student/session.py` ("one problem -> dialogue -> session lifecycle") is built.
- **Unfixed code-review findings on `dialogue.py`.** A code review after the dialogue engine landed found 3 CONFIRMED correctness bugs (fixed, see Current State) plus 6 more findings deliberately left alone since the user asked only for "the confirmed bugs": (1) `self._llm = llm_client or LLMClient()` uses `x or default()`, which would silently discard an injected client that happens to be falsy — PLAUSIBLE, no current caller triggers it; (2) the guardrail-retry correction is injected as a `{"role": "user", ...}` message, misattributing an operator-level correction to the student — PLAUSIBLE, and not a trivial fix since the Claude API's mid-conversation `role: "system"` alternative requires the message to directly follow a `user` turn, which the current retry sequence doesn't; (3) retry-then-fallback orchestration lives in `DialogueEngine.ask()` rather than on `guardrail.py` itself, so a second caller of `check()` would have to reimplement it; (4) the full conversation history is resent on every turn and every retry with no truncation or Anthropic prompt caching; (5) `FALLBACK_RESPONSE` is always the identical string regardless of context or repeat exposure; (6) the retry loop's manual counter/`while True` could be a `for attempt in range(...)` and the success/fallback branches duplicate an append-then-return shape. None of these are blocking; worth revisiting before the `interface/repl.py` step if a real student conversation will actually exercise long sessions.
- **API key management, and whether an admin UI/role is needed.** For v1, the LLM API key is a single environment variable (the `anthropic` SDK resolves `ANTHROPIC_API_KEY` from the environment automatically — no code change needed) — fine for a single-deployment, single-key setup. The user is considering a further-out model: multiple teachers register, an IT-administrator role configures the LLM API key (and presumably approves/manages teachers), which implies multi-tenancy the current design doesn't have — curricula are keyed by `curriculum_id` only, with no owning-teacher or owning-org concept. This is explicitly **not** v1 scope; noted here so it isn't lost, not because it should influence current TODO ordering.
- **Whether students need to register at all.** The user's current thinking: no per-student account/login — instead, a school points internal DNS at the deployment and students just start a conversation. This is in tension with Core Design Decision #2 (persistent per-student model, scoped per curriculum, keyed by `student_id` in the schema) — some identifier still has to tie a conversation back to a specific student's history across sessions, even without a formal registration flow. Candidate approaches (none chosen): a device-local identifier (browser storage/cookie, no login), the school's existing SSO/roster feeding an identifier without SocraticLLM ever handling credentials, or a lightweight name/ID prompt with no password. Affects the `student_id` field in the Student State Schema above and the eventual `interface/repl.py` (or web equivalent) — flagging now, not deciding now.

---

## Working Conventions

- Update the "Current State" checklist and "Last session" note at the end of every session.
- Don't start a new component until the previous one has a passing test.
- When uncertain about a design decision, flag it explicitly rather than picking arbitrarily — add to `## Open Design Questions` above.
