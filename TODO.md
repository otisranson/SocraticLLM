# TODO

Vision pivoted (2026-07-12) from a self-narrating, from-scratch transformer to a Socratic
dialogue tutor. See `VISION.md` and `CLAUDE.md` for the full story. Everything below is the
build order for the *new* direction — none of it has started. The old build order (tokenizer ->
embeddings -> attention -> feedforward -> softmax -> transformer -> narrator) is superseded; that
code has been extracted with history to a standalone repo at `~/Projects/didactic-transformer`
and removed from here entirely.

Build in this order — each step unblocks the next:

1. **Resolve the remaining Open Design Question in `CLAUDE.md`** — the `learner/` vs `student/`
   naming, and whether `learner/state.json` (old fixed schema) gets migrated or replaced.
2. **Concept graph schema** — `socraticllm/curriculum/concept_graph.py`. Define `Concept`,
   `Prerequisite`, `Domain` (or equivalent). This is the foundation: the student model's
   `concept_map` keys reference these nodes, and the dialogue engine classifies problems against
   this graph. Everything else depends on its shape.
3. **Student state schema + persistence** — redesign `learner/state.json` per the proposed
   shape in `CLAUDE.md` (dynamic, per-curriculum `concept_map` instead of the old fixed 5-key
   one). Implement load/save.
4. **LLM client wrapper** — `socraticllm/engine/llm_client.py`. Thin wrapper around the API
   call used for dialogue. No model-internals work here — confirmed the dialogue engine calls an
   existing LLM API, not a self-hosted model.
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

- This machine has no pip/ensurepip; `python3 -m venv` fails because `python3.14-venv` isn't
  installed (`apt install python3.14-venv`, needs sudo). Still unresolved from the prior effort —
  will matter again once there's new code to test.
