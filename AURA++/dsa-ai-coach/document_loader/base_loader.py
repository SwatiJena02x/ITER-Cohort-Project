from abc import ABC, abstractmethod

from .document import Document


class BaseDocumentLoader(ABC):
    """
    Abstract base class for all document loaders.
    """

    @abstractmethod
    def load(self, file_path: str) -> list[Document]:
        """
        Load a document and return standardized Document objects.
        """
        pass