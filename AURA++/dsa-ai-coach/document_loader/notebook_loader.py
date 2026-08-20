import json
from pathlib import Path

from .base_loader import BaseDocumentLoader
from .document import Document


class NotebookLoader(BaseDocumentLoader):
    """
    Loads Jupyter Notebook files.

    Markdown and code cells are preserved and labeled
    separately.
    """

    def load(self, file_path: str) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() != ".ipynb":
            raise ValueError(
                f"Expected IPYNB file, got: {path.suffix}"
            )

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            notebook = json.load(file)

        sections = []

        for index, cell in enumerate(
            notebook.get("cells", [])
        ):

            cell_type = cell.get(
                "cell_type",
                "unknown"
            )

            source = "".join(
                cell.get("source", [])
            ).strip()

            if not source:
                continue

            if cell_type == "markdown":

                sections.append(
                    f"[MARKDOWN CELL {index}]\n"
                    f"{source}"
                )

            elif cell_type == "code":

                sections.append(
                    f"[CODE CELL {index}]\n"
                    f"```python\n"
                    f"{source}\n"
                    f"```"
                )

        full_text = "\n\n".join(sections)

        document = Document(
            text=full_text,
            metadata={
                "source": path.name,
                "file_path": str(path),
                "file_type": "ipynb",
                "language": "python"
            }
        )

        return [document]