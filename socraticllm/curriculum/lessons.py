"""Sequential guided-curriculum content, keyed to the components in socraticllm.model.

Ordering follows VISION.md's architecture list: tokenizer, embeddings, attention,
feed-forward, softmax, output. Each lesson references the component it's teaching so
the curriculum stays in sync with the code rather than drifting into its own narrative.
"""

LESSONS: list[dict] = []
