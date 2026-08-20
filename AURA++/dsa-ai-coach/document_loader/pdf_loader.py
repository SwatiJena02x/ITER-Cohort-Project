from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import EmptyFileError

from .base_loader import BaseDocumentLoader
from .document import Document


class PDFLoader(BaseDocumentLoader):
    """
    Loads PDF files page by page.
    """

    def load(self, file_path: str) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Expected PDF file, got: {path.suffix}"
            )

        # Check for empty file
        if path.stat().st_size == 0:
            print(
                f"⚠ Skipping empty PDF: {path.name}"
            )
            return []

        try:
            reader = PdfReader(str(path))

        except EmptyFileError:
            print(
                f"⚠ Skipping empty PDF: {path.name}"
            )
            return []

        except Exception as error:
            print(
                f"⚠ Could not read PDF "
                f"{path.name}: {error}"
            )
            return []

        documents = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = page.extract_text() or ""

            if not text.strip():
                continue

            document = Document(
                text=text.strip(),
                metadata={
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "pdf",
                    "page": page_number
                }
            )

            documents.append(document)

        return documents