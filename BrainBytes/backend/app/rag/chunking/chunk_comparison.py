from typing import Dict, List


def compare_chunks(
    fixed_chunks: List[str],
    recursive_chunks: List[str],
    sentence_window_chunks: List[str]
) -> Dict:
    """
    Compare outputs from different chunking strategies.

    Returns basic metrics that can be used to evaluate
    chunk count, average length, and total text coverage.
    """

    strategies = {
        "fixed": fixed_chunks,
        "recursive": recursive_chunks,
        "sentence_window": sentence_window_chunks,
    }

    comparison = {}

    for name, chunks in strategies.items():
        if not chunks:
            comparison[name] = {
                "chunk_count": 0,
                "average_length": 0,
                "total_characters": 0,
            }
            continue

        lengths = [len(chunk) for chunk in chunks]

        comparison[name] = {
            "chunk_count": len(chunks),
            "average_length": sum(lengths) / len(lengths),
            "total_characters": sum(lengths),
        }

    return comparison


def compare_chunk_documents(
    fixed_chunks: List[Dict],
    recursive_chunks: List[Dict],
    sentence_window_chunks: List[Dict]
) -> Dict:
    """
    Compare document-level chunk outputs.

    Each chunk is expected to contain:
        {
            "text": "...",
            "metadata": {...}
        }
    """

    fixed_text = [chunk.get("text", "") for chunk in fixed_chunks]
    recursive_text = [chunk.get("text", "") for chunk in recursive_chunks]
    sentence_window_text = [
        chunk.get("text", "") for chunk in sentence_window_chunks
    ]

    return compare_chunks(
        fixed_text,
        recursive_text,
        sentence_window_text
    )