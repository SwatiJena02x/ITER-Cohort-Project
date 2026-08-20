from typing import Any, Dict, List, Optional

from backend.app.rag.retrieval.semantic_search import SemanticSearch
from backend.app.rag.retrieval.bm25_search import BM25Search
from backend.app.rag.vector_store.vector_manager import VectorManager


class HybridSearch:
    """
    Hybrid retrieval combining semantic search and BM25 keyword search.

    Semantic search captures meaning and contextual similarity.
    BM25 captures exact keyword matches.
    """

    def __init__(
        self,
        vector_manager: Optional[VectorManager] = None,
        semantic_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ):
        """
        Initialize hybrid search.

        Args:
            vector_manager: Optional shared VectorManager instance.
            semantic_weight: Weight given to semantic search.
            bm25_weight: Weight given to BM25 search.
        """

        if semantic_weight < 0 or bm25_weight < 0:
            raise ValueError("Search weights cannot be negative.")

        if semantic_weight + bm25_weight == 0:
            raise ValueError(
                "At least one search weight must be greater than 0."
            )

        total_weight = semantic_weight + bm25_weight

        self.semantic_weight = semantic_weight / total_weight
        self.bm25_weight = bm25_weight / total_weight

        self.vector_manager = vector_manager or VectorManager()

        self.semantic_search = SemanticSearch(
            vector_manager=self.vector_manager
        )

        self.bm25_search = BM25Search(
            vector_manager=self.vector_manager
        )

    @staticmethod
    def _normalize_scores(scores: List[float]) -> List[float]:
        """
        Normalize scores to the range 0-1 using min-max normalization.

        Higher values represent better results.
        """

        if not scores:
            return []

        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            return [1.0 for _ in scores]

        return [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]

    @staticmethod
    def _semantic_similarity_from_distance(distance: float) -> float:
        """
        Convert a Chroma distance into a similarity score.

        Chroma is configured with cosine distance, where lower
        distance means greater similarity.
        """

        return 1.0 / (1.0 + max(float(distance), 0.0))

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Perform hybrid semantic + BM25 search.

        Args:
            query: User search query.
            top_k: Number of final results to return.

        Returns:
            Dictionary containing ranked hybrid search results.
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

        # Retrieve more candidates than the final top_k.
        candidate_k = max(top_k * 2, 10)

        semantic_results = self.semantic_search.search(
            query=query,
            top_k=candidate_k,
        )

        bm25_results = self.bm25_search.search(
            query=query,
            top_k=candidate_k,
        )

        combined: Dict[str, Dict[str, Any]] = {}

        # ---------------------------------------------------------
        # Semantic results
        # ---------------------------------------------------------

        semantic_ids = semantic_results.get("ids", [])
        semantic_documents = semantic_results.get("documents", [])
        semantic_metadatas = semantic_results.get("metadatas", [])
        semantic_distances = semantic_results.get("distances", [])

        # Chroma returns nested lists for a single query.
        if semantic_ids and isinstance(semantic_ids[0], list):
            semantic_ids = semantic_ids[0]

        if semantic_documents and isinstance(semantic_documents[0], list):
            semantic_documents = semantic_documents[0]

        if semantic_metadatas and isinstance(semantic_metadatas[0], list):
            semantic_metadatas = semantic_metadatas[0]

        if semantic_distances and isinstance(semantic_distances[0], list):
            semantic_distances = semantic_distances[0]

        for index, document_id in enumerate(semantic_ids):
            distance = (
                semantic_distances[index]
                if index < len(semantic_distances)
                else 1.0
            )

            similarity = self._semantic_similarity_from_distance(
                distance
            )

            document = (
                semantic_documents[index]
                if index < len(semantic_documents)
                else ""
            )

            metadata = (
                semantic_metadatas[index]
                if index < len(semantic_metadatas)
                else {}
            )

            combined[document_id] = {
                "id": document_id,
                "document": document,
                "metadata": metadata,
                "semantic_score": similarity,
                "bm25_score": 0.0,
            }

        # ---------------------------------------------------------
        # BM25 results
        # ---------------------------------------------------------

        bm25_ids = bm25_results.get("ids", [])
        bm25_documents = bm25_results.get("documents", [])
        bm25_metadatas = bm25_results.get("metadatas", [])
        bm25_scores = bm25_results.get("scores", [])

        normalized_bm25_scores = self._normalize_scores(
            bm25_scores
        )

        for index, document_id in enumerate(bm25_ids):
            bm25_score = (
                normalized_bm25_scores[index]
                if index < len(normalized_bm25_scores)
                else 0.0
            )

            document = (
                bm25_documents[index]
                if index < len(bm25_documents)
                else ""
            )

            metadata = (
                bm25_metadatas[index]
                if index < len(bm25_metadatas)
                else {}
            )

            if document_id in combined:
                combined[document_id]["bm25_score"] = bm25_score
            else:
                combined[document_id] = {
                    "id": document_id,
                    "document": document,
                    "metadata": metadata,
                    "semantic_score": 0.0,
                    "bm25_score": bm25_score,
                }

        # ---------------------------------------------------------
        # Calculate final hybrid scores
        # ---------------------------------------------------------

        results = []

        for item in combined.values():
            hybrid_score = (
                self.semantic_weight * item["semantic_score"]
                + self.bm25_weight * item["bm25_score"]
            )

            item["score"] = float(hybrid_score)

            results.append(item)

        # Highest score first.
        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        results = results[:top_k]

        return {
            "ids": [
                item["id"]
                for item in results
            ],
            "documents": [
                item["document"]
                for item in results
            ],
            "metadatas": [
                item["metadata"]
                for item in results
            ],
            "scores": [
                item["score"]
                for item in results
            ],
        }

    def count(self) -> int:
        """
        Return the number of indexed documents.
        """
        return self.vector_manager.count()