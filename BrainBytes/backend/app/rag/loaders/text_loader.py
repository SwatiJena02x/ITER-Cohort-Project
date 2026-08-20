from pathlib import Path


def load_text(path: Path) -> dict:
    """
    Load a plain text document.
    """
    text = path.read_text(encoding="utf-8")

    return {
        "text": text,
        "metadata": {
            "source": str(path),
            "file_name": path.name,
            "file_type": "txt",
        },
    }