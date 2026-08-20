from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """
    Represents a chunk created from a document.
    """

    chunk_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return (
            f"Chunk("
            f"id='{self.chunk_id}', "
            f"characters={len(self.text)}"
            f")"
        )