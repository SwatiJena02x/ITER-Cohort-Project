from rag import RAGPipeline


def main():

    print("\n" + "=" * 60)
    print("DSA COACH - HYBRID RAG TEST")
    print("=" * 60)

    rag = RAGPipeline(
        model="qwen2.5-coder:7b",
        top_k=3
    )

    question = (
        "What does dp[i-2] + nums[i] mean?"
    )

    result = rag.ask(   
        question
    )

    print("\n" + "=" * 60)
    print("QUESTION")
    print("=" * 60)

    print(
        result["question"]
    )

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)

    print(
        result["answer"]
    )

    print("\n" + "=" * 60)
    print("RETRIEVED SOURCES")
    print("=" * 60)

    for rank, source in enumerate(
        result["sources"],
        start=1
    ):

        print(
            f"\nRank {rank}"
        )

        print(
            f"Chunk: "
            f"{source['chunk_id']}"
        )

        print(
            f"RRF Score: "
            f"{source['rrf_score']:.6f}"
        )

        print(
            f"Semantic Score: "
            f"{source['semantic_score']:.4f}"
        )

        print(
            f"BM25 Score: "
            f"{source['bm25_score']:.4f}"
        )

        print(
            f"Source: "
            f"{source['source']}"
        )

    rag.close()


if __name__ == "__main__":
    main()