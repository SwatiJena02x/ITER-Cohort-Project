import re
from typing import Dict, List


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences while preserving sentence content."""
    if not text or not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def sentence_window_chunk(
    text: str,
    window_size: int = 2
) -> List[str]:
    """
    Create sentence-window chunks.

    Each chunk contains the current sentence plus surrounding
    sentences according to the configured window size.

    Args:
        text: Input text.
        window_size: Number of surrounding sentences on each side.

    Returns:
        List of sentence-window chunks.
    """
    if not text or not text.strip():
        return []

    if window_size < 0:
        raise ValueError("window_size must be >= 0")

    sentences = _split_sentences(text)

    chunks = []

    for i in range(len(sentences)):
        start = max(0, i - window_size)
        end = min(len(sentences), i + window_size + 1)

        chunk = " ".join(sentences[start:end])
        chunks.append(chunk)

    return chunks


def sentence_window_chunk_document(
    document: Dict,
    window_size: int = 2
) -> List[Dict]:
    """
    Apply sentence-window chunking to a parsed document.

    Preserves the document metadata and adds chunk information.
    """
    if not isinstance(document, dict):
        raise TypeError("document must be a dictionary")

    text = document.get("text", "")
    metadata = document.get("metadata", {}).copy()

    chunks = sentence_window_chunk(
        text=text,
        window_size=window_size
    )

    result = []

    for i, chunk in enumerate(chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            "chunk_id": i,
            "chunking_strategy": "sentence_window",
            "window_size": window_size
        })

        result.append({
            "text": chunk,
            "metadata": chunk_metadata
        })

    return result