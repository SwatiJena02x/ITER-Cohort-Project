from pathlib import Path

import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings

from langchain_ollama import OllamaEmbeddings

from app.core.config import settings


CHROMA_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / settings.CHROMA_PERSIST_DIRECTORY
)


class NomicEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

    def __call__(self, input: Documents) -> Embeddings:
        return self.embeddings.embed_documents(input)


embedding_function = NomicEmbeddingFunction()


client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


collection = client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    embedding_function=embedding_function,
)