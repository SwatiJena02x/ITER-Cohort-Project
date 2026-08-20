import json
from pathlib import Path


def load_json(path: Path) -> dict:
    """
    Load a JSON document.
    """
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return {
        "text": json.dumps(data, ensure_ascii=False, indent=2),
        "metadata": {
            "source": str(path),
            "file_name": path.name,
            "file_type": "json",
        },
    }