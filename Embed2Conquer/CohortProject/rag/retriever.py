import os
import time
from dotenv import load_dotenv
import psycopg
from pgvector.psycopg import register_vector

from rank_bm25 import BM25Okapi

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "dsa_coach_tree")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# RETRIEVER
# ============================================================

class Retriever:

    def __init__(self):

        print(
            "Loading embedding model..."
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Loading documents from PostgreSQL..."
        )

        self.documents = self._load_documents()

        print(
            f"Loaded {len(self.documents)} documents."
        )

        # ----------------------------------------------------
        # BM25 INDEX
        # ----------------------------------------------------

        tokenized_documents = [
            document["content"].lower().split()
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

        print(
            "BM25 keyword index ready."
        )


    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def _get_connection(self):

        if not DB_PASSWORD:

            raise ValueError(
                "DB_PASSWORD is not set in .env"
            )

        connection = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        register_vector(connection)

        return connection


    # ========================================================
    # LOAD DOCUMENTS
    # ========================================================

    def _load_documents(self):

        connection = self._get_connection()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        content,
                        source,
                        chunk_index
                    FROM tree_documents
                    ORDER BY id;
                    """
                )

                rows = cursor.fetchall()

        finally:

            connection.close()


        documents = []

        for row in rows:

            documents.append(
                {
                    "id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "chunk_index": row[3]
                }
            )

        return documents


    # ========================================================
    # EMBEDDING SEARCH
    # ========================================================

    def semantic_search(
        self,
        query,
        top_k=5
    ):

        query_vector = self.model.encode(
            query,
            convert_to_numpy=True
        )

        connection = self._get_connection()

        try:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        content,
                        source,
                        chunk_index,
                        1 - (embedding <=> %s)
                            AS similarity
                    FROM tree_documents
                    ORDER BY embedding <=> %s
                    LIMIT %s;
                    """,
                    (
                        query_vector,
                        query_vector,
                        top_k
                    )
                )

                rows = cursor.fetchall()

        finally:

            connection.close()


        results = []

        for row in rows:

            results.append(
                {
                    "id": row[0],
                    "text": row[1],
                    "source": row[2],
                    "chunk_index": row[3],
                    "score": float(row[4]),
                    "retrieval_type": "semantic"
                }
            )

        return results


    # ========================================================
    # BM25 SEARCH
    # ========================================================

    def keyword_search(
        self,
        query,
        top_k=5
    ):

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indices[:top_k]:

            document = self.documents[index]

            results.append(
                {
                    "id": document["id"],
                    "text": document["content"],
                    "source": document["source"],
                    "chunk_index": document["chunk_index"],
                    "score": float(scores[index]),
                    "retrieval_type": "keyword"
                }
            )

        return results


    # ========================================================
    # HYBRID SEARCH
    # ========================================================

    def hybrid_search(
        self,
        query,
        top_k=5,
        alpha=0.5
    ):
        start_time = time.perf_counter()
        semantic_results = self.semantic_search(
            query,
            top_k=top_k
        )
        semantic_time = time.perf_counter()

        keyword_results = self.keyword_search(
            query,
            top_k=top_k
        )
        keyword_time = time.perf_counter()
        # ----------------------------------------------------
        # Normalize semantic scores
        # ----------------------------------------------------

        semantic_scores = {}

        for result in semantic_results:

            semantic_scores[
                result["id"]
            ] = result["score"]


        # ----------------------------------------------------
        # Normalize BM25 scores
        # ----------------------------------------------------

        keyword_scores = {}

        for result in keyword_results:

            keyword_scores[
                result["id"]
            ] = result["score"]


        max_keyword = max(
            keyword_scores.values(),
            default=1
        )

        if max_keyword == 0:
            max_keyword = 1


        # ----------------------------------------------------
        # Combine scores
        # ----------------------------------------------------

        combined = {}

        all_ids = set(
            semantic_scores
        ) | set(
            keyword_scores
        )

        for document_id in all_ids:

            semantic_score = semantic_scores.get(
                document_id,
                0
            )

            keyword_score = (
                keyword_scores.get(
                    document_id,
                    0
                ) / max_keyword
            )

            final_score = (
                alpha * semantic_score
                +
                (1 - alpha) * keyword_score
            )

            combined[
                document_id
            ] = final_score


        # ----------------------------------------------------
        # Get document information
        # ----------------------------------------------------

        document_map = {
            document["id"]: document
            for document in self.documents
        }

        ranked_ids = sorted(
            combined,
            key=combined.get,
            reverse=True
        )

        results = []

        for document_id in ranked_ids[:top_k]:

            document = document_map[
                document_id
            ]

            results.append(
                {
                    "id": document["id"],
                    "text": document["content"],
                    "source": document["source"],
                    "chunk_index": document["chunk_index"],
                    "score": combined[
                        document_id
                    ]
                }
            )
        total_time = time.perf_counter()
        print(f"⏱️ RAG TIMING | "f"semantic={semantic_time - start_time:.3f}s | "f"BM25={keyword_time - semantic_time:.3f}s | "f"total={total_time - start_time:.3f}s")

        return results


# ============================================================
# TEST RETRIEVER
# ============================================================

if __name__ == "__main__":

    retriever = Retriever()

    query = input(
        "\nAsk a Tree question: "
    )

    print(
        "\nSearching..."
    )

    results = retriever.hybrid_search(
        query,
        top_k=5,
        alpha=0.5
    )

    print(
        "\n" + "=" * 70
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nRESULT {i}"
        )

        print(
            "Source:",
            result["source"]
        )

        print(
            "Chunk:",
            result["chunk_index"]
        )

        print(
            "Score:",
            result["score"]
        )

        print(
            "Content:"
        )

        print(
            result["text"][:500]
        )