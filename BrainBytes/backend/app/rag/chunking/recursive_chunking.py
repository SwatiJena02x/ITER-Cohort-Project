from typing import Dict, List


def recursive_chunk(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[str]:
    """
    Split text recursively using natural text boundaries.

    The function first tries paragraph boundaries, then line boundaries,
    then sentence boundaries, and finally falls back to fixed-size splitting.
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

    if len(text) <= chunk_size:
        return [text]

    separators = ["\n\n", "\n", ". ", " "]

    def split_text(content: str, separator_index: int) -> List[str]:
        if len(content) <= chunk_size:
            return [content.strip()]

        if separator_index >= len(separators):
            return _fixed_fallback(
                content,
                chunk_size,
                chunk_overlap,
            )

        separator = separators[separator_index]
        parts = content.split(separator)

        if len(parts) == 1:
            return split_text(content, separator_index + 1)

        chunks = []
        current = ""

        for part in parts:
            part = part.strip()

            if not part:
                continue

            candidate = (
                f"{current}{separator}{part}"
                if current
                else part
            )

            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.extend(
                        split_text(current, separator_index + 1)
                    )

                current = part

        if current:
            chunks.extend(
                split_text(current, separator_index + 1)
            )

        return chunks

    raw_chunks = split_text(text, 0)

    # Add overlap between neighboring chunks.
    if chunk_overlap == 0:
        return raw_chunks

    chunks = []

    for index, chunk in enumerate(raw_chunks):
        if index == 0:
            chunks.append(chunk)
            continue

        previous = raw_chunks[index - 1]
        overlap = previous[-chunk_overlap:]

        combined = f"{overlap} {chunk}".strip()
        chunks.append(combined)

    return chunks


def _fixed_fallback(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> List[str]:
    """Fallback to fixed-size splitting when no natural boundary exists."""

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


def recursive_chunk_document(
    document: Dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Dict]:
    """
    Chunk a parsed document using recursive splitting
    while preserving document metadata.
    """

    text = document.get("text", "")
    metadata = document.get("metadata", {})

    text_chunks = recursive_chunk(
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
                "chunking_strategy": "recursive",
            },
        }
        for index, chunk in enumerate(text_chunks)
    ]