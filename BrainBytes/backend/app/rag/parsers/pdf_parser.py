from typing import Dict


def parse_pdf(document: Dict) -> Dict:
    """
    Parse extracted PDF text while preserving metadata.
    """
    text = document.get("text", "")

    return {
        "text": text.strip(),
        "metadata": document.get("metadata", {}),
        "pages": document.get("pages", []),
    }