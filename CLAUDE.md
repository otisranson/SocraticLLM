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
├── learner/                     # existing student-state persistence; schema below needs a redesign pass (see Open Design Questions)
│   ├── state.json
│   └── history/
└── tests/
```

---

## Student State Schema (redesign in progress)

`learner/state.json` (path may move to `student/state.json` to match the vocabulary above — undecided) is injected into each session. The prior schema hardcoded a 5-item concept map (tokenization/embeddings/attention/feedforward/softmax) tied to the old vision. Since curriculum is now pluggable, the concept map must be keyed dynamically off whatever concept graph is active, and scoped per curriculum since a student may work through more than one.

Proposed shape — **not yet implemented, not yet reconciled with the file that already exists on disk** (which still has the old fixed schema):

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
- [ ] Remaining Open Design Questions below resolved
- [ ] Repo restructured to target shape (`engine/`, `curriculum/`, `student/`, `teacher/`, `interface/`) — `curriculum/` started, rest not yet
- [x] Concept graph schema defined (`socraticllm/curriculum/concept_graph.py` — `Concept`, `ConceptGraph`; add/get, prerequisite lookup, cycle + dangling-reference validation, topological ordering; tests passing)
- [ ] Student state schema redesigned and `learner/state.json` migrated (or moved) to it
- [ ] LLM client wrapper implemented
- [ ] Dialogue engine + guardrail (the hard constraint) implemented
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

**Next task:** Student state schema — redesign `learner/state.json` so `concept_map` keys
reference `ConceptGraph` concept ids per curriculum (see the proposed shape in the Student State
Schema section above) rather than the old fixed 5-key map, and implement load/save. See `TODO.md`
step 3.

---

## Open Design Questions

- **`learner/` vs `student/` naming**, and whether the existing `learner/state.json` (old fixed schema, already has one real entry with `last_updated: 2026-07-12`) gets migrated or replaced.
- **First-version curriculum scope.** `VISION.md`'s "First Version" section names algebra as the example; the user has since clarified the domain is generic (e.g. a book on LLMs would work equally). Still open: whether v1 hand-authors a small concept graph directly (fastest path to proving the dialogue constraint) or builds the ingestion/extraction pipeline first. Leaning toward hand-authoring first, per `VISION.md`'s own "just prove the dialogue works" framing, but not decided.

---

## Working Conventions

- Update the "Current State" checklist and "Last session" note at the end of every session.
- Don't start a new component until the previous one has a passing test.
- When uncertain about a design decision, flag it explicitly rather than picking arbitrarily — add to `## Open Design Questions` above.
