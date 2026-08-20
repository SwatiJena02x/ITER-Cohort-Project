"""FAISS-backed similarity index for retrieving relevant text chunks."""

from typing import Dict, List

import numpy as np
import faiss


def create_index(embeddings: np.ndarray) -> faiss.Index:
    """Build a flat inner-product FAISS index from embeddings.

    Assumes embeddings are already L2-normalized (so inner product ==
    cosine similarity), matching `embeddings.create_embeddings`.

    Raises:
        ValueError: If `embeddings` is empty or not 2-dimensional.
    """
    if embeddings.ndim != 2:
        raise ValueError(f"embeddings must be 2D, got shape {embeddings.shape}")
    if embeddings.shape[0] == 0:
        raise ValueError("Cannot build an index from zero embeddings")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index


def save_index(index: faiss.Index, path: str) -> None:
    """Persist a FAISS index to disk."""
    faiss.write_index(index, path)


def load_index(path: str) -> faiss.Index:
    """Load a FAISS index previously saved with `save_index`."""
    return faiss.read_index(path)


def retrieve_rules(
    index: faiss.Index,
    rule_chunks: List[str],
    query_embedding: np.ndarray,
    top_k: int = 5,
) -> List[Dict]:
    """Retrieve the top-k chunks most similar to a query embedding.

    Args:
        index: A FAISS index built by `create_index`.
        rule_chunks: The text chunks corresponding to each index entry,
            in the same order used to build the index.
        query_embedding: A (1, dim) or (dim,) array for a single query.
        top_k: Maximum number of results to return.

    Returns:
        A list of dicts with "chunk_id", "text", and "score", ordered by
        descending similarity. Empty if the index has no entries.

    Raises:
        ValueError: If the query dimension doesn't match the index, or if
            `rule_chunks` doesn't match the number of vectors in the index.
    """
    if index.ntotal == 0:
        return []

    if index.ntotal != len(rule_chunks):
        raise ValueError(
            f"Index has {index.ntotal} vectors but rule_chunks has "
            f"{len(rule_chunks)} entries; they must correspond 1:1"
        )

    query_embedding = np.asarray(query_embedding, dtype="float32")
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.shape[1] != index.d:
        raise ValueError(
            f"Query embedding dim {query_embedding.shape[1]} does not match "
            f"index dim {index.d}"
        )

    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_embedding, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        if idx == -1:  # FAISS pads with -1 if fewer than k results exist
            continue
        results.append(
            {
                "chunk_id": int(idx),
                "text": rule_chunks[idx],
                "score": float(distances[0][rank]),
            }
        )

    return results
