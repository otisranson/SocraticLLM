import numpy as np

from socraticllm.model import Transformer


def test_logits_shape():
    model = Transformer(
        vocab_size=100, d_model=16, n_heads=4, d_ff=64, n_layers=2, max_seq_len=32
    )
    token_ids = np.array([1, 2, 3])
    logits = model.forward(token_ids)
    assert logits.shape == (3, 100)
