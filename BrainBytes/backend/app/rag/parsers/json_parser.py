import json
from typing import Dict


def parse_json(document: Dict) -> Dict:
    """
    Parse JSON content into searchable text.
    """
    text = document.get("text", "")

    try:
        data = json.loads(text)
        normalized_text = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
    except json.JSONDecodeError:
        normalized_text = text

    return {
        "text": normalized_text.strip(),
        "metadata": document.get("metadata", {}),
    }