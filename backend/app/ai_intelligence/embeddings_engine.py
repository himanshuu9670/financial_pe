"""Lightweight transaction embeddings for search and duplicate detection."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from app.ai_intelligence.semantic_parser import parse_semantic
from app.shared.models import StructuredTransaction


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def embed_text(text: str, dim: int = 64) -> list[float]:
    """Hash-trick embedding — no external ML model required."""
    tokens = _tokenize(text)
    vec = [0.0] * dim
    if not tokens:
        return vec
    for tok in tokens:
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


class EmbeddingsIndex:
    def __init__(self, transactions: list[StructuredTransaction] | None = None) -> None:
        self.entries: list[tuple[str, str, list[float]]] = []
        if transactions:
            for txn in transactions:
                semantic = parse_semantic(txn.description or "")
                category_hint = semantic.get("category_hint", "")
                text = " ".join(filter(None, [txn.description or "", txn.date or "", category_hint]))
                self.entries.append((txn.transaction_id, txn.description, embed_text(text)))

    @classmethod
    def from_cached(cls, entries: list[dict]) -> EmbeddingsIndex:
        index = cls(None)
        for row in entries:
            index.entries.append(
                (
                    row["transaction_id"],
                    row.get("description", ""),
                    row["vector"],
                )
            )
        return index

    def find_duplicates(self, threshold: float = 0.92) -> list[tuple[str, str, float]]:
        dupes: list[tuple[str, str, float]] = []
        n = len(self.entries)
        for i in range(n):
            for j in range(i + 1, n):
                sim = cosine_similarity(self.entries[i][2], self.entries[j][2])
                if sim >= threshold:
                    dupes.append((self.entries[i][0], self.entries[j][0], round(sim, 3)))
        return dupes

    def semantic_search(self, query: str, limit: int = 20) -> list[tuple[str, float]]:
        qvec = embed_text(query)
        scored = [
            (tid, cosine_similarity(qvec, vec))
            for tid, _, vec in self.entries
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [(tid, round(s, 3)) for tid, s in scored[:limit] if s > 0.1]
