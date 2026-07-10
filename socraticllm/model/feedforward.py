"""Position-wise feed-forward layer: the per-token transformation between attention layers."""

import numpy as np

from socraticllm.narration.narrator import Narrator


class FeedForward:
    """Two linear projections with a nonlinearity, applied independently per position."""

    def __init__(self, d_model: int, d_ff: int, narrator: Narrator | None = None):
        self.narrator = narrator or Narrator()
        self.d_model = d_model
        self.d_ff = d_ff

    def forward(self, x: np.ndarray) -> np.ndarray:
        raise NotImplementedError
