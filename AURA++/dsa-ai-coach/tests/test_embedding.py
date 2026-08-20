from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker
from embedding import EmbeddingService


def main():

    # 1. Load documents
    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print(
        f"\nDocuments loaded: {len(documents)}"
    )

    # 2. Chunk
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

    # 3. Embedding model
    embedding_service = EmbeddingService()

    # 4. Generate embeddings
    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = (
        embedding_service.embed_documents(
            texts
        )
    )

    # 5. Display
    print(
        f"\nEmbeddings created: "
        f"{len(embeddings)}"
    )

    print(
        f"Embedding dimensions: "
        f"{len(embeddings[0])}"
    )

    print("\nFirst 10 values:")

    print(
        embeddings[0][:10]
    )


if __name__ == "__main__":
    main()