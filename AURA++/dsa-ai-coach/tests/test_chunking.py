from document_loader import DocumentLoader
from chunking.recursive_chunker import RecursiveChunker


def main():

    # ----------------------------------
    # STEP 1: LOAD DOCUMENTS
    # ----------------------------------

    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print("\n")
    print("=" * 60)
    print("DOCUMENTS")
    print("=" * 60)

    print(
        f"Documents loaded: {len(documents)}"
    )


    # ----------------------------------
    # STEP 2: CHUNK DOCUMENTS
    # ----------------------------------

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = chunker.chunk_documents(
        documents
    )


    # ----------------------------------
    # STEP 3: DISPLAY RESULTS
    # ----------------------------------

    print("\n")
    print("=" * 60)
    print("CHUNKING RESULTS")
    print("=" * 60)

    print(
        f"Total chunks: {len(chunks)}"
    )


    for chunk in chunks:

        print("\n")
        print("-" * 60)

        print(
            f"Chunk ID: {chunk.chunk_id}"
        )

        print(
            f"Source: "
            f"{chunk.metadata.get('source')}"
        )

        print(
            f"Type: "
            f"{chunk.metadata.get('file_type')}"
        )

        print(
            f"Characters: {len(chunk)}"
        )

        print("\nText:")

        print(chunk.text)


if __name__ == "__main__":
    main()