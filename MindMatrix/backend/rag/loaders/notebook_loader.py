# ============================================================
# DSA Coach AI - Jupyter Notebook Loader
# ============================================================
# Purpose:
#   Load .ipynb files and extract Markdown and Code cells
#   separately as LangChain Document objects.
#
# Task 1:
#   Document Loading
#
# Supported:
#   - Markdown cells
#   - Code cells
#   - Notebook metadata
#   - Cell numbers
# ============================================================

import json
from pathlib import Path

from langchain_core.documents import Document


def load_notebook(file_path: str) -> list[Document]:
    """
    Load a Jupyter Notebook (.ipynb) file.

    Each Markdown and Code cell is converted into
    a separate LangChain Document.

    Args:
        file_path: Path to the notebook.

    Returns:
        List of LangChain Document objects.
    """

    # Convert the supplied path into a Path object
    path = Path(file_path)

    # Convert relative paths into absolute paths
    path = path.resolve()

    # Check whether the notebook exists
    if not path.exists():
        raise FileNotFoundError(
            f"Notebook not found: {path}"
        )

    # Check that the file is actually a notebook
    if path.suffix.lower() != ".ipynb":
        raise ValueError(
            f"Expected a .ipynb file, but received: {path.name}"
        )

    # Open the notebook as UTF-8 JSON
    with open(path, "r", encoding="utf-8") as file:
        notebook = json.load(file)

    # Store extracted LangChain documents
    documents = []

    # Get all notebook cells
    cells = notebook.get("cells", [])

    # Process each notebook cell
    for cell_number, cell in enumerate(cells):

        # Get the cell type
        cell_type = cell.get("cell_type", "")

        # Get the source content
        source = cell.get("source", [])

        # source can be either a list or a string
        if isinstance(source, list):
            content = "".join(source).strip()
        else:
            content = str(source).strip()

        # Ignore empty cells
        if not content:
            continue

        # ----------------------------------------------------
        # Markdown cell
        # ----------------------------------------------------
        if cell_type == "markdown":

            document = Document(
                page_content=content,
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "ipynb",
                    "cell_type": "markdown",
                    "cell_number": cell_number,
                },
            )

            documents.append(document)

        # ----------------------------------------------------
        # Code cell
        # ----------------------------------------------------
        elif cell_type == "code":

            document = Document(
                page_content=content,
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "ipynb",
                    "cell_type": "code",
                    "cell_number": cell_number,
                },
            )

            documents.append(document)

        # ----------------------------------------------------
        # Ignore unknown cell types
        # ----------------------------------------------------
        else:
            continue

    # Return all extracted documents
    return documents


# ============================================================
# TEST THE NOTEBOOK LOADER
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Find the backend directory automatically
    #
    # Current file:
    # backend/rag/loaders/notebook_loader.py
    #
    # parents[0] = loaders
    # parents[1] = rag
    # parents[2] = backend
    # --------------------------------------------------------

    backend_dir = Path(__file__).resolve().parents[2]

    # Build the correct notebook path
    notebook_path = (
        backend_dir
        / "rag"
        / "documents"
        / "algorithms.ipynb"
    )

    print("\n========================================")
    print("DSA Coach AI - Notebook Loader Test")
    print("========================================")

    print(f"\nNotebook path:")
    print(notebook_path)

    # Check the file before loading
    if not notebook_path.exists():

        print("\nERROR:")
        print("algorithms.ipynb was not found.")

        print("\nExpected location:")
        print(notebook_path)

        print("\nPlease make sure the file exists here:")
        print("backend/rag/documents/algorithms.ipynb")

        raise SystemExit(1)

    # Load the notebook
    docs = load_notebook(str(notebook_path))

    # Display number of extracted cells
    print(f"\nSuccessfully loaded {len(docs)} cells.")

    # Display every extracted document
    for index, doc in enumerate(docs, start=1):

        print("\n----------------------------------------")
        print(f"Document {index}")
        print("----------------------------------------")

        print(
            "Cell type:",
            doc.metadata.get("cell_type")
        )

        print(
            "Cell number:",
            doc.metadata.get("cell_number")
        )

        print(
            "Source:",
            doc.metadata.get("source")
        )

        print("\nContent:")
        print(doc.page_content[:500])

    print("\n========================================")
    print("Notebook loader test completed!")
    print("========================================")