"""Hybrid RAG service — ChromaDB (vector) + BM25 (keyword) with Reciprocal Rank Fusion.

Indexes DSA knowledge documents at startup. Provides hybrid_search() for
retrieving relevant context to enrich LLM prompts.
"""
import os
import re
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi

# ─── Module-level state ────────────────────────────────────────────────
_chroma_client: Optional[chromadb.ClientAPI] = None
_collection: Optional[chromadb.Collection] = None
_bm25: Optional[BM25Okapi] = None
_chunk_texts: list[str] = []
_chunk_ids: list[str] = []
_chunk_sources: list[str] = []
_is_ready = False


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


def _tokenize(text: str) -> list[str]:
    """Simple tokenizer for BM25 — lowercase, alphanumeric tokens."""
    return re.findall(r'\w+', text.lower())


# ─── Index building ────────────────────────────────────────────────────

def build_index(knowledge_dir: Optional[str] = None) -> None:
    """Read all markdown files from the knowledge directory, chunk them,
    and build both ChromaDB (vector) and BM25 (keyword) indices.
    
    Called once at startup.
    """
    global _chroma_client, _collection, _bm25, _chunk_texts, _chunk_ids, _chunk_sources, _is_ready

    if knowledge_dir is None:
        knowledge_dir = str(Path(__file__).parent.parent / "data" / "knowledge")

    knowledge_path = Path(knowledge_dir)
    if not knowledge_path.exists():
        print(f"[RAG] Knowledge directory not found: {knowledge_path}")
        return

    # Collect all chunks from all documents
    all_chunks: list[str] = []
    all_ids: list[str] = []
    all_metadatas: list[dict] = []
    all_sources: list[str] = []

    for md_file in sorted(knowledge_path.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        doc_name = md_file.stem
        chunks = _chunk_document(text)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}_chunk_{i}"
            all_chunks.append(chunk)
            all_ids.append(chunk_id)
            all_metadatas.append({"source": doc_name, "chunk_index": i})
            all_sources.append(f"{doc_name}.md")
        
        print(f"  [RAG] Indexed {doc_name}.md -> {len(chunks)} chunks")

    if not all_chunks:
        print("[RAG] No knowledge documents found, RAG disabled.")
        return

    # ── ChromaDB (Vector Search) ──────────────────────────────────────
    # Use sentence-transformers for embeddings
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    persist_dir = str(Path(__file__).parent.parent / "data" / "chroma_db")
    _chroma_client = chromadb.Client()  # in-memory for speed
    
    # Delete existing collection if it exists (fresh rebuild each startup)
    try:
        _chroma_client.delete_collection("dsa_knowledge")
    except Exception:
        pass

    _collection = _chroma_client.create_collection(
        name="dsa_knowledge",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Add all chunks to ChromaDB
    _collection.add(
        documents=all_chunks,
        ids=all_ids,
        metadatas=all_metadatas,
    )

    # ── BM25 (Keyword Search) ────────────────────────────────────────
    tokenized_chunks = [_tokenize(chunk) for chunk in all_chunks]
    _bm25 = BM25Okapi(tokenized_chunks)
    _chunk_texts = all_chunks
    _chunk_ids = all_ids
    _chunk_sources = all_sources

    _is_ready = True
    print(f"[RAG] Hybrid index built: {len(all_chunks)} chunks from {len(list(knowledge_path.glob('*.md')))} documents")


# ─── Hybrid search ─────────────────────────────────────────────────────

def hybrid_search(query: str, top_k: int = 3) -> str:
    """Perform hybrid search: vector (ChromaDB) + keyword (BM25) with
    Reciprocal Rank Fusion to merge results.
    
    Returns a single string of concatenated relevant context chunks.
    """
    if not _is_ready or not _collection or not _bm25:
        return ""

    MAX_VECTOR_DISTANCE = 0.75
    MIN_BM25_SCORE = 0.0

    # ── Vector search (ChromaDB) ──────────────────────────────────────
    vector_results = _collection.query(
        query_texts=[query],
        n_results=min(top_k * 2, len(_chunk_texts)),  # fetch more for fusion
        include=["documents", "metadatas", "distances"]
    )
    
    vector_ids = []
    if vector_results["ids"] and vector_results["distances"]:
        for cid, dist in zip(vector_results["ids"][0], vector_results["distances"][0]):
            if dist <= MAX_VECTOR_DISTANCE:
                vector_ids.append(cid)

    # ── Keyword search (BM25) ─────────────────────────────────────────
    tokenized_query = _tokenize(query)
    bm25_scores = _bm25.get_scores(tokenized_query)
    
    # Get top indices sorted by BM25 score, keeping only score > MIN_BM25_SCORE
    bm25_top_indices = sorted(
        [i for i, score in enumerate(bm25_scores) if score > MIN_BM25_SCORE],
        key=lambda i: bm25_scores[i],
        reverse=True,
    )[:top_k * 2]
    bm25_ids = [_chunk_ids[i] for i in bm25_top_indices]

    # ── Reciprocal Rank Fusion (RRF) ──────────────────────────────────
    k = 60  # RRF constant (standard value)
    rrf_scores: dict[str, float] = {}

    for rank, chunk_id in enumerate(vector_ids):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (k + rank + 1)

    for rank, chunk_id in enumerate(bm25_ids):
        rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + 1.0 / (k + rank + 1)

    # Sort by fused score and take top_k
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]

    # Build the id→text and id→source lookups
    id_to_text = dict(zip(_chunk_ids, _chunk_texts))
    id_to_source = dict(zip(_chunk_ids, _chunk_sources))
    
    # Concatenate top chunks with source labels
    retrieved_chunks = []
    for cid in sorted_ids:
        if cid in id_to_text:
            source = id_to_source.get(cid, "unknown")
            retrieved_chunks.append(f"[Source: {source}]\n{id_to_text[cid]}")

    if not retrieved_chunks:
        return ""

    return "\n\n---\n\n".join(retrieved_chunks)


def is_ready() -> bool:
    """Check if the RAG index is built and ready."""
    return _is_ready
