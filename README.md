# SocraticLLM

A Socratic tutor: a dialogue system that never gives the answer, only the next question.

Most AI tutors are answer machines wearing a friendly voice. SocraticLLM is structurally
incapable of being one — the constraint is architectural, not a prompt suggestion. A student
brings a problem; the system guides them toward *recognizing* what kind of problem it is and what
approach applies, through questions alone. Execution is almost incidental. Recognition is the
thing that transfers to problems the student hasn't seen before, which is what tests have never
been able to measure.

## How it works

- **Student side** — a student states a problem. The system classifies the concept domain
  internally (never revealed) and runs a dialogue with one hard rule: questions only. The session
  ends when the student demonstrates recognition. Over time, a persistent model of that student
  builds up — not scores, but where they stall, where they reach for the wrong tool, when they're
  ready for something harder.
- **Teacher side** — a teacher uploads their own textbook. The system extracts the concept graph
  (problem types, prerequisites, sequencing) from it, so the curriculum is whatever the teacher
  actually teaches, not a fixed subject list. The teacher's job becomes the human one: seeing
  where their students are stuck at recognition versus ready to go deeper.

Full vision: [`VISION.md`](VISION.md).

## Status

Early. The vision and architecture are settled; the dialogue engine, concept-graph extraction,
and student model are not yet built. See [`TODO.md`](TODO.md) for the build order and
[`CLAUDE.md`](CLAUDE.md) for current state and open design questions.

An earlier direction for this repo — a from-scratch, self-narrating transformer — has been
extracted to its own project and is no longer part of this one.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
