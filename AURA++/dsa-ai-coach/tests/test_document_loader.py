from document_loader import DocumentLoader


def main():

    loader = DocumentLoader()

    documents = loader.load_directory(
        "knowledge_base/documents"
    )

    print("\n")
    print("=" * 60)
    print("DOCUMENT LOADING COMPLETE")
    print("=" * 60)

    print(
        f"Total documents/pages loaded: "
        f"{len(documents)}"
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print("\n" + "-" * 60)

        print(f"Document #{index}")

        print(
            f"Source: "
            f"{document.metadata.get('source')}"
        )

        print(
            f"Type: "
            f"{document.metadata.get('file_type')}"
        )

        if "page" in document.metadata:
            print(
                f"Page: "
                f"{document.metadata['page']}"
            )

        print(
            f"Characters: "
            f"{len(document)}"
        )

        print("\nPreview:")

        print(
            document.text[:300]
        )


if __name__ == "__main__":
    main()