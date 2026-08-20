# ============================================================
# DSA Coach AI - Python File Loader
# ============================================================

import ast
from pathlib import Path

from langchain_core.documents import Document


def load_python_file(file_path: str) -> list[Document]:
    """
    Load a Python file and extract:
    - Complete source code
    - Comments
    - Docstrings
    """

    path = Path(file_path).resolve()

    # Check file exists
    if not path.exists():
        raise FileNotFoundError(
            f"Python file not found: {path}"
        )

    # Check extension
    if path.suffix.lower() != ".py":
        raise ValueError(
            f"Expected a .py file, got: {path.name}"
        )

    # Read Python source
    source_code = path.read_text(
        encoding="utf-8"
    )

    documents = []

    # --------------------------------------------------------
    # 1. Complete source code
    # --------------------------------------------------------

    if source_code.strip():

        documents.append(
            Document(
                page_content=source_code,
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "python",
                    "content_type": "code",
                },
            )
        )

    # --------------------------------------------------------
    # 2. Parse Python AST
    # --------------------------------------------------------

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(
            f"Warning: Could not parse {path.name}: {e}"
        )
        return documents

    # --------------------------------------------------------
    # 3. Extract docstrings
    # --------------------------------------------------------

    docstrings = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.Module,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):

            docstring = ast.get_docstring(node)

            if docstring:
                docstrings.append(docstring)

    if docstrings:

        documents.append(
            Document(
                page_content="\n\n".join(docstrings),
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "python",
                    "content_type": "docstring",
                },
            )
        )

    # --------------------------------------------------------
    # 4. Extract comments
    # --------------------------------------------------------

    comments = []

    try:

        import tokenize
        from io import StringIO

        tokens = tokenize.generate_tokens(
            StringIO(source_code).readline
        )

        for token in tokens:

            if token.type == tokenize.COMMENT:

                comment = token.string.strip()

                if comment:
                    comments.append(comment)

    except Exception as e:

        print(
            f"Warning: Could not extract comments "
            f"from {path.name}: {e}"
        )

    if comments:

        documents.append(
            Document(
                page_content="\n".join(comments),
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "python",
                    "content_type": "comment",
                },
            )
        )

    return documents


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Find backend directory automatically
    backend_dir = Path(__file__).resolve().parents[2]

    # Python file inside rag/documents
    python_file = (
        backend_dir
        / "rag"
        / "documents"
        / "example.py"
    )

    print("\n========================================")
    print("DSA Coach AI - Python Loader Test")
    print("========================================")

    print("\nPython file:")
    print(python_file)

    # Check file
    if not python_file.exists():

        print("\nERROR:")
        print("example.py was not found.")

        print("\nExpected location:")
        print(python_file)

        raise SystemExit(1)

    # Load file
    docs = load_python_file(
        str(python_file)
    )

    print(
        f"\nSuccessfully extracted "
        f"{len(docs)} documents."
    )

    # Display extracted documents
    for index, doc in enumerate(
        docs,
        start=1
    ):

        print("\n----------------------------------------")
        print(f"Document {index}")
        print("----------------------------------------")

        print(
            "Content type:",
            doc.metadata.get("content_type")
        )

        print(
            "Source:",
            doc.metadata.get("source")
        )

        print("\nContent:")

        print(
            doc.page_content[:1000]
        )

    print("\n========================================")
    print("Python loader test completed!")
    print("========================================")