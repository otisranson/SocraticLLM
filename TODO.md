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
5. **Guardrail** — first pass done. `socraticllm/engine/guardrail.py`: `check(response)` /
   `GuardrailResult`, structural/heuristic (declarative "the answer is"/"the solution is"
   phrasing, "Answer:"/"Final answer:" labels, "so/therefore the answer..." conclusions,
   multi-step "Step 1: ... Step 2: ..." walkthroughs). No `Problem`/expected-answer model exists
   yet, so this pass checks the *shape* of a response, not whether its content is factually the
   answer to a specific problem — a semantic, LLM-judge-based layer is a deliberate follow-up
   (see CLAUDE.md's Open Design Questions). `tests/test_guardrail.py` passing (17 cases: 11
   leaked-answer attempts rejected, 6 legitimate Socratic responses passed).
   **Dialogue engine** — `socraticllm/engine/dialogue.py`, still to do: wires `LLMClient` +
   the guardrail + the concept graph into a turn loop, including a retry strategy for guardrail
   rejections (not yet designed).
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
