from socraticllm.tokenizer import BPETokenizer


def test_encode_decode_roundtrip():
    tokenizer = BPETokenizer()
    tokenizer.train(corpus="the quick brown fox", vocab_size=50)
    ids = tokenizer.encode("the quick fox")
    assert tokenizer.decode(ids) == "the quick fox"
