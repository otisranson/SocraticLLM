"""Scaled dot-product and multi-head attention: how tokens relate to each other."""

import numpy as np

from socraticllm.narration.narrator import Narrator


def scaled_dot_product_attention(
    query: np.ndarray, key: np.ndarray, value: np.ndarray, mask: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (output, attention_weights) so the weights can be narrated/visualized."""
    raise NotImplementedError


class MultiHeadAttention:
    """Runs several attention heads in parallel and combines their outputs."""

    def __init__(self, d_model: int, n_heads: int, narrator: Narrator | None = None):
        self.narrator = narrator or Narrator()
        self.d_model = d_model
        self.n_heads = n_heads

    def forward(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        raise NotImplementedError
