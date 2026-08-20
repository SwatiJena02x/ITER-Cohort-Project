from typing import Any, Dict

from .text_cleaner import clean_text
from .metadata_extractor import extract_metadata


def preprocess_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean document text and enrich its metadata.
    """

    if not isinstance(document, dict):
        raise TypeError("document must be a dictionary")

    if "text" not in document:
        raise ValueError("document must contain a 'text' field")

    text = clean_text(document["text"])

    metadata = dict(document.get("metadata", {}))

    source = metadata.get("source")

    if source:
        extracted_metadata = extract_metadata(
            source=source,
            file_type=metadata.get("file_type")
        )

        # Preserve existing metadata while adding extracted metadata.
        extracted_metadata.update(metadata)
        metadata = extracted_metadata

    return {
        "text": text,
        "metadata": metadata,
    }