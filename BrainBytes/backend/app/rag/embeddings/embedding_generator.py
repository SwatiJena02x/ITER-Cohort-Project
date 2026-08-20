from typing import List, Union

from .embedding_model import EmbeddingModel


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using the configured embedding model.
    """

    def __init__(self, model: EmbeddingModel | None = None):
        self.model = model or EmbeddingModel()

    def generate(
        self,
        texts: Union[str, List[str]],
    ):
        """
        Generate embeddings for one or more texts.

        Args:
            texts: A single text string or a list of text strings.

        Returns:
            NumPy array containing the generated embedding(s).
        """
        if isinstance(texts, str):
            if not texts.strip():
                raise ValueError("Text cannot be empty.")
        elif isinstance(texts, list):
            if not texts:
                raise ValueError("Text list cannot be empty.")

            if any(not isinstance(text, str) or not text.strip() for text in texts):
                raise ValueError("All texts must be non-empty strings.")
        else:
            raise TypeError("texts must be a string or a list of strings.")

        return self.model.encode(texts)

    def generate_for_chunks(self, chunks: List[str]):
        """
        Generate embeddings for document chunks.

        Args:
            chunks: List of text chunks.

        Returns:
            NumPy array containing one embedding per chunk.
        """
        return self.generate(chunks)

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self.model.dimension