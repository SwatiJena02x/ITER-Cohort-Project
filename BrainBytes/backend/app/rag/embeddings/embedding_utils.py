from typing import List

import numpy as np


def validate_embedding(embedding) -> bool:
    """
    Validate that an embedding is a non-empty numeric 1D vector.
    """
    if embedding is None:
        return False

    array = np.asarray(embedding)

    if array.ndim != 1 or array.size == 0:
        return False

    if not np.issubdtype(array.dtype, np.number):
        return False

    return True


def normalize_embedding(embedding) -> np.ndarray:
    """
    Normalize an embedding vector to unit length.
    """
    array = np.asarray(embedding, dtype=np.float32)

    norm = np.linalg.norm(array)

    if norm == 0:
        raise ValueError("Cannot normalize a zero-vector.")

    return array / norm


def embedding_dimension(embedding) -> int:
    """
    Return the dimension of a single embedding vector.
    """
    array = np.asarray(embedding)

    if array.ndim != 1:
        raise ValueError("Expected a single 1-dimensional embedding.")

    return array.shape[0]


def embeddings_dimension(embeddings) -> int:
    """
    Return the dimension of a batch of embeddings.
    """
    array = np.asarray(embeddings)

    if array.ndim != 2:
        raise ValueError("Expected a 2-dimensional array of embeddings.")

    return array.shape[1]


def validate_embeddings(embeddings) -> bool:
    """
    Validate a batch of embeddings.
    """
    if embeddings is None:
        return False

    array = np.asarray(embeddings)

    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        return False

    if not np.issubdtype(array.dtype, np.number):
        return False

    return True