from embedding import EmbeddingService
from vector_store import PostgreSQLVectorStore


def main():

    print("\n" + "=" * 60)
    print("SEMANTIC SEARCH TEST")
    print("=" * 60)

    # --------------------------------
    # 1. Load embedding model
    # --------------------------------

    embedding_service = EmbeddingService()

    # --------------------------------
    # 2. User query
    # --------------------------------

    query = (
        "What is the DP state in the "
        "House Robber problem?"
    )

    print(f"\nQuery:")
    print(query)

    # --------------------------------
    # 3. Create query embedding
    # --------------------------------

    query_embedding = (
        embedding_service.embed_query(
            query
        )
    )

    print(
        f"\nQuery embedding dimension: "
        f"{len(query_embedding)}"
    )

    # --------------------------------
    # 4. Search PostgreSQL
    # --------------------------------

    vector_store = PostgreSQLVectorStore()

    results = vector_store.similarity_search(
        query_embedding=query_embedding,
        top_k=3
    )

    # --------------------------------
    # 5. Display results
    # --------------------------------

    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)

    for index, result in enumerate(
        results,
        start=1
    ):

        print("\n" + "-" * 60)

        print(
            f"Rank: {index}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print("\nContent:")

        print(
            result["content"]
        )

    vector_store.close()


if __name__ == "__main__":
    main()