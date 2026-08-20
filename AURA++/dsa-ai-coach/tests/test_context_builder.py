from embedding import EmbeddingService
from vector_store import PostgreSQLVectorStore
from rag import ContextBuilder


def main():

    print("\n" + "=" * 60)
    print("CONTEXT BUILDER TEST")
    print("=" * 60)

    # --------------------------------
    # 1. Create embedding service
    # --------------------------------

    embedding_service = EmbeddingService()

    # --------------------------------
    # 2. User query
    # --------------------------------

    query = (
        "What is the DP state in "
        "the House Robber problem?"
    )

    print("\nQuery:")
    print(query)

    # --------------------------------
    # 3. Create query embedding
    # --------------------------------

    query_embedding = (
        embedding_service.embed_query(
            query
        )
    )

    # --------------------------------
    # 4. Semantic search
    # --------------------------------

    vector_store = PostgreSQLVectorStore()

    results = vector_store.similarity_search(
        query_embedding=query_embedding,
        top_k=3
    )

    print(
        f"\nRetrieved chunks: "
        f"{len(results)}"
    )

    # --------------------------------
    # 5. Build context
    # --------------------------------

    context_builder = ContextBuilder(
        max_chunks=3
    )

    context = context_builder.build(
        results
    )

    # --------------------------------
    # 6. Display context
    # --------------------------------

    print("\n" + "=" * 60)
    print("GENERATED CONTEXT")
    print("=" * 60)

    print(context)

    vector_store.close()


if __name__ == "__main__":
    main()