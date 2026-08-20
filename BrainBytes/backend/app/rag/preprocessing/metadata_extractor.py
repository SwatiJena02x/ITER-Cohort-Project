from pathlib import Path
from typing import Any, Dict


def extract_metadata(
    source: str,
    file_type: str | None = None
) -> Dict[str, Any]:
    """
    Extract basic metadata from a document source.
    """

    path = Path(source)

    if file_type is None:
        file_type = path.suffix.lower().lstrip(".")

    return {
        "source": str(source),
        "file_name": path.name,
        "file_type": file_type.lower(),
    }