from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker
from embedding import EmbeddingService
from vector_store import PostgreSQLVectorStore


def main():

    print("\n" + "=" * 60)
    print("DSA COACH - RAG INGESTION")
    print("=" * 60)

    # --------------------------------
    # 1. LOAD DOCUMENTS
    # --------------------------------

    print("\n[1] Loading documents...")

    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print(
        f"Documents loaded: {len(documents)}"
    )

    # --------------------------------
    # 2. CHUNK
    # --------------------------------

    print("\n[2] Creating chunks...")

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = chunker.chunk_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    # --------------------------------
    # 3. EMBEDDINGS
    # --------------------------------

    print("\n[3] Creating embeddings...")

    embedding_service = EmbeddingService()

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = (
        embedding_service.embed_documents(
            texts
        )
    )

    print(
        f"Embeddings created: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    # --------------------------------
    # 4. POSTGRESQL
    # --------------------------------

    print("\n[4] Storing in PostgreSQL...")

    vector_store = PostgreSQLVectorStore()

    vector_store.add_chunks(
        chunks,
        embeddings
    )

    # --------------------------------
    # 5. VERIFY
    # --------------------------------

    count = vector_store.count()

    print(
        f"\nTotal rows in database: {count}"
    )

    vector_store.close()

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()