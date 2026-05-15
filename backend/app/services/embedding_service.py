import hashlib
import math
import re
from collections.abc import Iterable


EMBEDDING_DIMENSION = 384


def _tokenize(text: str) -> list[str]:
    normalized = text.lower()
    tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", normalized)
    bigrams = [
        f"{tokens[index]}{tokens[index + 1]}"
        for index in range(len(tokens) - 1)
        if re.fullmatch(r"[\u4e00-\u9fff]", tokens[index])
        and re.fullmatch(r"[\u4e00-\u9fff]", tokens[index + 1])
    ]
    return tokens + bigrams


def _stable_index(token: str) -> int:
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % EMBEDDING_DIMENSION


def embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIMENSION
    tokens = _tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        vector[_stable_index(token)] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [embed_text(text) for text in texts]


class SimpleEmbeddingFunction:
    def __call__(self, input: Iterable[str]) -> list[list[float]]:
        return embed_texts(list(input))
