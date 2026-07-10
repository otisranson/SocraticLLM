"""Byte-pair-encoding tokenizer, implemented explicitly so its merges are inspectable."""

from socraticllm.narration.narrator import Narrator


class BPETokenizer:
    """Learns and applies byte-pair merges over raw text."""

    def __init__(self, narrator: Narrator | None = None):
        self.narrator = narrator or Narrator()
        self.merges: dict[tuple[str, str], str] = {}
        self.vocab: dict[str, int] = {}

    def train(self, corpus: str, vocab_size: int) -> None:
        tokens = list(corpus)
        self.vocab = {tok: i for i, tok in enumerate(sorted(set(tokens)))}
        self.merges = {}

        while len(self.vocab) < vocab_size:
            pair_counts = self._count_pairs(tokens)
            if not pair_counts:
                break
            best_pair = max(pair_counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
            merged = best_pair[0] + best_pair[1]
            self.merges[best_pair] = merged
            self.vocab.setdefault(merged, len(self.vocab))
            tokens = self._apply_merge(tokens, best_pair, merged)

    def encode(self, text: str) -> list[int]:
        merge_rank = {pair: rank for rank, pair in enumerate(self.merges)}
        tokens = list(text)

        while True:
            pairs_present = [pair for pair in zip(tokens, tokens[1:]) if pair in merge_rank]
            if not pairs_present:
                break
            best_pair = min(pairs_present, key=lambda pair: merge_rank[pair])
            tokens = self._apply_merge(tokens, best_pair, self.merges[best_pair])

        return [self.vocab[tok] for tok in tokens]

    def decode(self, ids: list[int]) -> str:
        id_to_token = {i: tok for tok, i in self.vocab.items()}
        return "".join(id_to_token[i] for i in ids)

    @staticmethod
    def _count_pairs(tokens: list[str]) -> dict[tuple[str, str], int]:
        counts: dict[tuple[str, str], int] = {}
        for pair in zip(tokens, tokens[1:]):
            counts[pair] = counts.get(pair, 0) + 1
        return counts

    @staticmethod
    def _apply_merge(tokens: list[str], pair: tuple[str, str], merged: str) -> list[str]:
        result = []
        i = 0
        while i < len(tokens):
            if i < len(tokens) - 1 and (tokens[i], tokens[i + 1]) == pair:
                result.append(merged)
                i += 2
            else:
                result.append(tokens[i])
                i += 1
        return result
