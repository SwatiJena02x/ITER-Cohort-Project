from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker
from retrieval import HybridRetriever
from rag.context_builder import ContextBuilder
from rag.rag_prompt import RAGPrompt
from llm import OllamaClient


class RAGPipeline:
    """
    RAG pipeline using hybrid retrieval.

    Retrieval:
        Semantic Search + BM25 + RRF

    Generation:
        Qwen 2.5 Coder 7B via Ollama
    """

    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        top_k: int = 5
    ):
        self.top_k = top_k

        # ==============================================
        # 1. LOAD DOCUMENTS
        # ==============================================

        print("\n[RAG] Loading knowledge base...")

        loader = DocumentLoader()

        documents = loader.load_directory(
            "knowledge_base/documents"
        )

        print(
            f"[RAG] Loaded {len(documents)} documents."
        )

        # ==============================================
        # 2. CREATE CHUNKS
        # ==============================================

        print("[RAG] Creating chunks...")

        chunker = RecursiveChunker(
            chunk_size=500,
            chunk_overlap=100
        )

        chunks = chunker.chunk_documents(
            documents
        )

        print(
            f"[RAG] Created {len(chunks)} chunks."
        )

        # ==============================================
        # 3. HYBRID RETRIEVER
        # ==============================================

        print("[RAG] Building hybrid retriever...")

        self.retriever = HybridRetriever(
            chunks=chunks,
            semantic_top_k=5,
            bm25_top_k=5,
            rrf_k=60
        )

        # ==============================================
        # 4. CONTEXT BUILDER
        # ==============================================

        self.context_builder = ContextBuilder(
            max_chunks=top_k
        )

        # ==============================================
        # 5. OLLAMA LLM
        # ==============================================

        print(
            f"[RAG] Loading LLM: {model}"
        )

        self.llm = OllamaClient(
            model=model
        )

        print("[RAG] Pipeline ready.")

    # ==================================================
    # ASK
    # ==================================================

    def ask(
        self,
        question: str
    ) -> dict:
        """
        Execute the complete RAG pipeline.

        Flow:

        Question
            ↓
        Hybrid Retrieval
            ↓
        Context Building
            ↓
        RAG Prompt
            ↓
        Qwen
            ↓
        Answer
        """

        print("\n" + "=" * 70)
        print("[RAG] NEW QUESTION")
        print("=" * 70)

        print(
            f"[RAG] Question: {question}"
        )

        # ==============================================
        # 1. HYBRID SEARCH
        # ==============================================

        print(
            "\n[1] Hybrid retrieval..."
        )

        results = self.retriever.search(
            query=question,
            top_k=self.top_k
        )

        print(
            f"[2] Retrieved {len(results)} chunks."
        )

        # ==============================================
        # DEBUG RETRIEVED CHUNKS
        # ==============================================

        for index, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\n--- Retrieved Chunk {index} ---"
            )

            print(
                f"Source: {result.get('source', 'unknown')}"
            )

            print(
                f"Chunk ID: {result.get('chunk_id', 'unknown')}"
            )

            print(
                f"Similarity: {result.get('similarity', 'unknown')}"
            )

            print(
                result.get(
                    "text",
                    result.get(
                        "content",
                        ""
                    )
                )[:500]
            )

        # ==============================================
        # 2. BUILD CONTEXT
        # ==============================================

        print(
            "\n[3] Building context..."
        )

        context = self.context_builder.build(
            results
        )

        print(
            f"[4] Context built. "
            f"Characters: {len(context)}"
        )

        # ==============================================
        # DEBUG CONTEXT
        # ==============================================

        print(
            "\n" + "-" * 70
        )

        print(
            "FINAL RAG CONTEXT"
        )

        print(
            "-" * 70
        )

        print(context)

        print(
            "-" * 70
        )

        # ==============================================
        # 3. BUILD PROMPT
        # ==============================================

        print(
            "\n[5] Building RAG prompt..."
        )

        prompt = RAGPrompt.build(
            question=question,
            context=context
        )

        print(
            f"[6] Prompt built. "
            f"Characters: {len(prompt)}"
        )

        # ==============================================
        # 4. GENERATE ANSWER
        # ==============================================

        print(
            "\n[7] Sending context to Qwen..."
        )

        answer = self.llm.generate(
            prompt
        )

        print(
            "\n[8] Answer generated."
        )

        print(
            "\n" + "-" * 70
        )

        print(
            "RAG ANSWER"
        )

        print(
            "-" * 70
        )

        print(answer)

        print(
            "-" * 70
        )

        # ==============================================
        # 5. RETURN RESULT
        # ==============================================

        return {
            "question": question,
            "answer": answer,
            "sources": results,
            "context": context
        }

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        print(
            "[RAG] Closing retriever..."
        )

        if hasattr(
            self.retriever,
            "close"
        ):
            self.retriever.close()

        print(
            "[RAG] Closed."
        )