from pathlib import Path

from .document import Document
from .loader_factory import DocumentLoaderFactory


class DocumentLoader:
    """
    High-level document loading service.
    """

    def load_file(
        self,
        file_path: str
    ) -> list[Document]:

        loader = DocumentLoaderFactory.get_loader(
            file_path
        )

        return loader.load(file_path)

    def load_directory(
        self,
        directory: str
    ) -> list[Document]:

        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )

        documents = []

        for file_path in path.rglob("*"):

            if not file_path.is_file():
                continue

            try:

                loaded_documents = self.load_file(
                    str(file_path)
                )

                documents.extend(
                    loaded_documents
                )

                print(
                    f"✓ Loaded: {file_path.name}"
                )

            except ValueError:

                # Ignore unsupported file types.
                continue

        return documents