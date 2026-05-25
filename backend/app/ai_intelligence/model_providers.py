"""Pluggable model backends — swap inference without coupling business logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


class CategoryProvider(Protocol):
    def categorize(self, description: str) -> tuple[str, float]: ...


class BaseEmbeddingBackend(ABC):
    @abstractmethod
    def embed(self, text: str, dim: int = 64) -> list[float]:
        raise NotImplementedError


class HashEmbeddingBackend(BaseEmbeddingBackend):
    """Default lightweight backend (no GPU / no sentence-transformers)."""

    def embed(self, text: str, dim: int = 64) -> list[float]:
        from app.ai_intelligence.embeddings_engine import embed_text

        return embed_text(text, dim=dim)


class SentenceTransformerBackend(BaseEmbeddingBackend):
    """Optional upgrade path — loads only when installed."""

    _model = None

    def embed(self, text: str, dim: int = 64) -> list[float]:
        try:
            if SentenceTransformerBackend._model is None:
                from sentence_transformers import SentenceTransformer

                SentenceTransformerBackend._model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
            vec = SentenceTransformerBackend._model.encode(text)
            return vec.tolist()[:dim]
        except ImportError:
            return HashEmbeddingBackend().embed(text, dim=dim)


def get_embedding_backend(name: str = "hash") -> BaseEmbeddingBackend:
    if name == "sentence_transformers":
        return SentenceTransformerBackend()
    return HashEmbeddingBackend()
