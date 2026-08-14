from pathlib import Path
from typing import List, Dict


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".json"}


def discover_documents(directory: str) -> List[Path]:
    """
    Discover supported documents recursively.
    """
    root = Path(directory)

    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    documents = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    return sorted(documents)


def load_document(path: str) -> Dict:
    """
    Load a single document using the appropriate loader.
    """
    file_path = Path(path)
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        from .pdf_loader import load_pdf
        return load_pdf(file_path)

    if extension == ".txt":
        from .text_loader import load_text
        return load_text(file_path)

    if extension == ".json":
        from .json_loader import load_json
        return load_json(file_path)

    raise ValueError(f"Unsupported file type: {extension}")


def load_documents(directory: str) -> List[Dict]:
    """
    Discover and load all supported documents.
    """
    documents = discover_documents(directory)

    return [load_document(str(path)) for path in documents]