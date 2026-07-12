# SocraticLLM

## Vision

A Socratic tutor that teaches students how to think, not what to answer. Designed for STEM and the Trivium — any domain where real learning is recognition and application, not memorization and retrieval.

Named after Socrates, who never gave answers. He asked questions until the student discovered what they already knew — or caught themselves not knowing what they thought they did. The method was the lesson.

## The Core Problem

AI has collapsed the distance between not knowing and having the answer. A student can paste an algebra problem and get a solution in seconds. Tests were already a weak proxy for learning. Now they're nearly meaningless.

The solution is not to block AI. It's to build an AI that cannot be shortcut — because the path through it *is* the learning.

## Core Constraint

**The system never gives the answer. It only gives the next question.**

A student who can recognize "this is a linear equation and I'm isolating a variable" before touching the algebra has learned something a student who just executes steps hasn't. Recognition is the real learning. Execution is almost incidental.

## What It Actually Teaches

Not answers. Not formulas. **Recognition and transfer.**

- Physics isn't memorizing F = ma. It's recognizing which problems F = ma applies to.
- Algebra isn't executing steps. It's identifying what kind of problem you're looking at.
- Logic isn't remembering fallacy names. It's spotting the structure of an argument.
- Rhetoric isn't vocabulary. It's reading what a situation calls for.

Tests measure retrieval. This measures transfer — the ability to apply knowledge in contexts you haven't seen before. That's the thing education has always struggled to develop, and almost never measures.

## Metacognition as a First-Class Feature

The system's primary goal is to make the student aware of their own learning.

Not through dashboards or progress bars — those are hollow and students see through them. Through *engineered moments of self-discovery*: handing a student back a problem they struggled with three weeks ago and watching them solve it in two minutes. Asking a question that makes them realize they know something they didn't know they knew.

The awareness is not delivered. It is provoked.

## Two Surfaces, One Engine

**Student side — the Socratic tutor**
- Student inputs a problem
- System classifies the concept domain internally (never tells the student)
- Dialogue begins: questions only, no answers
- System guides the student to recognize the problem type and appropriate approach
- Session ends when the student has demonstrated recognition
- Over time, builds a persistent model of this student's patterns — where they stall, where they reach for the wrong tool, when they're ready for something harder

**Teacher side — curriculum scaffolding**
- Teacher uploads their textbook. The system extracts the concept map: problem types, domains, prerequisites, sequencing. The teacher does not build this manually.
- Teacher does not write questions — the system handles dialogue
- The teacher's remaining job is the human one: understanding where their students are mentally. Not who got the right answer — who is stuck at recognition, who is ready to go deeper, who is applying the right tool to the wrong problem type.
- That's information standardized testing has never provided, and it's the information a good teacher actually needs

## Domain Focus

- **STEM** — mathematics, physics, chemistry, biology. Anywhere formulas exist to be applied, not memorized.
- **Trivium** — grammar, logic, rhetoric. The classical framework for structured thought.

Designed to integrate into existing educational institutions. Schools do not have to abandon their curriculum. They plug this in for the part standardized education was never good at: the individual, longitudinal relationship with a specific student's mind.

## Architecture (Conceptual)

- A concept graph per domain, defined or imported by the teacher
- A student model, updated per session, tracking recognition patterns not scores
- A dialogue engine with one hard constraint: questions only
- A metacognitive layer that engineers moments of self-discovery, not reports on progress

## What Makes This Different

Every other AI tutor is a sophisticated answer machine. This one is structurally incapable of being one. The Socratic constraint is not a feature — it is the architecture.

## First Version

One subject. One concept domain. One student flow.

Algebra: student inputs a problem, system guides them through recognition via dialogue, session ends when student has identified problem type and approach. No teacher dashboard yet. No longitudinal tracking. Just prove the dialogue works.

## Influences

- **Socrates** — never wrote anything down, taught entirely through questions, made the student do the work of arriving at the answer
- **Feynman** — if you can't explain it simply, you don't understand it
- **The Trivium** — grammar, logic, rhetoric as a framework for structured thought, not a set of rules to memorize
- **Euclid** — progressive disclosure, every theorem earned before the next is introduced

## License

Apache 2.0 — permissive, patent grant included, no friction for researchers or educators.

