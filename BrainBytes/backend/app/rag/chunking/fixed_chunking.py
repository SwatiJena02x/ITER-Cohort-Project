from typing import Dict, List


def fixed_chunk(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[str]:
    """
    Split text into fixed-size chunks with optional overlap.

    Args:
        text: Input text.
        chunk_size: Maximum number of characters in each chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    chunks = []

    start = 0
    step = chunk_size - chunk_overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def fixed_chunk_document(
    document: Dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Dict]:
    """
    Chunk a parsed document while preserving its metadata.
    """
    text = document.get("text", "")
    metadata = document.get("metadata", {})

    text_chunks = fixed_chunk(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return [
        {
            "text": chunk,
            "metadata": {
                **metadata,
                "chunk_id": index,
                "chunking_strategy": "fixed",
            },
        }
        for index, chunk in enumerate(text_chunks)
    ]