from typing import Any, List, Optional

import chromadb


class ChromaStore:
    """
    ChromaDB-backed vector store for RAG documents.
    """

    def __init__(
        self,
        collection_name: str = "fatigue_documents",
        persist_directory: str = "data/chroma",
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            configuration={
                "hnsw": {
                    "space": "cosine",
                }
            },
        )

    def add(
        self,
        ids: List[str],
        embeddings: List[Any],
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> None:
        """
        Add documents and their embeddings to ChromaDB.
        """
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: Any,
        top_k: int = 5,
    ) -> dict:
        """
        Search for the most similar documents.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

    def count(self) -> int:
        """
        Return the number of stored documents.
        """
        return self.collection.count()