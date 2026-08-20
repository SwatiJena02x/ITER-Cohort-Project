from typing import Any, Dict, Optional

from backend.app.rag.vector_store.vector_manager import VectorManager


class SemanticSearch:
    """
    Semantic search over the ChromaDB vector store.
    """

    def __init__(self, vector_manager: Optional[VectorManager] = None):
        """
        Initialize semantic search.

        Args:
            vector_manager: Optional existing VectorManager instance.
        """
        self.vector_manager = vector_manager or VectorManager()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Search for documents semantically similar to the query.

        Args:
            query: User's search query.
            top_k: Number of results to return.

        Returns:
            Search results from ChromaDB.
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

        return self.vector_manager.search(
            query=query,
            top_k=top_k,
        )

    def count(self) -> int:
        """
        Return the number of indexed documents.
        """
        return self.vector_manager.count()