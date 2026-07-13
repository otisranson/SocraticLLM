# TODO

Vision pivoted (2026-07-12) from a self-narrating, from-scratch transformer to a Socratic
dialogue tutor. See `VISION.md` and `CLAUDE.md` for the full story. Everything below is the
build order for the *new* direction — none of it has started. The old build order (tokenizer ->
embeddings -> attention -> feedforward -> softmax -> transformer -> narrator) is superseded; that
code has been extracted with history to a standalone repo at `~/Projects/didactic-transformer`
and removed from here entirely.

Build in this order — each step unblocks the next:

1. **`learner/` vs `student/` naming** — done. Renamed `learner/` to `student/`; no real data
   existed in the old `learner/state.json` to migrate.
2. **Concept graph schema** — done. `socraticllm/curriculum/concept_graph.py`: `Concept`
   (id, name, description, `domain` tag, `prerequisites` as a list of concept ids) and
   `ConceptGraph` (add/get, `prerequisites_of`, `validate()` for dangling refs and cycles,
   `topological_order()`). No separate `Prerequisite`/`Domain` classes — deferred until they need
   their own fields. `tests/test_concept_graph.py` passing (9 cases).
3. **Student state schema + persistence** — done. `socraticllm/student/model.py`: `StudentState`,
   `CurriculumProgress`, `ConceptProgress` dataclasses, dynamic per-curriculum `concept_map`
   keyed off `ConceptGraph` concept ids (via `ensure_curriculum()`), `load()`/`save()`.
   `tests/test_student_model.py` passing (4 cases).
4. **LLM client wrapper** — done. `socraticllm/engine/llm_client.py`: `LLMClient`, a thin wrapper
   around `anthropic.Anthropic().messages.create()` (default model `claude-opus-4-8`, adaptive
   thinking on). `anthropic` added as a real dependency. `tests/test_llm_client.py` passing
   (2 cases, injectable fake client — no real API calls in tests).
5. **Dialogue engine + guardrail** — `socraticllm/engine/dialogue.py` and
   `socraticllm/engine/guardrail.py`. The guardrail enforces the hard constraint (no answer ever
   leaves this layer) — this is the core differentiator and should be solid, with real test
   cases of leaked-answer attempts, before anything user-facing is built on top of it.
6. **First-version curriculum content.** Hand-author a small concept graph for one subject
   directly (skip the ingestion pipeline for now) — fastest path to proving the dialogue
   constraint works end to end, per `VISION.md`'s own "First Version" framing. Which subject is
   still open (algebra was the example in `VISION.md`; not a requirement).
7. **Student-side interface** — `socraticllm/interface/repl.py`. Wire concept graph + student
   model + dialogue engine + guardrail together into one working loop: student states a problem,
   dialogue proceeds via questions only, session ends on demonstrated recognition, student state
   updates.
8. **Metacognition layer** — `socraticllm/engine/metacognition.py`. Only once step 7 produces
   real session history to work with: engineer self-discovery moments (e.g. resurface a problem
   the student struggled with previously).
9. **Curriculum ingestion pipeline** — `socraticllm/curriculum/ingest.py` (textbook upload ->
   text extraction) and the concept-graph extraction logic in `concept_graph.py`. Teacher-side;
   comes after the student-side loop is proven per `VISION.md`'s deferred-teacher-dashboard
   scoping.
10. **Teacher dashboard** — `socraticllm/teacher/dashboard.py`. Explicitly deferred past v1;
    no timeline yet.

## Environment

- A working `.venv` (with pytest) already exists at the repo root and was used to install the
  package (`pip install -e .`) and run tests. The venv-creation issue noted here by the prior
  effort appears resolved — leaving this note in case it resurfaces.
