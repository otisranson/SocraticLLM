"""Softmax and sampling: how a probability distribution collapses into a word choice."""

import numpy as np

from socraticllm.narration.narrator import Narrator


def softmax(logits: np.ndarray, axis: int = -1) -> np.ndarray:
    raise NotImplementedError


def sample(
    probabilities: np.ndarray,
    temperature: float = 1.0,
    top_k: int | None = None,
    top_p: float | None = None,
    narrator: Narrator | None = None,
) -> int:
    """Collapses a distribution into a single token id, narrating the choice if asked."""
    raise NotImplementedError
