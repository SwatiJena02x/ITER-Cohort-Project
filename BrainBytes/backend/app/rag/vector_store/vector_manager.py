from typing import Any, Dict, List, Optional

from backend.app.rag.embeddings.embedding_generator import EmbeddingGenerator
from backend.app.rag.embeddings.embedding_model import EmbeddingModel
from backend.app.rag.vector_store.chroma_store import ChromaStore


class VectorManager:
    """
    High-level manager for generating embeddings
    and storing/searching chunks in ChromaDB.
    """

    def __init__(
        self,
        model: Optional[EmbeddingModel] = None,
        store: Optional[ChromaStore] = None,
    ):
        """
        Initialize the embedding model, generator, and vector store.
        """
        self.model = model or EmbeddingModel()
        self.generator = EmbeddingGenerator(self.model)
        self.store = store or ChromaStore()

    @property
    def dimension(self) -> int:
        """
        Return the embedding dimension.
        """
        return self.generator.dimension

    def count(self) -> int:
        """
        Return the number of stored chunks.
        """
        return self.store.count()

    def add_chunks(
        self,
        chunks: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """
        Generate embeddings for chunks and store them in ChromaDB.

        Args:
            chunks: List of text chunks.
            metadatas: Optional metadata for each chunk.
            ids: Optional unique IDs for each chunk.
        """
        if not chunks:
            return

        if metadatas is not None and len(metadatas) != len(chunks):
            raise ValueError(
                "metadatas must have the same length as chunks."
            )

        if ids is not None and len(ids) != len(chunks):
            raise ValueError(
                "ids must have the same length as chunks."
            )

        if ids is None:
            start_index = self.count()
            ids = [
                f"chunk_{start_index + index}"
                for index in range(len(chunks))
            ]

        embeddings = self.generator.generate_for_chunks(chunks)

        self.store.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Search stored chunks using semantic similarity.

        Args:
            query: Search query.
            top_k: Number of results to return.

        Returns:
            ChromaDB search results.
        """
        if not query or not query.strip():
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": [],
            }

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query_embedding = self.generator.generate(query)

        return self.store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )