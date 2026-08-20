from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi

from backend.app.rag.vector_store.vector_manager import VectorManager


class BM25Search:
    """
    Keyword-based BM25 search over documents stored in the vector store.
    """

    def __init__(
        self,
        vector_manager: Optional[VectorManager] = None,
    ):
        """
        Initialize BM25 search.

        Args:
            vector_manager: Optional existing VectorManager.
        """
        self.vector_manager = vector_manager or VectorManager()

        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.ids: List[str] = []

        self.bm25: Optional[BM25Okapi] = None

        self._build_index()

    def _build_index(self) -> None:
        """
        Build the BM25 index from documents currently in ChromaDB.
        """
        if self.vector_manager.count() == 0:
            self.bm25 = None
            return

        results = self.vector_manager.store.collection.get(
            include=["documents", "metadatas"]
        )

        self.documents = results.get("documents") or []
        self.metadatas = results.get("metadatas") or []
        self.ids = results.get("ids") or []

        if not self.documents:
            self.bm25 = None
            return

        tokenized_documents = [
            self._tokenize(document)
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """
        Convert text into simple lowercase tokens.
        """
        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Search documents using BM25 keyword matching.

        Args:
            query: User search query.
            top_k: Number of results to return.

        Returns:
            Dictionary containing matching documents,
            metadata, IDs, and BM25 scores.
        """
        if not query or not query.strip():
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "scores": [],
            }

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        # Rebuild in case new documents were added.
        self._build_index()

        if self.bm25 is None:
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "scores": [],
            }

        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        return {
            "ids": [
                self.ids[index]
                for index in ranked_indices
            ],
            "documents": [
                self.documents[index]
                for index in ranked_indices
            ],
            "metadatas": [
                self.metadatas[index]
                for index in ranked_indices
            ],
            "scores": [
                float(scores[index])
                for index in ranked_indices
            ],
        }

    def count(self) -> int:
        """
        Return the number of indexed documents.
        """
        return len(self.documents)