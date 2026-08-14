from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    """
    Wrapper around the SentenceTransformer embedding model.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        """
        Generate embeddings for one or more texts.

        Args:
            texts: A string or list of strings.

        Returns:
            Embedding vector or list of embedding vectors.
        """
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

    @property
    def dimension(self) -> int:
        """
        Return the dimensionality of the embedding vectors.
        """
        return self.model.get_embedding_dimension()