"""Token and positional embeddings: how discrete tokens become vectors."""

import numpy as np

from socraticllm.narration.narrator import Narrator


class Embeddings:
    """Looks up a learned vector per token and adds a positional signal."""

    def __init__(self, vocab_size: int, d_model: int, max_seq_len: int, narrator: Narrator | None = None):
        self.narrator = narrator or Narrator()
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.max_seq_len = max_seq_len
        self.token_embeddings: np.ndarray | None = None
        self.position_embeddings: np.ndarray | None = None

    def forward(self, token_ids: np.ndarray) -> np.ndarray:
        raise NotImplementedError
