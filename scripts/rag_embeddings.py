import hashlib
import math
import re
from typing import Iterable


class HashNgramEmbeddingFunction:
    """Deterministic local embeddings for offline Chroma retrieval.

    This is intentionally dependency-light and reproducible. It works well for
    regulation lookup where exact terms, article numbers, and short Chinese
    phrases matter. A later skill can swap in a stronger embedding model while
    keeping the same Chroma metadata contract.
    """

    def __init__(self, dimensions: int = 1024):
        self.dimensions = dimensions

    def name(self) -> str:
        return f"hash_ngram_{self.dimensions}"

    def __call__(self, input: Iterable[str]) -> list[list[float]]:
        return [self._embed(text or "") for text in input]

    def embed_documents(self, input: Iterable[str]) -> list[list[float]]:
        return self(input)

    def embed_query(self, input: Iterable[str]) -> list[list[float]]:
        return self(input)

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        tokens = list(self._tokens(text))
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            idx = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            weight = 1.0 + min(len(token), 8) / 8.0
            vec[idx] += sign * weight
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _tokens(self, text: str):
        text = re.sub(r"\s+", "", text.lower())
        for m in re.finditer(r"[a-z0-9_./-]{2,}", text):
            yield m.group(0)
        chars = [c for c in text if "\u4e00" <= c <= "\u9fff"]
        for n in (2, 3, 4):
            for i in range(0, max(0, len(chars) - n + 1)):
                yield "".join(chars[i : i + n])
        for m in re.finditer(r"第[一二三四五六七八九十百千万零〇\d]+条", text):
            yield m.group(0)
