import numpy as np

from socraticllm.model import FeedForward


def test_output_shape_matches_input():
    ff = FeedForward(d_model=16, d_ff=64)
    x = np.random.randn(5, 16)
    out = ff.forward(x)
    assert out.shape == x.shape
