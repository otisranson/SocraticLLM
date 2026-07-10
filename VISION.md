# SocraticLLM

## Vision

An educational LLM that exposes its own internals as you interact with it. Not just a model — a window into one. Named after Socrates, who made the *process* of thinking visible rather than just producing answers.

## Core Concept

A didactic transformer — architecturally honest, small enough to run on a laptop, big enough to be coherent. Every component implemented from scratch and instrumented to narrate itself.

## Progressive Disclosure (Core Design Principle)

The system teaches you until you don't need the teaching anymore, then gets out of the way.

- **Novice mode** — every layer explained, annotated, visual. Tokens forming, attention weights lighting up, probability distributions collapsing into word choices
- **Intermediate mode** — summarizes rather than narrates. Shows the interesting parts, skips the mechanical ones
- **Expert mode** — clean output. The instrumentation is always one click away if you want to dive back in

## Audience

Primary: curious people with a CS background who haven't touched ML yet. Secondary: non-technical people who want to understand what an LLM actually is.

## Architecture

Build every component from scratch, small but real:

1. **Tokenizer** — how raw text becomes tokens
2. **Embeddings** — how tokens become vectors
3. **Attention heads** — how the model relates tokens to each other
4. **Feed-forward layers** — transformation at each position
5. **Softmax sampling** — how the probability distribution collapses into a word choice
6. **Output** — how it all comes together

Each component:
- Is implemented honestly (no black boxes)
- Can narrate what it's doing
- Can be inspected on demand
- Gets quieter as the user learns

## Interactive Experience

Two modes working together:

1. **The artifact is the explanation** — as you type a prompt, it shows what's happening at each stage in real time alongside the output
2. **Guided curriculum** — work through concepts sequentially; the interactive model is the teaching tool at each stage

## License

Apache 2.0 — permissive, patent grant included, no friction for researchers or collaborators.

## Influences

- **Socrates** — taught through exposure, made the process visible, never claimed to know everything
- **Feynman** — if you can't explain it simply, you don't understand it
- **Paracelsus** — direct observation over received authority
- **Euclid** — progressive disclosure, every theorem earned before the next is introduced

## Named After

Socrates — who never wrote anything down, taught entirely through questions, and made the student do the work of arriving at the answer. The method *was* the lesson.

## Next Steps

1. Draft README
2. Define repo structure
3. Build tokenizer first — it's the most visual and tangible entry point
4. Instrument each layer as it's built
5. Build the progressive disclosure UI last
