# ============================================================
# DSA Coach AI - Unified Document Loader
# ============================================================
#
# Supports:
#   .ipynb  -> Jupyter Notebook
#   .py     -> Python
#   .txt    -> Text
#   .pdf    -> PDF
#
# The loader automatically selects the correct loader based
# on the file extension.
# ============================================================

from pathlib import Path

from langchain_core.documents import Document

from rag.loaders.notebook_loader import load_notebook
from rag.loaders.python_loader import load_python_file
from rag.loaders.text_loader import load_text_file


# ============================================================
# PDF LOADER
# ============================================================

def load_pdf_file(file_path: str) -> list[Document]:
    """
    Load a PDF file using PyPDFLoader.
    """

    try:
        from langchain_community.document_loaders import (
            PyPDFLoader
        )

    except ImportError:

        raise ImportError(
            "PyPDFLoader is not available. "
            "Install pypdf and langchain-community."
        )

    path = Path(file_path).resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {path}"
        )

    loader = PyPDFLoader(str(path))

    documents = loader.load()

    # Add our own metadata
    for document in documents:

        document.metadata.update(
            {
                "source": path.name,
                "file_path": str(path),
                "file_type": "pdf",
            }
        )

    return documents


# ============================================================
# LOAD ONE DOCUMENT
# ============================================================

def load_document(file_path: str) -> list[Document]:
    """
    Automatically select the correct loader according
    to the file extension.
    """

    path = Path(file_path).resolve()

    if not path.exists():

        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    # --------------------------------------------------------
    # Jupyter Notebook
    # --------------------------------------------------------

    if extension == ".ipynb":

        return load_notebook(str(path))

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    elif extension == ".py":

        return load_python_file(str(path))

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    elif extension == ".txt":

        return load_text_file(str(path))

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    elif extension == ".pdf":

        return load_pdf_file(str(path))

    # --------------------------------------------------------
    # Unsupported file
    # --------------------------------------------------------

    else:

        raise ValueError(
            f"Unsupported file type: {extension}\n"
            f"Supported types: .ipynb, .py, .txt, .pdf"
        )


# ============================================================
# LOAD ALL DOCUMENTS
# ============================================================

def load_all_documents(
    documents_directory: str
) -> list[Document]:
    """
    Load all supported documents from a directory.
    """

    directory = Path(
        documents_directory
    ).resolve()

    if not directory.exists():

        raise FileNotFoundError(
            f"Documents directory not found: {directory}"
        )

    if not directory.is_dir():

        raise ValueError(
            f"Not a directory: {directory}"
        )

    all_documents = []

    supported_extensions = {
        ".ipynb",
        ".py",
        ".txt",
        ".pdf",
    }

    # --------------------------------------------------------
    # Process every file
    # --------------------------------------------------------

    for file_path in sorted(directory.iterdir()):

        # Ignore folders
        if not file_path.is_file():
            continue

        # Ignore unsupported files
        if file_path.suffix.lower() not in supported_extensions:
            continue

        print(
            f"\nLoading: {file_path.name}"
        )

        try:

            documents = load_document(
                str(file_path)
            )

            all_documents.extend(documents)

            print(
                f"  Loaded {len(documents)} document(s)"
            )

        except Exception as error:

            print(
                f"  ERROR loading "
                f"{file_path.name}: {error}"
            )

    return all_documents


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Current file:
    #
    # backend/
    #   rag/
    #     loaders/
    #       document_loader.py
    #
    # parents[0] = loaders
    # parents[1] = rag
    # parents[2] = backend

    backend_directory = (
        Path(__file__).resolve().parents[2]
    )

    documents_directory = (
        backend_directory
        / "rag"
        / "documents"
    )

    print("\n========================================")
    print("DSA Coach AI - Unified Document Loader")
    print("========================================")

    print(
        "\nDocuments directory:"
    )

    print(documents_directory)

    # Load all documents
    documents = load_all_documents(
        str(documents_directory)
    )

    print("\n========================================")
    print(
        f"TOTAL DOCUMENTS LOADED: "
        f"{len(documents)}"
    )
    print("========================================")

    # Display summary
    for index, document in enumerate(
        documents,
        start=1
    ):

        print("\n----------------------------------------")

        print(
            f"Document {index}"
        )

        print(
            "Source:",
            document.metadata.get("source")
        )

        print(
            "File type:",
            document.metadata.get("file_type")
        )

        print(
            "Content type:",
            document.metadata.get(
                "content_type",
                document.metadata.get(
                    "cell_type",
                    "text"
                )
            )
        )

        print(
            "Characters:",
            len(document.page_content)
        )

    print("\n========================================")
    print("Unified loader test completed!")
    print("========================================")