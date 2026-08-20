from __future__ import annotations

from typing import List, Sequence

from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from langchain_core.embeddings import Embeddings


class LocalChromaEmbeddings(Embeddings):
    """LangChain adapter for Chroma's bundled local MiniLM embedding model."""

    def __init__(self) -> None:
        self._embedding_function = DefaultEmbeddingFunction()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors = self._embedding_function([text or "" for text in texts])
        return [[float(value) for value in vector] for vector in vectors]

    def embed_query(self, text: str) -> List[float]:
        vectors = self._embedding_function([text or ""])
        return [float(value) for value in vectors[0]]


def embedding_dimension(embeddings: Embeddings | None = None) -> int:
    model = embeddings or LocalChromaEmbeddings()
    return len(model.embed_query("embedding dimension probe"))
