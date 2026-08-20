from typing import Any, Dict, List, Optional

from sentence_transformers import CrossEncoder


DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """
    Cross-encoder reranker for improving retrieved document ranking.

    The reranker evaluates the query and each candidate document together,
    producing a relevance score for each query-document pair.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
    ):
        """
        Initialize the cross-encoder reranker.

        Args:
            model_name: Hugging Face cross-encoder model name.
        """
        self.model_name = model_name
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents according to their relevance to the query.

        Args:
            query: User's search query.
            documents: Candidate documents from retrieval.
            top_k: Maximum number of results to return.

        Returns:
            List of documents sorted by descending relevance score.
        """

        if not query or not query.strip():
            return []

        if not documents:
            return []

        if top_k is not None and top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        pairs = [
            [query, document]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        results = [
            {
                "document": document,
                "score": float(score),
            }
            for document, score in zip(documents, scores)
        ]

        results.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        if top_k is not None:
            results = results[:top_k]

        return results

    def rerank_results(
        self,
        query: str,
        results: Dict[str, Any],
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Rerank a retrieval result dictionary while preserving IDs
        and metadata.

        Args:
            query: User's search query.
            results: Results returned by a retrieval component.
            top_k: Maximum number of results to return.

        Returns:
            Reranked result dictionary.
        """

        if not query or not query.strip():
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "scores": [],
            }

        documents = results.get("documents", [])
        ids = results.get("ids", [])
        metadatas = results.get("metadatas", [])

        if not documents:
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "scores": [],
            }

        # Handle ChromaDB's nested result format if necessary.
        if documents and isinstance(documents[0], list):
            documents = documents[0]

        if ids and isinstance(ids[0], list):
            ids = ids[0]

        if metadatas and isinstance(metadatas[0], list):
            metadatas = metadatas[0]

        pairs = [
            [query, document]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        reranked = []

        for index, (document, score) in enumerate(
            zip(documents, scores)
        ):
            reranked.append(
                {
                    "id": ids[index] if index < len(ids) else "",
                    "document": document,
                    "metadata": (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    ),
                    "score": float(score),
                }
            )

        reranked.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        if top_k is not None:
            if top_k <= 0:
                raise ValueError("top_k must be greater than 0.")

            reranked = reranked[:top_k]

        return {
            "ids": [
                item["id"]
                for item in reranked
            ],
            "documents": [
                item["document"]
                for item in reranked
            ],
            "metadatas": [
                item["metadata"]
                for item in reranked
            ],
            "scores": [
                item["score"]
                for item in reranked
            ],
        }