import numpy as np

from socraticllm.model import Embeddings


def test_output_shape():
    embeddings = Embeddings(vocab_size=100, d_model=16, max_seq_len=32)
    token_ids = np.array([1, 2, 3])
    out = embeddings.forward(token_ids)
    assert out.shape == (3, 16)
