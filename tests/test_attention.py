import numpy as np

from socraticllm.model import MultiHeadAttention


def test_output_shape_matches_input():
    attention = MultiHeadAttention(d_model=16, n_heads=4)
    x = np.random.randn(5, 16)
    out = attention.forward(x)
    assert out.shape == x.shape
