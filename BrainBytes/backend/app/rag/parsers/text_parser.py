from typing import Dict


def parse_text(document: Dict) -> Dict:
    """
    Parse a text document into normalized text and metadata.
    """
    text = document.get("text", "")

    return {
        "text": text.strip(),
        "metadata": document.get("metadata", {}),
    }