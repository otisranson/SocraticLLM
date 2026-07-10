# TODO

Repo scaffold is done (see `socraticllm/`, `tests/`, `examples/repl.py`, `pyproject.toml`).
Everything below is a stub raising `NotImplementedError`. Build in this order —
each step unblocks the next:

1. **Tokenizer** — `socraticllm/tokenizer/bpe.py`. Implement `train()`, `encode()`, `decode()`.
   First per VISION.md: "most visual and tangible entry point." Check against
   `tests/test_tokenizer.py`.
2. **Embeddings** — `socraticllm/model/embeddings.py`. `Embeddings.forward()`: token lookup
   + positional embedding. Check against `tests/test_embeddings.py`.
3. **Attention** — `socraticllm/model/attention.py`. `scaled_dot_product_attention()` (return
   weights too, needed for narration/visualization later) and `MultiHeadAttention.forward()`.
   Check against `tests/test_attention.py`.
4. **Feed-forward** — `socraticllm/model/feedforward.py`. `FeedForward.forward()`: two linear
   projections + nonlinearity, per-position. Check against `tests/test_feedforward.py`.
5. **Softmax/sampling** — `socraticllm/model/softmax.py`. `softmax()` (numerically stable) and
   `sample()` with temperature/top-k/top-p. Check against `tests/test_softmax.py`.
6. **Wire up Transformer** — `socraticllm/model/transformer.py`. `TransformerBlock.forward()`
   (attention + residual + feed-forward + residual) and `Transformer.forward()` (embeddings ->
   blocks -> logits). Depends on steps 2-4. Check against `tests/test_transformer.py`.
7. **Narration hooks** — `socraticllm/narration/narrator.py`. Implement `Narrator.report()`
   branching on `DisclosureLevel` (novice=full explanation, intermediate=summary, expert=silent).
   Then add `narrator.report(...)` calls at meaningful points in every component above.
8. **Curriculum content** — `socraticllm/curriculum/lessons.py`. Populate `LESSONS` with
   sequential lessons keyed to each component, per VISION.md's guided-curriculum concept.
9. **Environment fix** — this machine has no pip/ensurepip; `python3 -m venv` fails because
   `python3.14-venv` isn't installed (`apt install python3.14-venv`, needs sudo). Resolve this
   so `pip install -e .[dev]` works, then run `pytest` and confirm everything passes for real
   (so far only syntax-checked via `py_compile`, never executed).
10. **Progressive-disclosure UI/artifact** — build *last*, per VISION.md's own Next Steps,
    once every component is implemented and instrumented. Two parts: (a) live artifact showing
    each stage as a prompt is typed, (b) guided curriculum walking through concepts sequentially.

These same 10 items are also tracked as tasks #1-#10 in this session's task list
(`TaskList` tool) if you're continuing in the same Claude Code session — this file is the
backup in case you're starting fresh.
