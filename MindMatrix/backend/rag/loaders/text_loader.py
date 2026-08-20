from pathlib import Path

from langchain_core.documents import Document


def load_text_file(file_path: str) -> list[Document]:

    path = Path(file_path).resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Text file not found: {path}"
        )

    text = path.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": path.name,
                "file_path": str(path),
                "file_type": "txt",
                "content_type": "text",
            },
        )
    ]