from pathlib import Path

from .base_loader import BaseDocumentLoader
from .document import Document


class PythonLoader(BaseDocumentLoader):
    """
    Loads Python source files.
    """

    def load(self, file_path: str) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() != ".py":
            raise ValueError(
                f"Expected Python file, got: {path.suffix}"
            )

        code = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        document = Document(
            text=code.strip(),
            metadata={
                "source": path.name,
                "file_path": str(path),
                "file_type": "python",
                "language": "python"
            }
        )

        return [document]