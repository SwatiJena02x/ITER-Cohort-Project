from pathlib import Path

from .base_loader import BaseDocumentLoader
from .pdf_loader import PDFLoader
from .text_loader import TextLoader
from .python_loader import PythonLoader
from .notebook_loader import NotebookLoader


class DocumentLoaderFactory:
    """
    Factory responsible for creating the correct
    document loader based on file extension.
    """

    _loaders = {
        ".pdf": PDFLoader,
        ".txt": TextLoader,
        ".py": PythonLoader,
        ".ipynb": NotebookLoader
    }

    @classmethod
    def get_loader(
        cls,
        file_path: str
    ) -> BaseDocumentLoader:

        extension = Path(
            file_path
        ).suffix.lower()

        loader_class = cls._loaders.get(
            extension
        )

        if loader_class is None:

            supported = ", ".join(
                cls._loaders.keys()
            )

            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {supported}"
            )

        return loader_class()