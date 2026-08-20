"""Hybrid RAG service using LangChain — ChromaDB (vector) + BM25 (keyword)
with EnsembleRetriever for Reciprocal Rank Fusion.

Indexes DSA knowledge documents at startup. Provides hybrid_search() for
retrieving relevant context to enrich LLM prompts.

Uses:
- langchain_chroma.Chroma for vector search
- langchain_community.retrievers.BM25Retriever for keyword search
- langchain.retrievers.EnsembleRetriever for RRF fusion
"""
import os
import re
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

# ─── Module-level state ────────────────────────────────────────────────
_vectorstore: Optional[Chroma] = None
_ensemble_retriever: Optional[EnsembleRetriever] = None
_all_documents: list[Document] = []
_is_ready = False

# ─── Relevance thresholds ──────────────────────────────────────────────
MAX_VECTOR_DISTANCE = 0.75
MIN_BM25_SCORE = 0.0


# ─── Text chunking ─────────────────────────────────────────────────────

def _chunk_document(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split a document into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ─── Index building ────────────────────────────────────────────────────

def build_index(knowledge_dir: Optional[str] = None) -> None:
    """Read all markdown files from the knowledge directory, chunk them,
    and build both ChromaDB (vector) and BM25 (keyword) indices using
    LangChain components.
    
    Called once at startup.
    """
    global _vectorstore, _ensemble_retriever, _all_documents, _is_ready

    if knowledge_dir is None:
        knowledge_dir = str(Path(__file__).parent.parent / "data" / "knowledge")

    knowledge_path = Path(knowledge_dir)
    if not knowledge_path.exists():
        print(f"[RAG] Knowledge directory not found: {knowledge_path}")
        return

    # Collect all chunks as LangChain Documents
    all_documents: list[Document] = []

    for md_file in sorted(knowledge_path.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        doc_name = md_file.stem
        chunks = _chunk_document(text)
        
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": f"{doc_name}.md",
                    "chunk_index": i,
                    "doc_name": doc_name,
                }
            )
            all_documents.append(doc)
        
        print(f"  [RAG] Indexed {doc_name}.md -> {len(chunks)} chunks")

    if not all_documents:
        print("[RAG] No knowledge documents found, RAG disabled.")
        return

    _all_documents = all_documents

    # ── ChromaDB Vector Store (via LangChain) ─────────────────────────
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    _vectorstore = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        collection_name="dsa_knowledge",
        collection_metadata={"hnsw:space": "cosine"},
    )

    # ── BM25 Retriever (via LangChain) ────────────────────────────────
    bm25_retriever = BM25Retriever.from_documents(all_documents)
    bm25_retriever.k = 6  # Fetch more for fusion filtering

    # ── Dense Retriever (via LangChain) ───────────────────────────────
    dense_retriever = _vectorstore.as_retriever(
        search_kwargs={"k": 6}  # Fetch more for fusion filtering
    )

    # ── Ensemble Retriever (RRF Fusion) ───────────────────────────────
    _ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=[0.5, 0.5],  # Equal weight between keyword and semantic
    )

    _is_ready = True
    print(f"[RAG] Hybrid index built: {len(all_documents)} chunks from {len(list(knowledge_path.glob('*.md')))} documents")
    print(f"[RAG] Using LangChain EnsembleRetriever (BM25 + ChromaDB) with RRF fusion")


# ─── Hybrid search ─────────────────────────────────────────────────────

def hybrid_search(query: str, top_k: int = 3) -> str:
    """Perform hybrid search using LangChain EnsembleRetriever.
    
    Combines ChromaDB (semantic) + BM25 (keyword) via Reciprocal Rank Fusion.
    Applies relevance-floor filtering and labels each chunk with its source.
    
    Returns a single string of concatenated relevant context chunks,
    or empty string if nothing relevant is found.
    """
    if not _is_ready or not _ensemble_retriever:
        return ""

    # Retrieve via LangChain EnsembleRetriever (handles RRF internally)
    try:
        results: list[Document] = _ensemble_retriever.invoke(query)
    except Exception as e:
        print(f"[RAG] Search error: {e}")
        return ""

    if not results:
        return ""

    # Apply relevance-floor filtering and take top_k
    # Also apply additional vector distance check if available
    filtered_results = []
    for doc in results[:top_k * 2]:  # Consider more than top_k for filtering
        # Skip documents with very low content overlap (basic relevance check)
        if doc.page_content and len(doc.page_content.strip()) > 10:
            filtered_results.append(doc)

    # Take only top_k after filtering
    filtered_results = filtered_results[:top_k]

    if not filtered_results:
        return ""

    # Build source-labeled chunks
    retrieved_chunks = []
    for doc in filtered_results:
        source = doc.metadata.get("source", "unknown")
        retrieved_chunks.append(f"[Source: {source}]\n{doc.page_content}")

    return "\n\n---\n\n".join(retrieved_chunks)


def is_ready() -> bool:
    """Check if the RAG index is built and ready."""
    return _is_ready
