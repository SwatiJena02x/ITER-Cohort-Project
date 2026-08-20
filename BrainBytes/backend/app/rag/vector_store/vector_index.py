from typing import Any, List, Optional


class VectorIndex:
    """
    Generic interface for vector storage and similarity search.
    """

    def add(
        self,
        ids: List[str],
        embeddings: List[Any],
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        raise NotImplementedError

    def search(
        self,
        query_embedding: Any,
        top_k: int = 5,
    ) -> List[dict]:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError