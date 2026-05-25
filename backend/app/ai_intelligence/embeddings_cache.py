"""Persisted embeddings cache keyed by transaction content fingerprint."""

from __future__ import annotations

import hashlib
from typing import Any

from app.shared.models import StructuredTransaction
from app.ai_intelligence.embeddings_engine import EmbeddingsIndex, embed_text

CACHE_KEY = "ai_embeddings_cache"
DEFAULT_DIM = 64


def transactions_fingerprint(transactions: list[StructuredTransaction]) -> str:
    parts = sorted(
        f"{t.transaction_id}|{t.description}|{t.date or ''}|{t.debit}|{t.credit}"
        for t in transactions
    )
    payload = "\n".join(parts)
    return hashlib.sha256(payload.encode()).hexdigest()


def build_cache_payload(
    transactions: list[StructuredTransaction],
    dim: int = DEFAULT_DIM,
) -> dict[str, Any]:
    entries = []
    for txn in transactions:
        text = f"{txn.description} {txn.date or ''}"
        entries.append(
            {
                "transaction_id": txn.transaction_id,
                "description": txn.description,
                "vector": embed_text(text, dim=dim),
            }
        )
    return {
        "fingerprint": transactions_fingerprint(transactions),
        "dim": dim,
        "entries": entries,
    }


def load_index_from_meta(
    meta: dict,
    transactions: list[StructuredTransaction],
    *,
    dim: int = DEFAULT_DIM,
    force_rebuild: bool = False,
) -> tuple[EmbeddingsIndex, dict, bool]:
    """
    Return (index, updated_meta_fragment, cache_hit).
    """
    fp = transactions_fingerprint(transactions)
    cached = meta.get(CACHE_KEY) if not force_rebuild else None

    if cached and cached.get("fingerprint") == fp and cached.get("entries"):
        index = EmbeddingsIndex.from_cached(cached["entries"])
        return index, {CACHE_KEY: cached}, True

    payload = build_cache_payload(transactions, dim=dim)
    index = EmbeddingsIndex.from_cached(payload["entries"])
    return index, {CACHE_KEY: payload}, False
