from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Creates embeddings for documents and queries.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.model_name = model_name

        print(
            f"Loading embedding model: {model_name}"
        )

        self.model = SentenceTransformer(
            model_name
        )

        print("Embedding model loaded.")

    def embed_text(self, text: str) -> list[float]:

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def embed_query(
        self,
        query: str
    ) -> list[float]:

        return self.embed_text(query)