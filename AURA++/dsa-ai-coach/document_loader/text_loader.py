from pathlib import Path

from .base_loader import BaseDocumentLoader
from .document import Document


class TextLoader(BaseDocumentLoader):
    """
    Loads plain text files.
    """

    def load(self, file_path: str) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() != ".txt":
            raise ValueError(
                f"Expected TXT file, got: {path.suffix}"
            )

        text = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        document = Document(
            text=text.strip(),
            metadata={
                "source": path.name,
                "file_path": str(path),
                "file_type": "txt"
            }
        )

        return [document]