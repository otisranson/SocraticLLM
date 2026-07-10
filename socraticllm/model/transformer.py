"""Wires embeddings, attention, and feed-forward blocks into a full forward pass."""

import numpy as np

from socraticllm.narration.narrator import Narrator
from .embeddings import Embeddings
from .attention import MultiHeadAttention
from .feedforward import FeedForward


class TransformerBlock:
    """One layer: attention followed by a feed-forward transformation, with residuals."""

    def __init__(self, d_model: int, n_heads: int, d_ff: int, narrator: Narrator | None = None):
        self.narrator = narrator or Narrator()
        self.attention = MultiHeadAttention(d_model, n_heads, narrator=self.narrator)
        self.feedforward = FeedForward(d_model, d_ff, narrator=self.narrator)

    def forward(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        raise NotImplementedError


class Transformer:
    """Stacks TransformerBlocks and projects to vocabulary logits."""

    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        n_heads: int,
        d_ff: int,
        n_layers: int,
        max_seq_len: int,
        narrator: Narrator | None = None,
    ):
        self.narrator = narrator or Narrator()
        self.embeddings = Embeddings(vocab_size, d_model, max_seq_len, narrator=self.narrator)
        self.blocks = [
            TransformerBlock(d_model, n_heads, d_ff, narrator=self.narrator) for _ in range(n_layers)
        ]

    def forward(self, token_ids: np.ndarray) -> np.ndarray:
        """Returns logits over the vocabulary for the next token at each position."""
        raise NotImplementedError
