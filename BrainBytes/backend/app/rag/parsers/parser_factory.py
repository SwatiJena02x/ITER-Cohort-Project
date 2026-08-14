from typing import Dict

from .json_parser import parse_json
from .pdf_parser import parse_pdf
from .text_parser import parse_text


def parse_document(document: Dict) -> Dict:
    """
    Select the appropriate parser based on document metadata.
    """
    metadata = document.get("metadata", {})
    file_type = metadata.get("file_type", "").lower()

    if file_type == "pdf":
        return parse_pdf(document)

    if file_type == "json":
        return parse_json(document)

    if file_type == "txt":
        return parse_text(document)

    raise ValueError(
        f"Unsupported document type: {file_type}"
    )