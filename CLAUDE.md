# CLAUDE.md — SocraticLLM

This file is read by Claude Code at session start. It is the source of truth for project state, decisions, and next steps. Update it after each meaningful session.

---

## What This Project Is

SocraticLLM is an educational transformer implementation that exposes its own internals as a user interacts with it. Every component is built from scratch and instrumented to narrate what it's doing. The goal is not just to show how transformers work — it's to make the learner's growing understanding visible to themselves.

Full vision: `VISION.md`

---

## Core Design Decisions (do not relitigate without flagging)

**1. Persistent learner state is the primary product.**
The model doesn't change through interaction — the learner does. That change should be made explicit: a structured learner profile tracks concept exposure, confidence, and friction points. It gets injected into each session as context and displayed to the learner so they can watch their own conceptual map evolve. Schema lives at `learner/state.json`.

**2. Progressive disclosure over fixed curriculum.**
The system adapts verbosity to the learner's state. Three modes: novice (everything narrated), intermediate (summarized), expert (clean output, instrumentation one click away). The learner's `disclosure_level` in state.json drives this.

**3. Build order follows conceptual dependency.**
Tokenizer → Embeddings → Attention → Feed-forward → Softmax → Output. Don't skip ahead. Each component must be instrumented before the next is started.

**4. No black boxes.**
Every component is implemented from scratch in Python. No importing `transformers` or similar. NumPy and PyTorch for tensor ops only.

**5. Python, small but real.**
Small enough to run on a laptop CPU. Big enough to produce coherent (if limited) output. Exact model size TBD — decide when embeddings are scoped.

---

## Repo Structure (target)

```
SocraticLLM/
├── CLAUDE.md               # this file
├── VISION.md               # full project vision
├── README.md               # not yet written
├── learner/
│   ├── state.json          # persistent learner state (see schema below)
│   └── history/            # per-session snapshots of state.json
├── model/
│   ├── tokenizer.py        # component 1
│   ├── embeddings.py       # component 2
│   ├── attention.py        # component 3
│   ├── feedforward.py      # component 4
│   ├── softmax.py          # component 5
│   └── model.py            # assembles components
├── narration/
│   └── narrator.py         # the instrumentation layer; wraps each component
├── ui/
│   └── ...                 # progressive disclosure UI — build last
├── tests/
│   └── ...
└── requirements.txt
```

---

## Learner State Schema

`learner/state.json` is injected into each session and updated at the end. It is also surfaced in the UI so learners can inspect their own progress.

```json
{
  "learner_state": {
    "version": "0.1",
    "last_updated": "",
    "session_count": 0,

    "concept_map": {
      "tokenization": {
        "status": "not_yet",
        "confidence": null,
        "notes": null
      },
      "embeddings": {
        "status": "not_yet",
        "confidence": null,
        "notes": null
      },
      "attention": {
        "status": "not_yet",
        "confidence": null,
        "notes": null
      },
      "feedforward": {
        "status": "not_yet",
        "confidence": null,
        "notes": null
      },
      "softmax": {
        "status": "not_yet",
        "confidence": null,
        "notes": null
      }
    },

    "friction_log": [],

    "open_questions": [],

    "preferred_explanation_style": {
      "analogies": null,
      "math": null,
      "code": null
    },

    "disclosure_level": "novice"
  }
}
```

`status` values: `not_yet` | `encountered` | `working`
`confidence` values: `low` | `medium` | `high` | `null`

---

## Current State

- [ ] VISION.md written ✓
- [ ] CLAUDE.md written ✓
- [ ] Repo structure created
- [ ] `learner/state.json` initialized
- [ ] Tokenizer implemented
- [ ] Tokenizer instrumented
- [ ] README written

**Last session:** Designed learner state schema and CLAUDE.md structure. Identified persistent learner state as the core product insight, not a side feature.

**Next task:** Scaffold the repo directory structure, initialize `learner/state.json`, then begin `model/tokenizer.py`.

---

## Working Conventions

- Update the "Current State" checklist and "Last session" note at the end of every session.
- Don't start a new component until the previous one has a passing test and working narration hook.
- When uncertain about a design decision, flag it explicitly rather than picking arbitrarily. Add a `## Open Design Questions` section below if needed.

