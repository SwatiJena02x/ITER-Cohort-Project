"""Text embedding utilities backed by sentence-transformers."""

import logging
from typing import List, Optional

import numpy as np
from langsmith import traceable
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Lazily-loaded, process-wide singleton. Avoids paying the model-load cost
# at import time (e.g. when this module is imported just to reuse a helper,
# or during testing) and lets load failures surface where they're handled.
_embedder: Optional[SentenceTransformer] = None


def get_embedder(model_name: str = EMBEDDING_MODEL, device: Optional[str] = None) -> SentenceTransformer:
    """Return a cached SentenceTransformer instance, loading it on first use."""
    global _embedder
    if _embedder is None:
        logger.info("Loading embedding model: %s", model_name)
        _embedder = SentenceTransformer(model_name, device=device)
    return _embedder


@traceable(name="create_embeddings", run_type="embedding")
def create_embeddings(
    texts: List[str],
    batch_size: int = 32,
    show_progress_bar: bool = False,
) -> np.ndarray:
    """Encode a list of texts into normalized float32 embeddings.

    Args:
        texts: List of strings to embed.
        batch_size: Number of texts encoded per batch (controls memory use).
        show_progress_bar: Whether sentence-transformers should print progress.

    Returns:
        A (len(texts), embedding_dim) float32 numpy array of L2-normalized
        embeddings. Returns an empty array if `texts` is empty.
    """
    if not texts:
        return np.empty((0, 0), dtype="float32")

    embedder = get_embedder()

    embeddings = embedder.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=show_progress_bar,
    )

    return np.asarray(embeddings, dtype="float32")
