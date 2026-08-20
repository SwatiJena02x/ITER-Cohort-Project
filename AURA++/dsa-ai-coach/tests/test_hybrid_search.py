from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker
from retrieval import HybridRetriever


def main():

    print("\n" + "=" * 60)
    print("HYBRID SEARCH TEST")
    print("=" * 60)

    # =================================
    # 1. LOAD DOCUMENTS
    # =================================

    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print(
        f"\nDocuments loaded: "
        f"{len(documents)}"
    )

    # =================================
    # 2. CREATE CHUNKS
    # =================================

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

    # =================================
    # 3. CREATE HYBRID RETRIEVER
    # =================================

    retriever = HybridRetriever(
        chunks=chunks,
        semantic_top_k=5,
        bm25_top_k=5,
        rrf_k=60
    )

    print(
        "\nHybrid retriever created."
    )

    # =================================
    # 4. QUERY
    # =================================

    query = (
        "dp[i-2] + nums[i]"
    )

    print(
        f"\nQuery:\n{query}"
    )

    # =================================
    # 5. HYBRID SEARCH
    # =================================

    results = retriever.search(
        query=query,
        top_k=3
    )

    # =================================
    # 6. DISPLAY RESULTS
    # =================================

    print("\n" + "=" * 60)
    print("HYBRID SEARCH RESULTS")
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
            f"RRF Score: "
            f"{result['rrf_score']:.6f}"
        )

        print(
            f"Semantic Score: "
            f"{result['semantic_score']:.4f}"
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

    retriever.close()


if __name__ == "__main__":
    main()