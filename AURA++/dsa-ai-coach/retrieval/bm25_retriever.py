from rank_bm25 import BM25Okapi

from chunking.chunk import Chunk


class BM25Retriever:
    """
    Keyword-based document retrieval using BM25.
    """

    def __init__(
        self,
        chunks: list[Chunk]
    ):
        self.chunks = chunks

        # Convert every chunk into tokens
        tokenized_documents = [
            self.tokenize(chunk.text)
            for chunk in chunks
        ]

        # Build BM25 index
        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    @staticmethod
    def tokenize(
        text: str
    ) -> list[str]:
        """
        Convert text into lowercase tokens.
        """

        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:
        """
        Search chunks using BM25.
        """

        # Tokenize query
        query_tokens = self.tokenize(
            query
        )

        # Calculate BM25 scores
        scores = self.bm25.get_scores(
            query_tokens
        )

        # Rank chunks by score
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        results = []

        # Get top K results
        for index in ranked_indices[:top_k]:

            chunk = self.chunks[index]

            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.text,
                    "source": chunk.metadata.get(
                        "source"
                    ),
                    "file_type": chunk.metadata.get(
                        "file_type"
                    ),
                    "chunk_index": chunk.metadata.get(
                        "chunk_index"
                    ),
                    "bm25_score": float(
                        scores[index]
                    )
                }
            )

        return results