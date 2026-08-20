from __future__ import annotations

from typing import Any, Dict, List, Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .embeddings import LocalChromaEmbeddings


class VectorEvidenceStore:
    def __init__(self, persist_directory: str = "./vector_store", collection_name: str = "exam_evidence"):
        self.persist_directory = persist_directory
        self.embeddings = LocalChromaEmbeddings()
        self.store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name,
        )

    def add_documents(self, documents: Sequence[Document]) -> None:
        if not documents:
            return
        values = list(documents)
        ids = [str(document.metadata.get("chunk_id") or document.metadata.get("evidence_id")) for document in values]
        self.store.add_documents(values, ids=ids)

    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        results = self.store.similarity_search_with_score(query, k=k)
        return [
            {
                "page_content": item.page_content,
                "metadata": item.metadata,
                "distance": float(score),
                "similarity": float(1.0 / (1.0 + score)),
            }
            for item, score in results
        ]
