"""Utilities for splitting text into overlapping word-based chunks."""

from typing import List


def chunk_text(text: str, chunk_size: int = 80, overlap: int = 20) -> List[str]:
    """Split text into overlapping chunks of whitespace-delimited words.

    Args:
        text: The input text to chunk.
        chunk_size: Number of words per chunk.
        overlap: Number of words shared between consecutive chunks.

    Returns:
        A list of chunk strings. Empty if `text` has no words.

    Raises:
        ValueError: If chunk_size <= 0, overlap < 0, or overlap >= chunk_size
            (which would otherwise stall or reverse progress through the text).
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got {overlap}")
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size}) "
            "or chunking will never advance"
        )

    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks = []

    for start in range(0, len(words), step):
        chunk = " ".join(words[start:start + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
        # Once a chunk reaches the end of the text, further starts are redundant.
        if start + chunk_size >= len(words):
            break

    return chunks
