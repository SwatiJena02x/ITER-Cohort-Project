from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker
from retrieval import BM25Retriever


def main():

    print("\n" + "=" * 60)
    print("BM25 SEARCH TEST")
    print("=" * 60)

    # -----------------------------
    # 1. Load documents
    # -----------------------------

    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print(
        f"\nDocuments loaded: "
        f"{len(documents)}"
    )

    # -----------------------------
    # 2. Create chunks
    # -----------------------------

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = chunker.chunk_documents(
        documents
    )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    # -----------------------------
    # 3. Create BM25 index
    # -----------------------------

    retriever = BM25Retriever(
        chunks
    )

    print("\nBM25 index created.")

    # -----------------------------
    # 4. Query
    # -----------------------------

    query = (
        "What is the DP state "
        "in House Robber?"
    )

    print(
        f"\nQuery: {query}"
    )

    # -----------------------------
    # 5. Search
    # -----------------------------

    results = retriever.search(
        query=query,
        top_k=3
    )

    # -----------------------------
    # 6. Display results
    # -----------------------------

    print("\n" + "=" * 60)
    print("BM25 RESULTS")
    print("=" * 60)

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            "\n" + "-" * 60
        )

        print(
            f"Rank: {rank}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print(
            f"BM25 Score: "
            f"{result['bm25_score']:.4f}"
        )

        print(
            f"Source: "
            f"{result['source']}"
        )

        print("\nContent:")

        print(
            result["content"]
        )


if __name__ == "__main__":
    main()