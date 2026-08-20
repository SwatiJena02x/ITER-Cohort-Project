from dataclasses import dataclass, field
from typing import Any

@dataclass
class Document:
    """
    Represents a standardized document used by the DSA AI Coach.
    """

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        source = self.metadata.get("source", "unknown")

        return (
            f"Document("
            f"source='{source}', "
            f"characters={len(self.text)}"
            f")"
        )