from embedding import EmbeddingService
from vector_store import PostgreSQLVectorStore
from .bm25_retriever import BM25Retriever


class HybridRetriever:
    """
    Combines semantic search and BM25 search
    using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        chunks,
        semantic_top_k: int = 5,
        bm25_top_k: int = 5,
        rrf_k: int = 60
    ):
        self.chunks = chunks

        self.semantic_top_k = semantic_top_k
        self.bm25_top_k = bm25_top_k
        self.rrf_k = rrf_k

        # Semantic search
        self.embedding_service = (
            EmbeddingService()
        )

        self.vector_store = (
            PostgreSQLVectorStore()
        )

        # BM25 search
        self.bm25 = BM25Retriever(
            chunks
        )

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:

        # =================================
        # 1. SEMANTIC SEARCH
        # =================================

        query_embedding = (
            self.embedding_service
            .embed_query(query)
        )

        semantic_results = (
            self.vector_store.similarity_search(
                query_embedding=query_embedding,
                top_k=self.semantic_top_k
            )
        )

        # =================================
        # 2. BM25 SEARCH
        # =================================

        bm25_results = (
            self.bm25.search(
                query=query,
                top_k=self.bm25_top_k
            )
        )

        # =================================
        # 3. RRF SCORE FUSION
        # =================================

        fused_results = {}

        # ---------------------------------
        # Add semantic rankings
        # ---------------------------------

        for rank, result in enumerate(
            semantic_results,
            start=1
        ):

            chunk_id = result["chunk_id"]

            if chunk_id not in fused_results:

                fused_results[chunk_id] = {
                    "chunk_id": chunk_id,
                    "content": result["content"],
                    "source": result["source"],
                    "file_type": result["file_type"],
                    "chunk_index": result["chunk_index"],
                    "semantic_score": result["similarity"],
                    "bm25_score": 0.0,
                    "rrf_score": 0.0
                }

            fused_results[chunk_id]["rrf_score"] += (
                1 / (self.rrf_k + rank)
            )

        # ---------------------------------
        # Add BM25 rankings
        # ---------------------------------

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            chunk_id = result["chunk_id"]

            if chunk_id not in fused_results:

                fused_results[chunk_id] = {
                    "chunk_id": chunk_id,
                    "content": result["content"],
                    "source": result["source"],
                    "file_type": result["file_type"],
                    "chunk_index": result["chunk_index"],
                    "semantic_score": 0.0,
                    "bm25_score": result["bm25_score"],
                    "rrf_score": 0.0
                }

            else:

                fused_results[chunk_id]["bm25_score"] = (
                    result["bm25_score"]
                )

            fused_results[chunk_id]["rrf_score"] += (
                1 / (self.rrf_k + rank)
            )

        # =================================
        # 4. SORT BY RRF SCORE
        # =================================

        results = sorted(
            fused_results.values(),
            key=lambda result: result["rrf_score"],
            reverse=True
        )

        return results[:top_k]

    def close(self):
        """
        Close PostgreSQL connection.
        """

        self.vector_store.close()